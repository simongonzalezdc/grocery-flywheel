from __future__ import annotations

import argparse
from pathlib import Path

from .core import analyze_state
from .render import render_dashboard
from .state_io import load_state, render_to_file


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Render a Grocery Flywheel dashboard.")
    parser.add_argument("state", type=Path, help="Path to replenishment state JSON.")
    parser.add_argument("--output", "-o", type=Path, required=True, help="HTML output path.")
    args = parser.parse_args(argv)

    state = load_state(args.state)
    analysis = analyze_state(state)
    target = render_to_file(render_dashboard(analysis), args.output)
    print(f"wrote {target}")


if __name__ == "__main__":
    main()
