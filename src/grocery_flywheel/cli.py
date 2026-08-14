from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import analyze_state
from .importers import import_csv_history, import_normalized_history
from .model.contract import validate_canonical_state
from .render import render_dashboard
from .state_io import load_state, render_to_file, write_state


def main(argv: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "import":
        _run_import(argv[1:])
        return

    parser = argparse.ArgumentParser(description="Render a Grocery Flywheel dashboard.")
    parser.add_argument("state", type=Path, help="Path to replenishment state JSON.")
    parser.add_argument("--output", "-o", type=Path, required=True, help="HTML output path.")
    args = parser.parse_args(argv)

    state = load_state(args.state)
    analysis = analyze_state(state)
    target = render_to_file(render_dashboard(analysis), args.output)
    print(f"wrote {target}")


def _run_import(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(
        prog="grocery-flywheel import",
        description="Import retailer history into a canonical state file.",
    )
    sub = parser.add_subparsers(dest="kind", required=True)

    normalized = sub.add_parser("normalized", help="Import a normalized JSON history payload.")
    normalized.add_argument("payload", type=Path)
    normalized.add_argument("--profile-id", default=None)
    normalized.add_argument("--as-of", default=None, help="Override the as_of date (ISO).")
    normalized.add_argument("--output", "-o", type=Path, required=True,
                            help="Canonical state JSON to write.")

    csv = sub.add_parser("csv", help="Import a CSV export.")
    csv.add_argument("payload", type=Path)
    csv.add_argument("--profile-id", default=None)
    csv.add_argument("--output", "-o", type=Path, required=True,
                     help="Canonical state JSON to write.")

    args = parser.parse_args(argv)

    if args.kind == "normalized":
        state = import_normalized_history(
            json.loads(args.payload.read_text()),
            profile_id=args.profile_id,
            as_of=args.as_of,
        )
    else:
        state = import_csv_history(args.payload, profile_id=args.profile_id)

    errors = validate_canonical_state(state)
    if errors:
        for error in errors:
            print(f"contract violation: {error}", file=sys.stderr)
        raise SystemExit(2)

    write_state(state, args.output)
    print(f"wrote {args.output} ({len(state['items'])} items, schema {state['schema_version']})")


if __name__ == "__main__":
    main()
