"""Shared state file and artifact IO.

The CLI and the MCP render tool previously each carried their own
read-state / mkdir / write-HTML sequence. One home here, so a fix to
artifact writing (permissions, parents, encoding) lands once.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_state(path: str | Path) -> dict[str, Any]:
    """Read and parse a state JSON file (lenient: no schema enforcement)."""
    return json.loads(Path(path).read_text())


def render_to_file(html: str, output_path: str | Path) -> Path:
    """Write a rendered artifact, creating parent directories.

    Returns the resolved path so callers can report it uniformly.
    """
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html)
    return target
