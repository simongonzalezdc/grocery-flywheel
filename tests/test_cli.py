import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args, check=True):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        [sys.executable, "-m", "grocery_flywheel.cli", *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
    return result


def test_adapter_cli_validate_and_inspect_json():
    validate = run_cli("adapters", "validate", "examples/retailer_profiles.json")
    inspect = run_cli("adapters", "inspect", "examples/retailer_profiles.json", "--format", "json")

    rows = json.loads(inspect.stdout)
    assert validate.returncode == 0
    assert rows[0]["id"] == "generic.browser_retailer"
    assert "purchase_history" in rows[0]["enabled_capabilities"]
    assert "cart_plan" in rows[0]["enabled_capabilities"]
    assert "order_submit" not in rows[0]["enabled_capabilities"]


def test_adapter_cli_inspect_validates_profiles_without_traceback(tmp_path):
    profile = json.loads((ROOT / "examples" / "retailer_profiles.json").read_text())[0]
    profile["capabilities"] = False
    profiles_path = tmp_path / "bad-profiles.json"
    profiles_path.write_text(json.dumps([profile]))

    result = run_cli(
        "adapters",
        "inspect",
        str(profiles_path),
        "--format",
        "json",
        check=False,
    )

    assert result.returncode == 1
    assert "capabilities must be an object" in result.stderr
    assert "Traceback" not in result.stderr


def test_adapter_cli_inspect_rejects_malformed_profile_field_types(tmp_path):
    profile = json.loads((ROOT / "examples" / "retailer_profiles.json").read_text())[0]
    profile["acquisition_methods"] = 0
    profiles_path = tmp_path / "bad-profiles.json"
    profiles_path.write_text(json.dumps([profile]))

    result = run_cli(
        "adapters",
        "inspect",
        str(profiles_path),
        "--format",
        "json",
        check=False,
    )

    assert result.returncode == 1
    assert "acquisition_methods must be a list" in result.stderr
    assert "Traceback" not in result.stderr


def test_adapter_cli_create_requires_acquisition_methods_and_writes_valid_profile(tmp_path):
    missing = run_cli(
        "adapters",
        "create",
        "--name",
        "Test Store",
        "--type",
        "grocery",
        "--channels",
        "pickup",
        "--capabilities",
        "purchase_history,product_search,price_lookup,unit_price",
        "--output",
        str(tmp_path / "profile.json"),
        check=False,
    )
    output = tmp_path / "profile.json"
    created = run_cli(
        "adapters",
        "create",
        "--name",
        "Test Store",
        "--type",
        "grocery",
        "--channels",
        "pickup,delivery",
        "--acquisition-methods",
        "retailer_history_import,browser_assisted",
        "--capabilities",
        "purchase_history,product_search,price_lookup,unit_price,availability,substitutions,cart_plan",
        "--output",
        str(output),
    )

    assert missing.returncode == 2
    assert "requires explicit --acquisition-methods" in missing.stderr
    assert created.returncode == 0
    profile = json.loads(output.read_text())[0]
    assert profile["capabilities"]["order_submit"] is False


def test_cli_reports_validation_errors_without_tracebacks(tmp_path):
    bad_create = run_cli(
        "adapters",
        "create",
        "--name",
        "Test Store",
        "--type",
        "grocery",
        "--channels",
        "pickup",
        "--acquisition-methods",
        "retailer_history_import",
        "--capabilities",
        "purchase_history,nope",
        "--output",
        str(tmp_path / "profile.json"),
        check=False,
    )

    assert bad_create.returncode == 1
    assert "unknown capability" in bad_create.stderr
    assert "Traceback" not in bad_create.stderr


def test_import_rejects_invalid_profiles_with_secret_values(tmp_path):
    profile = json.loads((ROOT / "examples" / "retailer_profiles.json").read_text())[0]
    profile["provenance"]["history_source"] = "Bearer sk_live_1234567890"
    profiles_path = tmp_path / "bad-profiles.json"
    profiles_path.write_text(json.dumps([profile]))

    result = run_cli(
        "import",
        "normalized",
        "examples/imports/example-history.json",
        "--profiles",
        str(profiles_path),
        "--output",
        str(tmp_path / "state.json"),
        check=False,
    )

    assert result.returncode == 1
    assert "invalid retailer profile" in result.stderr
    assert "provenance.history_source" in result.stderr
    assert "Traceback" not in result.stderr


def test_import_rejects_malformed_corrections_without_traceback(tmp_path):
    payload = json.loads((ROOT / "examples" / "imports" / "example-history.json").read_text())
    payload["corrections"] = ["bad event"]
    input_path = tmp_path / "bad-history.json"
    input_path.write_text(json.dumps(payload))

    result = run_cli(
        "import",
        "normalized",
        str(input_path),
        "--output",
        str(tmp_path / "state.json"),
        check=False,
    )

    assert result.returncode == 1
    assert "corrections entries must be objects" in result.stderr
    assert "Traceback" not in result.stderr


def test_import_rejects_disabled_consent_corrections_without_traceback(tmp_path):
    payload = json.loads((ROOT / "examples" / "imports" / "example-history.json").read_text())
    payload["consent"] = {
        "correction_telemetry": "disabled",
        "hosted_sync": False,
        "retailer_session_storage": "none",
        "password_storage": "forbidden",
    }
    input_path = tmp_path / "disabled-corrections.json"
    input_path.write_text(json.dumps(payload))

    result = run_cli(
        "import",
        "normalized",
        str(input_path),
        "--output",
        str(tmp_path / "state.json"),
        check=False,
    )

    assert result.returncode == 1
    assert "corrections require local_only or hosted_opt_in" in result.stderr
    assert "Traceback" not in result.stderr


def test_import_rejects_malformed_falsey_consent_without_traceback(tmp_path):
    payload = json.loads((ROOT / "examples" / "imports" / "example-history.json").read_text())
    payload["consent"] = False
    input_path = tmp_path / "false-consent.json"
    input_path.write_text(json.dumps(payload))

    result = run_cli(
        "import",
        "normalized",
        str(input_path),
        "--output",
        str(tmp_path / "state.json"),
        check=False,
    )

    assert result.returncode == 1
    assert "consent must be an object" in result.stderr
    assert "Traceback" not in result.stderr


def test_import_rejects_malformed_items_without_traceback(tmp_path):
    for value in (0, False, "", {}):
        payload = json.loads((ROOT / "examples" / "imports" / "example-history.json").read_text())
        payload["items"] = value
        input_path = tmp_path / f"bad-items-{type(value).__name__}.json"
        output_path = tmp_path / f"bad-items-{type(value).__name__}.state.json"
        input_path.write_text(json.dumps(payload))

        result = run_cli(
            "import",
            "normalized",
            str(input_path),
            "--output",
            str(output_path),
            check=False,
        )

        assert result.returncode == 1
        assert "items must be a list" in result.stderr
        assert "Traceback" not in result.stderr
        assert not output_path.exists()


def test_import_rejects_non_object_payload_without_traceback(tmp_path):
    input_path = tmp_path / "bad-payload.json"
    output_path = tmp_path / "bad-payload.state.json"
    input_path.write_text(json.dumps([]))

    result = run_cli(
        "import",
        "normalized",
        str(input_path),
        "--output",
        str(output_path),
        check=False,
    )

    assert result.returncode == 1
    assert "normalized import payload must be an object" in result.stderr
    assert "Traceback" not in result.stderr
    assert not output_path.exists()


def test_import_rejects_malformed_item_objects_without_traceback(tmp_path):
    cases = [
        ([{}], "items[0] missing name"),
        ([{"name": "Coffee", "spend": "not money"}], "items[0].spend must be numeric"),
        (
            [{"name": "Coffee", "spend": 1, "product_evidence": "bad"}],
            "items[0].product_evidence must be a list",
        ),
    ]
    for index, (items, expected) in enumerate(cases):
        payload = json.loads((ROOT / "examples" / "imports" / "example-history.json").read_text())
        payload["items"] = items
        input_path = tmp_path / f"bad-item-object-{index}.json"
        output_path = tmp_path / f"bad-item-object-{index}.state.json"
        input_path.write_text(json.dumps(payload))

        result = run_cli(
            "import",
            "normalized",
            str(input_path),
            "--output",
            str(output_path),
            check=False,
        )

        assert result.returncode == 1
        assert expected in result.stderr
        assert "Traceback" not in result.stderr
        assert not output_path.exists()


def test_import_analyze_render_and_run_vertical_slice(tmp_path):
    state_path = tmp_path / "state.json"
    analysis_path = tmp_path / "analysis.json"
    html_path = tmp_path / "dashboard.html"
    run_html = tmp_path / "run-dashboard.html"

    run_cli(
        "import",
        "normalized",
        "examples/imports/example-history.json",
        "--profiles",
        "examples/retailer_profiles.json",
        "--output",
        str(state_path),
    )
    run_cli("analyze", str(state_path), "--objective", "balanced_roi", "--output", str(analysis_path))
    run_cli("render", str(analysis_path), "--output", str(html_path))
    run_cli(
        "run",
        "examples/imports/example-history.json",
        "--profiles",
        "examples/retailer_profiles.json",
        "--objective",
        "lowest_cost",
        "--output",
        str(run_html),
    )

    state = json.loads(state_path.read_text())
    analysis = json.loads(analysis_path.read_text())
    html = html_path.read_text()
    run_output = run_html.read_text()

    assert state["schema_version"]
    assert analysis["objective"] == "balanced_roi"
    assert analysis["first_wow"]["estimated_unit_savings"] > 0
    assert "Sourcing Alternatives" in html
    assert "Potential Unit Savings" in run_output
    assert "checkout unavailable" in run_output


def test_legacy_sample_state_positional_render_path_still_works(tmp_path):
    html_path = tmp_path / "sample-dashboard.html"

    result = run_cli(
        "examples/sample_state.json",
        "--output",
        str(html_path),
        check=False,
    )

    assert result.returncode == 0
    assert "Traceback" not in result.stderr
    assert "Grocery Flywheel" in html_path.read_text()


def test_analyze_fails_closed_on_contract_errors(tmp_path):
    payload = json.loads((ROOT / "examples" / "imports" / "example-history.json").read_text())
    state_path = tmp_path / "bad-state.json"
    analysis_path = tmp_path / "analysis.json"

    run_cli(
        "import",
        "normalized",
        "examples/imports/example-history.json",
        "--output",
        str(state_path),
    )
    state = json.loads(state_path.read_text())
    state["external_cart_draft"] = {"items": []}
    state_path.write_text(json.dumps(state))

    result = run_cli(
        "analyze",
        str(state_path),
        "--output",
        str(analysis_path),
        check=False,
    )

    assert payload["source"] == "retailer_history_import"
    assert result.returncode == 1
    assert "external_cart_draft is excluded from MVP code paths" in result.stderr
    assert not analysis_path.exists()


def test_analyze_fails_closed_for_unversioned_state_with_excluded_cart_surface(tmp_path):
    state_path = tmp_path / "bad-unversioned-state.json"
    analysis_path = tmp_path / "analysis.json"
    state_path.write_text(
        json.dumps(
            {
                "as_of": "2026-05-26",
                "order": {"store": "Example", "date": "2026-05-20", "total": 1},
                "items": [],
                "external_cart_draft": {"items": []},
            }
        )
    )

    result = run_cli(
        "analyze",
        str(state_path),
        "--output",
        str(analysis_path),
        check=False,
    )

    assert result.returncode == 1
    assert "state schema_version is missing or unsupported" in result.stderr
    assert "external_cart_draft is excluded from MVP code paths" in result.stderr
    assert not analysis_path.exists()


def test_analyze_fails_closed_for_non_object_state_without_traceback(tmp_path):
    state_path = tmp_path / "bad-state.json"
    analysis_path = tmp_path / "analysis.json"
    state_path.write_text(json.dumps([]))

    result = run_cli(
        "analyze",
        str(state_path),
        "--output",
        str(analysis_path),
        check=False,
    )

    assert result.returncode == 1
    assert "state must be an object" in result.stderr
    assert "Traceback" not in result.stderr
    assert not analysis_path.exists()


def test_analyze_fails_closed_for_non_object_order_without_traceback(tmp_path):
    state_path = tmp_path / "bad-order-state.json"
    analysis_path = tmp_path / "analysis.json"
    run_cli(
        "import",
        "normalized",
        "examples/imports/example-history.json",
        "--output",
        str(state_path),
    )
    state = json.loads(state_path.read_text())
    state["order"] = False
    state_path.write_text(json.dumps(state))

    result = run_cli(
        "analyze",
        str(state_path),
        "--output",
        str(analysis_path),
        check=False,
    )

    assert result.returncode == 1
    assert "order must be an object" in result.stderr
    assert "Traceback" not in result.stderr
    assert not analysis_path.exists()


def test_analyze_fails_closed_for_missing_order_total_without_traceback(tmp_path):
    state_path = tmp_path / "missing-order-total-state.json"
    analysis_path = tmp_path / "analysis.json"
    run_cli(
        "import",
        "normalized",
        "examples/imports/example-history.json",
        "--output",
        str(state_path),
    )
    state = json.loads(state_path.read_text())
    state["order"].pop("total")
    state_path.write_text(json.dumps(state))

    result = run_cli(
        "analyze",
        str(state_path),
        "--output",
        str(analysis_path),
        check=False,
    )

    assert result.returncode == 1
    assert "order missing total" in result.stderr
    assert "Traceback" not in result.stderr
    assert not analysis_path.exists()


def test_analyze_fails_closed_for_invalid_dates_without_traceback(tmp_path):
    state_path = tmp_path / "invalid-date-state.json"
    analysis_path = tmp_path / "analysis.json"
    run_cli(
        "import",
        "normalized",
        "examples/imports/example-history.json",
        "--output",
        str(state_path),
    )
    state = json.loads(state_path.read_text())
    state["as_of"] = "not-a-date"
    state["order"]["date"] = "also-bad"
    state_path.write_text(json.dumps(state))

    result = run_cli(
        "analyze",
        str(state_path),
        "--output",
        str(analysis_path),
        check=False,
    )

    assert result.returncode == 1
    assert "as_of must be an ISO date" in result.stderr
    assert "order.date must be an ISO date" in result.stderr
    assert "Traceback" not in result.stderr
    assert not analysis_path.exists()


def test_analyze_fails_closed_for_non_canonical_iso_dates_without_traceback(tmp_path):
    state_path = tmp_path / "non-canonical-date-state.json"
    analysis_path = tmp_path / "analysis.json"
    run_cli(
        "import",
        "normalized",
        "examples/imports/example-history.json",
        "--output",
        str(state_path),
    )
    state = json.loads(state_path.read_text())
    state["as_of"] = "20260526"
    state["order"]["date"] = "2026-W22-2"
    state_path.write_text(json.dumps(state))

    result = run_cli(
        "analyze",
        str(state_path),
        "--output",
        str(analysis_path),
        check=False,
    )

    assert result.returncode == 1
    assert "as_of must be an ISO date" in result.stderr
    assert "order.date must be an ISO date" in result.stderr
    assert "Traceback" not in result.stderr
    assert not analysis_path.exists()


def test_analyze_fails_closed_for_malformed_items_without_traceback(tmp_path):
    state_path = tmp_path / "bad-items-state.json"
    analysis_path = tmp_path / "analysis.json"
    state_path.write_text(
        json.dumps(
            {
                "schema_version": "2026-05-26.mvp1",
                "as_of": "2026-05-26",
                "order": {
                    "schema_version": "2026-05-26.mvp1",
                    "store": "Example",
                    "date": "2026-05-20",
                    "total": 1,
                },
                "privacy": {"purchase_history": "sensitive_purchase_history"},
                "consent": {
                    "correction_telemetry": "local_only",
                    "hosted_sync": False,
                    "retailer_session_storage": "none",
                    "password_storage": "forbidden",
                },
                "items": 0,
            }
        )
    )

    result = run_cli(
        "analyze",
        str(state_path),
        "--output",
        str(analysis_path),
        check=False,
    )

    assert result.returncode == 1
    assert "items must be a list" in result.stderr
    assert "Traceback" not in result.stderr
    assert not analysis_path.exists()


def test_analyze_fails_closed_for_malformed_item_fields_without_traceback(tmp_path):
    state_path = tmp_path / "bad-item-fields-state.json"
    analysis_path = tmp_path / "analysis.json"
    run_cli(
        "import",
        "normalized",
        "examples/imports/example-history.json",
        "--output",
        str(state_path),
    )
    state = json.loads(state_path.read_text())
    state["items"][0].pop("name")
    state["items"][0]["spend"] = "expensive"
    state_path.write_text(json.dumps(state))

    result = run_cli(
        "analyze",
        str(state_path),
        "--output",
        str(analysis_path),
        check=False,
    )

    assert result.returncode == 1
    assert "items[0].name must be a string" in result.stderr
    assert "items[0].spend must be numeric" in result.stderr
    assert "Traceback" not in result.stderr
    assert not analysis_path.exists()


def test_analyze_fails_closed_for_malformed_sourcing_research_without_traceback(tmp_path):
    state_path = tmp_path / "bad-sourcing-state.json"
    analysis_path = tmp_path / "analysis.json"
    run_cli(
        "import",
        "normalized",
        "examples/imports/example-history.json",
        "--output",
        str(state_path),
    )
    state = json.loads(state_path.read_text())
    state["sourcing_research"] = [{"alternatives": [{"savings_amount": {}}]}]
    state_path.write_text(json.dumps(state))

    result = run_cli(
        "analyze",
        str(state_path),
        "--output",
        str(analysis_path),
        check=False,
    )

    assert result.returncode == 1
    assert "sourcing_research[0].item must be a string" in result.stderr
    assert "sourcing_research[0].alternatives[0].savings_amount must be numeric" in result.stderr
    assert "Traceback" not in result.stderr
    assert not analysis_path.exists()


def test_analyze_fails_closed_for_malformed_substitutions_without_traceback(tmp_path):
    state_path = tmp_path / "bad-substitutions-state.json"
    analysis_path = tmp_path / "analysis.json"
    run_cli(
        "import",
        "normalized",
        "examples/imports/example-history.json",
        "--output",
        str(state_path),
    )
    state = json.loads(state_path.read_text())
    state["substitutions"] = [
        {
            "current": "Coffee",
            "candidate": "Warehouse coffee",
            "current_unit_price": {},
            "candidate_unit_price": 1,
            "candidate_product_evidence": 1,
        }
    ]
    state_path.write_text(json.dumps(state))

    result = run_cli(
        "analyze",
        str(state_path),
        "--output",
        str(analysis_path),
        check=False,
    )

    assert result.returncode == 1
    assert "substitutions[0].current_unit_price must be numeric" in result.stderr
    assert "substitutions[0].candidate_product_evidence must be a list" in result.stderr
    assert "Traceback" not in result.stderr
    assert not analysis_path.exists()


def test_analyze_fails_closed_for_malformed_dietary_profiles_without_traceback(tmp_path):
    state_path = tmp_path / "bad-dietary-state.json"
    analysis_path = tmp_path / "analysis.json"
    run_cli(
        "import",
        "normalized",
        "examples/imports/example-history.json",
        "--output",
        str(state_path),
    )
    state = json.loads(state_path.read_text())
    state["dietary_profiles"] = [False]
    state_path.write_text(json.dumps(state))

    result = run_cli(
        "analyze",
        str(state_path),
        "--output",
        str(analysis_path),
        check=False,
    )

    assert result.returncode == 1
    assert "dietary_profiles[0] must be an object" in result.stderr
    assert "Traceback" not in result.stderr
    assert not analysis_path.exists()


def test_analyze_fails_closed_for_null_dietary_restrictions_without_traceback(tmp_path):
    state_path = tmp_path / "bad-dietary-restrictions-state.json"
    analysis_path = tmp_path / "analysis.json"
    run_cli(
        "import",
        "normalized",
        "examples/imports/example-history.json",
        "--output",
        str(state_path),
    )
    state = json.loads(state_path.read_text())
    state["dietary_profiles"] = [{"profile_id": "bad", "restrictions": None}]
    state_path.write_text(json.dumps(state))

    result = run_cli(
        "analyze",
        str(state_path),
        "--output",
        str(analysis_path),
        check=False,
    )

    assert result.returncode == 1
    assert "dietary_profiles[0].restrictions must be a list" in result.stderr
    assert "Traceback" not in result.stderr
    assert not analysis_path.exists()


def test_analyze_rejects_disabled_consent_with_existing_corrections(tmp_path):
    state_path = tmp_path / "disabled-existing-corrections.json"
    analysis_path = tmp_path / "analysis.json"
    run_cli(
        "import",
        "normalized",
        "examples/imports/example-history.json",
        "--output",
        str(state_path),
    )
    state = json.loads(state_path.read_text())
    state["consent"]["correction_telemetry"] = "disabled"
    state_path.write_text(json.dumps(state))

    result = run_cli(
        "analyze",
        str(state_path),
        "--output",
        str(analysis_path),
        check=False,
    )

    assert result.returncode == 1
    assert "sensitive correction telemetry requires local_only or hosted_opt_in consent" in result.stderr
    assert "Traceback" not in result.stderr
    assert not analysis_path.exists()


def test_render_fails_closed_on_analysis_contract_errors(tmp_path):
    analysis_path = tmp_path / "bad-analysis.json"
    html_path = tmp_path / "dashboard.html"
    analysis_path.write_text(
        json.dumps(
            {
                "schema_version": "2026-05-26.mvp1",
                "order": {"store": "Example", "date": "2026-05-20", "total": 1},
                "as_of": "2026-05-26",
                "estimated_days_remaining": None,
                "known_consumed_fraction": 0,
                "days_elapsed": 1,
                "consumed_value": 0,
                "contract_errors": ["external_cart_draft is excluded from MVP code paths"],
                "items": [],
                "role_summary": [],
                "sourcing_research": [],
                "dietary_profiles": [],
                "substitutions": [],
                "pulses": [],
            }
        )
    )

    result = run_cli(
        "render",
        str(analysis_path),
        "--output",
        str(html_path),
        check=False,
    )

    assert result.returncode == 1
    assert "external_cart_draft is excluded from MVP code paths" in result.stderr
    assert not html_path.exists()


def test_render_validates_analysis_shape_and_consent(tmp_path):
    analysis_path = tmp_path / "bad-analysis-shape.json"
    html_path = tmp_path / "dashboard.html"
    analysis_path.write_text(
        json.dumps(
            {
                "schema_version": "2026-05-26.mvp1",
                "order": {"store": "Example", "date": "2026-05-20", "total": 1},
                "as_of": "2026-05-26",
                "contract_errors": [],
                "estimated_days_remaining": None,
                "known_consumed_fraction": 0,
                "days_elapsed": 1,
                "consumed_value": 0,
                "items": [],
                "role_summary": [],
                "sourcing_research": [],
                "dietary_profiles": [],
                "substitutions": [],
                "pulses": [],
                "consent": False,
            }
        )
    )

    result = run_cli(
        "render",
        str(analysis_path),
        "--output",
        str(html_path),
        check=False,
    )

    assert result.returncode == 1
    assert "analysis consent must be an object" in result.stderr
    assert "Traceback" not in result.stderr
    assert not html_path.exists()


def test_render_rejects_missing_required_analysis_fields(tmp_path):
    analysis_path = tmp_path / "missing-analysis-fields.json"
    html_path = tmp_path / "dashboard.html"
    analysis_path.write_text(json.dumps({"contract_errors": []}))

    result = run_cli(
        "render",
        str(analysis_path),
        "--output",
        str(html_path),
        check=False,
    )

    assert result.returncode == 1
    assert "analysis missing order" in result.stderr
    assert "analysis missing items" in result.stderr
    assert not html_path.exists()


def test_render_rejects_unsupported_analysis_schema_version(tmp_path):
    analysis_path = tmp_path / "unsupported-schema-analysis.json"
    html_path = tmp_path / "dashboard.html"
    analysis_path.write_text(
        json.dumps(
            {
                "schema_version": "bad",
                "order": {"store": "Example", "date": "2026-05-20", "total": 1},
                "as_of": "2026-05-26",
                "contract_errors": [],
                "estimated_days_remaining": None,
                "known_consumed_fraction": 0,
                "days_elapsed": 1,
                "consumed_value": 0,
                "items": [],
                "role_summary": [],
                "sourcing_research": [],
                "dietary_profiles": [],
                "substitutions": [],
                "pulses": [],
            }
        )
    )

    result = run_cli(
        "render",
        str(analysis_path),
        "--output",
        str(html_path),
        check=False,
    )

    assert result.returncode == 1
    assert "analysis schema_version is missing or unsupported" in result.stderr
    assert "Traceback" not in result.stderr
    assert not html_path.exists()


def test_render_rejects_non_canonical_analysis_dates(tmp_path):
    analysis_path = tmp_path / "bad-analysis-dates.json"
    html_path = tmp_path / "dashboard.html"
    analysis_path.write_text(
        json.dumps(
            {
                "schema_version": "2026-05-26.mvp1",
                "order": {"store": "Example", "date": "2026-W22-2", "total": 1},
                "as_of": "20260526",
                "contract_errors": [],
                "estimated_days_remaining": None,
                "known_consumed_fraction": 0,
                "days_elapsed": 1,
                "consumed_value": 0,
                "items": [
                    {
                        "name": "Coffee",
                        "role": "coffee",
                        "spend": 1,
                        "consumed_fraction": 0,
                        "notes": "",
                        "product_evidence": [
                            {
                                "evidence_type": "ingredient_label",
                                "source": "package",
                                "checked_date": "20260526",
                            }
                        ],
                    }
                ],
                "role_summary": [],
                "sourcing_research": [
                    {
                        "item": "Coffee",
                        "alternatives": [
                            {
                                "source": "Warehouse",
                                "unit_price": 0.5,
                                "checked_date": "2026-W22-2",
                            }
                        ],
                    }
                ],
                "dietary_profiles": [],
                "substitutions": [],
                "pulses": [{"date": "20260526", "text": "Bad compact date."}],
            }
        )
    )

    result = run_cli(
        "render",
        str(analysis_path),
        "--output",
        str(html_path),
        check=False,
    )

    assert result.returncode == 1
    assert "analysis as_of must be an ISO date" in result.stderr
    assert "analysis order.date must be an ISO date" in result.stderr
    assert "analysis items[0].product_evidence[0].checked_date must be an ISO date" in result.stderr
    assert "analysis sourcing_research[0].alternatives[0].checked_date must be an ISO date" in result.stderr
    assert "analysis pulses[0].date must be an ISO date" in result.stderr
    assert "Traceback" not in result.stderr
    assert not html_path.exists()


def test_render_rejects_malformed_display_strings(tmp_path):
    analysis_path = tmp_path / "bad-display-strings.json"
    html_path = tmp_path / "dashboard.html"
    analysis_path.write_text(
        json.dumps(
            {
                "schema_version": "2026-05-26.mvp1",
                "order": {"store": "Example", "date": "2026-05-20", "total": 1},
                "as_of": "2026-05-26",
                "objective_label": ["bad"],
                "contract_errors": [],
                "estimated_days_remaining": None,
                "known_consumed_fraction": 0,
                "days_elapsed": 1,
                "consumed_value": 0,
                "first_wow": {
                    "estimated_unit_savings": 1,
                    "headline": [],
                    "best_sourcing_move": [],
                },
                "items": [
                    {
                        "name": "Coffee",
                        "role": "coffee",
                        "spend": 1,
                        "consumed_fraction": 0,
                        "notes": "",
                        "category": [],
                        "confidence": [],
                        "product_evidence": [
                            {
                                "evidence_type": [],
                                "source": [],
                                "checked_date": [],
                            }
                        ],
                    }
                ],
                "role_summary": [],
                "sourcing_research": [],
                "dietary_profiles": [
                    {
                        "label": [],
                        "restrictions": [{"value": [], "behavior": []}],
                    }
                ],
                "substitutions": [],
                "pulses": [],
                "cart_plan": {"mode": [], "items": []},
            }
        )
    )

    result = run_cli(
        "render",
        str(analysis_path),
        "--output",
        str(html_path),
        check=False,
    )

    assert result.returncode == 1
    assert "analysis objective_label must be a string" in result.stderr
    assert "analysis first_wow.headline must be a string" in result.stderr
    assert "analysis first_wow.best_sourcing_move must be a string" in result.stderr
    assert "analysis items[0].category must be a string" in result.stderr
    assert "analysis items[0].product_evidence[0].source must be a string" in result.stderr
    assert "analysis dietary_profiles[0].label must be a string" in result.stderr
    assert "analysis dietary_profiles[0].restrictions[0].value must be a string" in result.stderr
    assert "analysis cart_plan.mode must be a string" in result.stderr
    assert "Traceback" not in result.stderr
    assert not html_path.exists()


def test_render_rejects_null_display_strings(tmp_path):
    analysis_path = tmp_path / "null-display-strings.json"
    html_path = tmp_path / "dashboard.html"
    analysis_path.write_text(
        json.dumps(
            {
                "schema_version": "2026-05-26.mvp1",
                "order": {"store": "Example", "date": "2026-05-20", "total": 1},
                "as_of": "2026-05-26",
                "contract_errors": [],
                "estimated_days_remaining": None,
                "known_consumed_fraction": 0,
                "days_elapsed": 1,
                "consumed_value": 0,
                "first_wow": {
                    "estimated_unit_savings": 1,
                    "headline": None,
                    "best_sourcing_move": None,
                },
                "items": [],
                "role_summary": [],
                "sourcing_research": [],
                "dietary_profiles": [],
                "substitutions": [],
                "pulses": [],
            }
        )
    )

    result = run_cli(
        "render",
        str(analysis_path),
        "--output",
        str(html_path),
        check=False,
    )

    assert result.returncode == 1
    assert "analysis first_wow.headline must be a string" in result.stderr
    assert "analysis first_wow.best_sourcing_move must be a string" in result.stderr
    assert "Traceback" not in result.stderr
    assert not html_path.exists()


def test_render_requires_contract_errors_field(tmp_path):
    analysis_path = tmp_path / "missing-contract-errors.json"
    html_path = tmp_path / "dashboard.html"
    analysis_path.write_text(
        json.dumps(
            {
                "schema_version": "2026-05-26.mvp1",
                "order": {"store": "Example", "date": "2026-05-20", "total": 1},
                "as_of": "2026-05-26",
                "estimated_days_remaining": None,
                "known_consumed_fraction": 0,
                "days_elapsed": 1,
                "consumed_value": 0,
                "items": [],
                "role_summary": [],
                "sourcing_research": [],
                "dietary_profiles": [],
                "substitutions": [],
                "pulses": [],
            }
        )
    )

    result = run_cli(
        "render",
        str(analysis_path),
        "--output",
        str(html_path),
        check=False,
    )

    assert result.returncode == 1
    assert "analysis missing contract_errors" in result.stderr
    assert "Traceback" not in result.stderr
    assert not html_path.exists()


def test_render_rejects_malformed_renderer_rows(tmp_path):
    analysis_path = tmp_path / "bad-render-rows.json"
    html_path = tmp_path / "dashboard.html"
    analysis_path.write_text(
        json.dumps(
            {
                "schema_version": "2026-05-26.mvp1",
                "order": {"store": "Example", "date": "2026-05-20", "total": 1},
                "as_of": "2026-05-26",
                "contract_errors": [],
                "estimated_days_remaining": None,
                "known_consumed_fraction": 0,
                "days_elapsed": 1,
                "consumed_value": 0,
                "items": [{}],
                "role_summary": [{"role": "pantry", "spend": 1, "consumed": 0, "consumed_fraction": 0}],
                "sourcing_research": [],
                "dietary_profiles": [],
                "substitutions": [],
                "pulses": [],
            }
        )
    )

    result = run_cli(
        "render",
        str(analysis_path),
        "--output",
        str(html_path),
        check=False,
    )

    assert result.returncode == 1
    assert "analysis items[0] missing name" in result.stderr
    assert "analysis items[0] missing notes" in result.stderr
    assert "Traceback" not in result.stderr
    assert not html_path.exists()


def test_render_rejects_malformed_adapter_and_optional_rows(tmp_path):
    analysis_path = tmp_path / "bad-adapter-row.json"
    html_path = tmp_path / "dashboard.html"
    analysis_path.write_text(
        json.dumps(
            {
                "schema_version": "2026-05-26.mvp1",
                "order": {"store": "Example", "date": "2026-05-20", "total": 1},
                "as_of": "2026-05-26",
                "contract_errors": [],
                "estimated_days_remaining": None,
                "known_consumed_fraction": 0,
                "days_elapsed": 1,
                "consumed_value": 0,
                "items": [],
                "role_summary": [],
                "sourcing_research": [
                    {"item": "Coffee", "alternatives": [{"unit_price": 1, "constraints": [False]}]}
                ],
                "dietary_profiles": [],
                "substitutions": [{"candidate": "A", "current": "B", "candidate_unit_price": 1, "fit": []}],
                "pulses": [],
                "adapter_matrix": [{"name": [], "score": "high", "acquisition_methods": [0], "errors": [False]}],
                "cart_plan": {"items": [{"item": "Coffee", "action": "add", "reason": []}]},
            }
        )
    )

    result = run_cli(
        "render",
        str(analysis_path),
        "--output",
        str(html_path),
        check=False,
    )

    assert result.returncode == 1
    assert "analysis adapter_matrix[0].name must be a string" in result.stderr
    assert "analysis adapter_matrix[0].score must be numeric" in result.stderr
    assert "analysis adapter_matrix[0].acquisition_methods[0] must be a string" in result.stderr
    assert "analysis sourcing_research[0].alternatives[0].constraints[0] must be a string" in result.stderr
    assert "analysis substitutions[0].fit must be a string" in result.stderr
    assert "analysis cart_plan.items[0].reason must be a string" in result.stderr
    assert "Traceback" not in result.stderr
    assert not html_path.exists()


def test_render_rejects_null_renderer_consumed_lists(tmp_path):
    analysis_path = tmp_path / "null-render-lists.json"
    html_path = tmp_path / "dashboard.html"
    analysis_path.write_text(
        json.dumps(
            {
                "schema_version": "2026-05-26.mvp1",
                "order": {"store": "Example", "date": "2026-05-20", "total": 1},
                "as_of": "2026-05-26",
                "contract_errors": [],
                "estimated_days_remaining": None,
                "known_consumed_fraction": 0,
                "days_elapsed": 1,
                "consumed_value": 0,
                "items": [],
                "role_summary": [],
                "sourcing_research": [
                    {"item": "Coffee", "alternatives": [{"unit_price": 1, "constraints": None}]}
                ],
                "dietary_profiles": [],
                "substitutions": [],
                "pulses": [],
                "adapter_matrix": [
                    {
                        "name": "Adapter",
                        "score": 1,
                        "acquisition_methods": None,
                        "enabled_capabilities": None,
                        "errors": None,
                    }
                ],
            }
        )
    )

    result = run_cli(
        "render",
        str(analysis_path),
        "--output",
        str(html_path),
        check=False,
    )

    assert result.returncode == 1
    assert "analysis sourcing_research[0].alternatives[0].constraints must be a list" in result.stderr
    assert "analysis adapter_matrix[0].acquisition_methods must be a list" in result.stderr
    assert "analysis adapter_matrix[0].enabled_capabilities must be a list" in result.stderr
    assert "analysis adapter_matrix[0].errors must be a list" in result.stderr
    assert "Traceback" not in result.stderr
    assert not html_path.exists()


def test_render_rejects_non_list_adapter_matrix(tmp_path):
    analysis_path = tmp_path / "bad-adapter-matrix.json"
    html_path = tmp_path / "dashboard.html"
    analysis_path.write_text(
        json.dumps(
            {
                "schema_version": "2026-05-26.mvp1",
                "order": {"store": "Example", "date": "2026-05-20", "total": 1},
                "as_of": "2026-05-26",
                "contract_errors": [],
                "estimated_days_remaining": None,
                "known_consumed_fraction": 0,
                "days_elapsed": 1,
                "consumed_value": 0,
                "items": [],
                "role_summary": [],
                "sourcing_research": [],
                "dietary_profiles": [],
                "substitutions": [],
                "pulses": [],
                "adapter_matrix": {"bad": "shape"},
            }
        )
    )

    result = run_cli(
        "render",
        str(analysis_path),
        "--output",
        str(html_path),
        check=False,
    )

    assert result.returncode == 1
    assert "analysis adapter_matrix must be a list" in result.stderr
    assert "Traceback" not in result.stderr
    assert not html_path.exists()


def test_render_rejects_null_dietary_restrictions_and_cart_items(tmp_path):
    analysis_path = tmp_path / "null-dietary-cart-lists.json"
    html_path = tmp_path / "dashboard.html"
    analysis_path.write_text(
        json.dumps(
            {
                "schema_version": "2026-05-26.mvp1",
                "order": {"store": "Example", "date": "2026-05-20", "total": 1},
                "as_of": "2026-05-26",
                "contract_errors": [],
                "estimated_days_remaining": None,
                "known_consumed_fraction": 0,
                "days_elapsed": 1,
                "consumed_value": 0,
                "items": [],
                "role_summary": [],
                "sourcing_research": [],
                "dietary_profiles": [{"profile_id": "bad", "restrictions": None}],
                "substitutions": [],
                "pulses": [],
                "cart_plan": {"items": None},
            }
        )
    )

    result = run_cli(
        "render",
        str(analysis_path),
        "--output",
        str(html_path),
        check=False,
    )

    assert result.returncode == 1
    assert "analysis dietary_profiles[0].restrictions must be a list" in result.stderr
    assert "analysis cart_plan.items must be a list" in result.stderr
    assert "Traceback" not in result.stderr
    assert not html_path.exists()


def test_corrections_add_records_private_local_event(tmp_path):
    state_path = tmp_path / "state.json"
    output_path = tmp_path / "corrected-state.json"
    run_cli(
        "import",
        "normalized",
        "examples/imports/example-history.json",
        "--output",
        str(state_path),
    )

    result = run_cli(
        "corrections",
        "add",
        str(state_path),
        "--item",
        "Cafe Bustelo bricks",
        "--signal",
        "good_default",
        "--note",
        "Moka pot default",
        "--output",
        str(output_path),
    )
    state = json.loads(output_path.read_text())

    assert result.returncode == 0
    assert state["corrections"][-1]["privacy_class"] == "sensitive_correction_telemetry"
    assert state["corrections"][-1]["signal"] == "good_default"


def test_profiles_file_must_not_be_empty(tmp_path):
    empty_profiles = tmp_path / "empty-profiles.json"
    empty_profiles.write_text("[]")

    result = run_cli(
        "import",
        "normalized",
        "examples/imports/example-history.json",
        "--profiles",
        str(empty_profiles),
        "--output",
        str(tmp_path / "state.json"),
        check=False,
    )

    assert result.returncode != 0
    assert "at least one profile" in result.stderr
