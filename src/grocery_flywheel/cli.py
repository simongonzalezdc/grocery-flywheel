from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import analyze_state
from .render import render_dashboard


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a Grocery Flywheel dashboard.")
    parser.add_argument("state", type=Path, help="Path to replenishment state JSON.")
    parser.add_argument("--output", "-o", type=Path, required=True, help="HTML output path.")
    args = parser.parse_args()

    state = json.loads(args.state.read_text())
    analysis = analyze_state(state)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_dashboard(analysis))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
