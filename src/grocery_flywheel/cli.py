from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .contracts import SCHEMA_VERSION, is_iso_date, validate_canonical_state
from .core import analyze_state
from .corrections import record_correction
from .importers import import_csv_history, import_normalized_history
from .privacy import CORRECTION_TELEMETRY_VALUES
from .render import render_dashboard
from .retailer_adapter import (
    capability_matrix,
    create_retailer_profile,
    format_capability_table,
    validate_retailer_profile,
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_profiles(path: Path) -> list[dict[str, Any]]:
    payload = read_json(path)
    if not isinstance(payload, list):
        raise ValueError("retailer profile file must contain a JSON list")
    if not payload:
        raise ValueError("retailer profile file must contain at least one profile")
    if not all(isinstance(profile, dict) for profile in payload):
        raise ValueError("retailer profile file must contain JSON objects")
    return payload


def split_csv(value: str | None) -> list[str]:
    return [part.strip() for part in (value or "").split(",") if part.strip()]


def cmd_adapters_validate(args: argparse.Namespace) -> int:
    profiles = load_profiles(args.path)
    errors = []
    for profile in profiles:
        for error in validate_retailer_profile(profile):
            errors.append(f"{profile.get('id', '<unknown>')}: {error}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"valid adapter profiles: {len(profiles)}")
    return 0


def cmd_adapters_inspect(args: argparse.Namespace) -> int:
    profiles = load_profiles(args.path)
    errors = profile_validation_errors(profiles)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    rows = capability_matrix(profiles)
    if args.format == "json":
        print(json.dumps(rows, indent=2, sort_keys=True))
    else:
        print(format_capability_table(rows))
    return 0


def cmd_adapters_create(args: argparse.Namespace) -> int:
    acquisition_methods = split_csv(args.acquisition_methods)
    if not acquisition_methods:
        print("adapters create requires explicit --acquisition-methods", file=sys.stderr)
        return 2
    profile = create_retailer_profile(
        name=args.name,
        type_=args.type,
        channels=split_csv(args.channels),
        acquisition_methods=acquisition_methods,
        capabilities=split_csv(args.capabilities),
        region=args.region,
    )
    write_json(args.output, [profile])
    print(f"wrote {args.output}")
    return 0


def profile_validation_errors(profiles: list[dict[str, Any]]) -> list[str]:
    errors = []
    for profile in profiles:
        profile_id = profile.get("id", "<unknown>")
        for error in validate_retailer_profile(profile):
            errors.append(f"{profile_id}: {error}")
    return errors


def attach_profiles(state: dict[str, Any], profiles_path: Path | None) -> dict[str, Any]:
    if not profiles_path:
        return state
    profiles = load_profiles(profiles_path)
    errors = profile_validation_errors(profiles)
    if errors:
        raise ValueError("invalid retailer profile(s): " + "; ".join(errors))
    state["adapter_matrix"] = capability_matrix(profiles)
    if not state.get("retailer_profiles"):
        state["retailer_profiles"] = [profiles[0]["id"]]
    return state


def assert_state_contract_clean(state: dict[str, Any]) -> None:
    errors = validate_canonical_state(state)
    if errors:
        raise ValueError("canonical state failed contract validation: " + "; ".join(errors))


def assert_analysis_contract_clean(analysis: Any) -> None:
    analysis_errors = validate_analysis_contract(analysis)
    if analysis_errors:
        raise ValueError("analysis failed contract validation: " + "; ".join(analysis_errors))
    errors = analysis.get("contract_errors", [])
    if errors:
        raise ValueError("canonical state failed contract validation: " + "; ".join(errors))


def validate_analysis_contract(analysis: Any) -> list[str]:
    if not isinstance(analysis, dict):
        return ["analysis must be an object"]
    errors: list[str] = []
    for field in (
        "schema_version",
        "order",
        "as_of",
        "items",
        "role_summary",
        "sourcing_research",
        "dietary_profiles",
        "substitutions",
        "pulses",
        "estimated_days_remaining",
        "known_consumed_fraction",
        "days_elapsed",
        "consumed_value",
        "contract_errors",
    ):
        if field not in analysis:
            errors.append(f"analysis missing {field}")
    if analysis.get("schema_version") != SCHEMA_VERSION:
        errors.append("analysis schema_version is missing or unsupported")
    if "contract_errors" in analysis and not isinstance(analysis["contract_errors"], list):
        errors.append("analysis contract_errors must be a list")
    elif "contract_errors" in analysis:
        for index, error in enumerate(analysis["contract_errors"]):
            if not isinstance(error, str):
                errors.append(f"analysis contract_errors[{index}] must be a string")
    order = analysis.get("order")
    if order is not None and not isinstance(order, dict):
        errors.append("analysis order must be an object")
    elif isinstance(order, dict):
        for field in ("store", "date", "total"):
            if field not in order:
                errors.append(f"analysis order missing {field}")
        for field in ("store", "date"):
            if field in order and not isinstance(order[field], str):
                errors.append(f"analysis order.{field} must be a string")
        if "date" in order and isinstance(order["date"], str):
            if not is_iso_date(order["date"]):
                errors.append("analysis order.date must be an ISO date")
        if "total" in order and not is_number(order["total"]):
            errors.append("analysis order.total must be numeric")
    for field in (
        "items",
        "role_summary",
        "sourcing_research",
        "dietary_profiles",
        "dietary_evaluations",
        "substitutions",
        "pulses",
        "adapter_matrix",
    ):
        if field in analysis and not isinstance(analysis[field], list):
            errors.append(f"analysis {field} must be a list")
    for field in ("privacy", "cart_plan", "run_sheet", "first_wow", "inventory_surface"):
        if field in analysis and analysis[field] is not None and not isinstance(analysis[field], dict):
            errors.append(f"analysis {field} must be an object")
    for field in ("known_consumed_fraction", "days_elapsed", "consumed_value"):
        if field in analysis and not is_number(analysis[field]):
            errors.append(f"analysis {field} must be numeric")
    if "estimated_days_remaining" in analysis and analysis["estimated_days_remaining"] is not None:
        if not is_number(analysis["estimated_days_remaining"]):
            errors.append("analysis estimated_days_remaining must be numeric or null")
    if "as_of" in analysis and not isinstance(analysis["as_of"], str):
        errors.append("analysis as_of must be a string")
    elif "as_of" in analysis and not is_iso_date(analysis["as_of"]):
        errors.append("analysis as_of must be an ISO date")
    if "objective_label" in analysis and not isinstance(analysis["objective_label"], str):
        errors.append("analysis objective_label must be a string")
    consent = analysis.get("consent")
    if consent is not None:
        if not isinstance(consent, dict):
            errors.append("analysis consent must be an object")
        elif consent.get("correction_telemetry") not in CORRECTION_TELEMETRY_VALUES:
            errors.append("analysis consent.correction_telemetry is missing or unsupported")
    errors.extend(validate_render_rows(analysis))
    return errors


def is_number(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, int | float)


def validate_render_rows(analysis: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for index, row in enumerate(object_rows(analysis, "items", errors)):
        require_fields(row, f"analysis items[{index}]", ("name", "role", "spend", "consumed_fraction", "notes"), errors)
        require_string_fields(row, f"analysis items[{index}]", ("name", "role", "notes"), errors)
        require_display_string_fields(row, f"analysis items[{index}]", ("category", "confidence"), errors)
        require_numeric_fields(row, f"analysis items[{index}]", ("spend", "consumed_fraction"), errors)
        evidence_rows = row.get("product_evidence", [])
        if evidence_rows is None:
            continue
        if not isinstance(evidence_rows, list):
            errors.append(f"analysis items[{index}].product_evidence must be a list")
        else:
            for evidence_index, evidence in enumerate(evidence_rows):
                if not isinstance(evidence, dict):
                    errors.append(
                        f"analysis items[{index}].product_evidence[{evidence_index}] must be an object"
                    )
                    continue
                require_display_string_fields(
                    evidence,
                    f"analysis items[{index}].product_evidence[{evidence_index}]",
                    ("evidence_type", "source", "checked_date"),
                    errors,
                )
                checked_date = evidence.get("checked_date")
                if isinstance(checked_date, str) and not is_iso_date(checked_date):
                    errors.append(
                        f"analysis items[{index}].product_evidence[{evidence_index}].checked_date must be an ISO date"
                    )

    for index, row in enumerate(object_rows(analysis, "role_summary", errors)):
        require_fields(row, f"analysis role_summary[{index}]", ("role", "spend", "consumed", "consumed_fraction"), errors)
        require_string_fields(row, f"analysis role_summary[{index}]", ("role",), errors)
        require_numeric_fields(row, f"analysis role_summary[{index}]", ("spend", "consumed", "consumed_fraction"), errors)

    for index, row in enumerate(object_rows(analysis, "sourcing_research", errors)):
        require_fields(row, f"analysis sourcing_research[{index}]", ("item", "alternatives"), errors)
        require_string_fields(row, f"analysis sourcing_research[{index}]", ("item",), errors)
        require_display_string_fields(
            row,
            f"analysis sourcing_research[{index}]",
            ("current_source", "confidence", "recommendation"),
            errors,
        )
        alternatives = row.get("alternatives", [])
        if not isinstance(alternatives, list):
            errors.append(f"analysis sourcing_research[{index}].alternatives must be a list")
            continue
        for alternative_index, alternative in enumerate(alternatives):
            if not isinstance(alternative, dict):
                errors.append(
                    f"analysis sourcing_research[{index}].alternatives[{alternative_index}] must be an object"
                )
                continue
            require_display_string_fields(
                alternative,
                f"analysis sourcing_research[{index}].alternatives[{alternative_index}]",
                ("source", "savings", "confidence", "checked_date"),
                errors,
            )
            checked_date = alternative.get("checked_date")
            if isinstance(checked_date, str) and not is_iso_date(checked_date):
                errors.append(
                    f"analysis sourcing_research[{index}].alternatives[{alternative_index}].checked_date must be an ISO date"
                )
            require_numeric_fields(
                alternative,
                f"analysis sourcing_research[{index}].alternatives[{alternative_index}]",
                ("unit_price",),
                errors,
            )
            constraints = alternative.get("constraints", [])
            validate_string_list(
                constraints,
                f"analysis sourcing_research[{index}].alternatives[{alternative_index}].constraints",
                errors,
            )

    for index, row in enumerate(object_rows(analysis, "dietary_profiles", errors)):
        require_display_string_fields(row, f"analysis dietary_profiles[{index}]", ("label",), errors)
        restrictions = row.get("restrictions", [])
        if not isinstance(restrictions, list):
            errors.append(f"analysis dietary_profiles[{index}].restrictions must be a list")
            continue
        for restriction_index, restriction in enumerate(restrictions):
            if not isinstance(restriction, dict):
                errors.append(
                    f"analysis dietary_profiles[{index}].restrictions[{restriction_index}] must be an object"
                )
                continue
            require_display_string_fields(
                restriction,
                f"analysis dietary_profiles[{index}].restrictions[{restriction_index}]",
                ("value", "behavior"),
                errors,
            )

    for index, row in enumerate(object_rows(analysis, "dietary_evaluations", errors)):
        require_fields(row, f"analysis dietary_evaluations[{index}]", ("item", "result", "reason"), errors)
        require_string_fields(row, f"analysis dietary_evaluations[{index}]", ("item", "result", "reason"), errors)

    for index, row in enumerate(object_rows(analysis, "substitutions", errors)):
        require_fields(row, f"analysis substitutions[{index}]", ("candidate", "current", "candidate_unit_price"), errors)
        require_string_fields(row, f"analysis substitutions[{index}]", ("candidate", "current"), errors)
        require_display_string_fields(row, f"analysis substitutions[{index}]", ("fit", "read"), errors)
        require_numeric_fields(row, f"analysis substitutions[{index}]", ("candidate_unit_price",), errors)

    for index, row in enumerate(object_rows(analysis, "pulses", errors)):
        require_fields(row, f"analysis pulses[{index}]", ("date", "text"), errors)
        require_string_fields(row, f"analysis pulses[{index}]", ("date", "text"), errors)
        if isinstance(row.get("date"), str) and not is_iso_date(row["date"]):
            errors.append(f"analysis pulses[{index}].date must be an ISO date")

    for index, row in enumerate(object_rows(analysis, "adapter_matrix", errors)):
        require_display_string_fields(row, f"analysis adapter_matrix[{index}]", ("id", "name", "type"), errors)
        if "score" in row and not is_number(row["score"]):
            errors.append(f"analysis adapter_matrix[{index}].score must be numeric")
        validate_string_list(
            row.get("acquisition_methods", []),
            f"analysis adapter_matrix[{index}].acquisition_methods",
            errors,
        )
        validate_string_list(
            row.get("enabled_capabilities", []),
            f"analysis adapter_matrix[{index}].enabled_capabilities",
            errors,
        )
        validate_string_list(
            row.get("errors", []),
            f"analysis adapter_matrix[{index}].errors",
            errors,
        )

    first_wow = analysis.get("first_wow")
    if isinstance(first_wow, dict):
        if "estimated_unit_savings" in first_wow and not is_number(first_wow["estimated_unit_savings"]):
            errors.append("analysis first_wow.estimated_unit_savings must be numeric")
        require_display_string_fields(
            first_wow,
            "analysis first_wow",
            ("headline", "best_sourcing_move"),
            errors,
        )

    cart_plan = analysis.get("cart_plan")
    if isinstance(cart_plan, dict):
        require_display_string_fields(cart_plan, "analysis cart_plan", ("mode",), errors)
        cart_items = cart_plan.get("items", [])
        if not isinstance(cart_items, list):
            errors.append("analysis cart_plan.items must be a list")
        else:
            for index, row in enumerate(cart_items):
                if not isinstance(row, dict):
                    errors.append(f"analysis cart_plan.items[{index}] must be an object")
                    continue
                require_fields(row, f"analysis cart_plan.items[{index}]", ("item", "action"), errors)
                require_string_fields(row, f"analysis cart_plan.items[{index}]", ("item", "action"), errors)
                require_display_string_fields(
                    row,
                    f"analysis cart_plan.items[{index}]",
                    ("source", "approval_state", "reason"),
                    errors,
                )

    return errors


def object_rows(analysis: dict[str, Any], field: str, errors: list[str]) -> list[dict[str, Any]]:
    value = analysis.get(field)
    if not isinstance(value, list):
        return []
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(value):
        if not isinstance(row, dict):
            errors.append(f"analysis {field}[{index}] must be an object")
            continue
        rows.append(row)
    return rows


def require_fields(
    row: dict[str, Any],
    path: str,
    fields: tuple[str, ...],
    errors: list[str],
) -> None:
    for field in fields:
        if field not in row:
            errors.append(f"{path} missing {field}")


def require_string_fields(
    row: dict[str, Any],
    path: str,
    fields: tuple[str, ...],
    errors: list[str],
) -> None:
    for field in fields:
        if field in row and not isinstance(row[field], str):
            errors.append(f"{path}.{field} must be a string")


def require_optional_string_fields(
    row: dict[str, Any],
    path: str,
    fields: tuple[str, ...],
    errors: list[str],
) -> None:
    for field in fields:
        if field in row and row[field] is not None and not isinstance(row[field], str):
            errors.append(f"{path}.{field} must be a string")


def require_display_string_fields(
    row: dict[str, Any],
    path: str,
    fields: tuple[str, ...],
    errors: list[str],
) -> None:
    for field in fields:
        if field in row and not isinstance(row[field], str):
            errors.append(f"{path}.{field} must be a string")


def require_numeric_fields(
    row: dict[str, Any],
    path: str,
    fields: tuple[str, ...],
    errors: list[str],
) -> None:
    for field in fields:
        if field in row and not is_number(row[field]):
            errors.append(f"{path}.{field} must be numeric")


def validate_string_list(
    value: Any,
    path: str,
    errors: list[str],
    *,
    allow_none: bool = False,
) -> None:
    if value is None and allow_none:
        return
    if not isinstance(value, list):
        errors.append(f"{path} must be a list")
        return
    for index, row in enumerate(value):
        if not isinstance(row, str):
            errors.append(f"{path}[{index}] must be a string")


def cmd_import_normalized(args: argparse.Namespace) -> int:
    state = import_normalized_history(read_json(args.input), profile_id=args.profile_id)
    attach_profiles(state, args.profiles)
    assert_state_contract_clean(state)
    write_json(args.output, state)
    print(f"wrote {args.output}")
    return 0


def cmd_import_csv(args: argparse.Namespace) -> int:
    state = import_csv_history(args.input, profile_id=args.profile_id)
    attach_profiles(state, args.profiles)
    assert_state_contract_clean(state)
    write_json(args.output, state)
    print(f"wrote {args.output}")
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    state = read_json(args.state)
    assert_state_contract_clean(state)
    analysis = analyze_state(state, objective=args.objective)
    assert_analysis_contract_clean(analysis)
    write_json(args.output, analysis)
    print(f"wrote {args.output}")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    analysis = read_json(args.analysis)
    assert_analysis_contract_clean(analysis)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_dashboard(analysis))
    print(f"wrote {args.output}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    state_path = args.state_output or args.output.with_suffix(".state.json")
    analysis_path = args.analysis_output or args.output.with_suffix(".analysis.json")
    state = import_normalized_history(read_json(args.input), profile_id=args.profile_id)
    attach_profiles(state, args.profiles)
    assert_state_contract_clean(state)
    analysis = analyze_state(state, objective=args.objective)
    assert_analysis_contract_clean(analysis)
    write_json(state_path, state)
    write_json(analysis_path, analysis)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_dashboard(analysis))
    print(f"wrote {args.output}")
    return 0


def cmd_corrections_add(args: argparse.Namespace) -> int:
    state = read_json(args.state)
    before = len(state.get("corrections", []))
    record_correction(state, item=args.item, signal=args.signal, note=args.note or "")
    if len(state.get("corrections", [])) == before:
        raise ValueError(
            "correction telemetry consent is not enabled; set consent.correction_telemetry to local_only or hosted_opt_in"
        )
    assert_state_contract_clean(state)
    write_json(args.output or args.state, state)
    print(f"recorded correction for {args.item}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Grocery Flywheel local-first command center.")
    subparsers = parser.add_subparsers(dest="command")

    adapters = subparsers.add_parser("adapters", help="Inspect, validate, and create retailer adapter profiles.")
    adapter_sub = adapters.add_subparsers(dest="adapter_command", required=True)
    validate = adapter_sub.add_parser("validate")
    validate.add_argument("path", type=Path)
    validate.set_defaults(func=cmd_adapters_validate)
    inspect = adapter_sub.add_parser("inspect")
    inspect.add_argument("path", type=Path)
    inspect.add_argument("--format", choices=["table", "json"], default="table")
    inspect.set_defaults(func=cmd_adapters_inspect)
    create = adapter_sub.add_parser("create")
    create.add_argument("--name", required=True)
    create.add_argument("--type", required=True)
    create.add_argument("--channels", required=True)
    create.add_argument("--acquisition-methods")
    create.add_argument("--capabilities", required=True)
    create.add_argument("--region", default="custom")
    create.add_argument("--output", type=Path, required=True)
    create.set_defaults(func=cmd_adapters_create)

    imports = subparsers.add_parser("import", help="Import retailer history into canonical state.")
    import_sub = imports.add_subparsers(dest="import_command", required=True)
    normalized = import_sub.add_parser("normalized")
    normalized.add_argument("input", type=Path)
    normalized.add_argument("--profiles", type=Path)
    normalized.add_argument("--profile-id")
    normalized.add_argument("--output", type=Path, required=True)
    normalized.set_defaults(func=cmd_import_normalized)
    csv_cmd = import_sub.add_parser("csv")
    csv_cmd.add_argument("input", type=Path)
    csv_cmd.add_argument("--profiles", type=Path)
    csv_cmd.add_argument("--profile-id")
    csv_cmd.add_argument("--output", type=Path, required=True)
    csv_cmd.set_defaults(func=cmd_import_csv)

    analyze = subparsers.add_parser("analyze")
    analyze.add_argument("state", type=Path)
    analyze.add_argument("--objective", default="balanced_roi")
    analyze.add_argument("--output", type=Path, required=True)
    analyze.set_defaults(func=cmd_analyze)

    render = subparsers.add_parser("render")
    render.add_argument("analysis", type=Path)
    render.add_argument("--output", type=Path, required=True)
    render.set_defaults(func=cmd_render)

    run = subparsers.add_parser("run")
    run.add_argument("input", type=Path)
    run.add_argument("--profiles", type=Path)
    run.add_argument("--profile-id")
    run.add_argument("--objective", default="balanced_roi")
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--state-output", type=Path)
    run.add_argument("--analysis-output", type=Path)
    run.set_defaults(func=cmd_run)

    corrections = subparsers.add_parser("corrections", help="Record local correction telemetry.")
    correction_sub = corrections.add_subparsers(dest="correction_command", required=True)
    add = correction_sub.add_parser("add")
    add.add_argument("state", type=Path)
    add.add_argument("--item", required=True)
    add.add_argument("--signal", required=True)
    add.add_argument("--note", default="")
    add.add_argument("--output", type=Path)
    add.set_defaults(func=cmd_corrections_add)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        parser = build_parser()
        raw_args = sys.argv[1:] if argv is None else argv
        commands = {"adapters", "import", "analyze", "render", "run", "corrections", "-h", "--help"}
        if raw_args and raw_args[0] not in commands:
            legacy = argparse.ArgumentParser(description="Render a Grocery Flywheel dashboard.")
            legacy.add_argument("state", type=Path)
            legacy.add_argument("--output", "-o", type=Path, required=True)
            args = legacy.parse_args(raw_args)
            state = read_json(args.state)
            assert_state_contract_clean(state)
            analysis = analyze_state(state)
            assert_analysis_contract_clean(analysis)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(render_dashboard(analysis))
            print(f"wrote {args.output}")
            return 0
        args = parser.parse_args(raw_args)
        if not hasattr(args, "func"):
            parser.print_help()
            return 2
        return int(args.func(args))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
