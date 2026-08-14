"""The 30-second quick start, verified end-to-end in CI.

Exercises the exact path the README promises, via the installed console
scripts (which is what pipx/uv invoke): render the bundled sample, import
both fixture formats, and check dietary safety — every command a brand-new
user runs in their first minute.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _script(name: str) -> str:
    """Resolve a console script: on PATH (CI) or next to this interpreter (venv)."""
    found = shutil.which(name)
    if found:
        return found
    beside = Path(sys.executable).parent / name
    assert beside.exists(), (
        f"console script {name} not found on PATH or in {Path(sys.executable).parent}; "
        "is the package installed?"
    )
    return str(beside)


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, timeout=120)


def test_console_scripts_exist():
    for script in ("grocery-flywheel", "grocery-flywheel-mcp",
                   "grocery-flywheel-capture-visit"):
        probe = _run(_script(script), "--help")
        assert probe.returncode == 0, f"{script} --help failed: {probe.stderr}"


def test_thirty_second_first_look(tmp_path: Path):
    out = tmp_path / "dist" / "dashboard.html"
    result = _run(_script("grocery-flywheel"),
                  str(REPO_ROOT / "examples" / "sample_state.json"),
                  "--output", str(out))
    assert result.returncode == 0, result.stderr
    html = out.read_text()
    assert len(html) > 5000 and html.startswith("<!doctype html>")
    assert "Grocery Flywheel" in html and "color-scheme: dark" in html


def test_import_both_fixture_formats(tmp_path: Path):
    normalized = tmp_path / "state.json"
    r1 = _run(_script("grocery-flywheel"), "import", "normalized",
              str(REPO_ROOT / "examples" / "imports" / "example-history.json"),
              "--output", str(normalized))
    assert r1.returncode == 0, r1.stderr
    assert json.loads(normalized.read_text())["schema_version"] == "2026-08-14.mvp2"

    csv_out = tmp_path / "state.csv.json"
    r2 = _run(_script("grocery-flywheel"), "import", "csv",
              str(REPO_ROOT / "examples" / "imports" / "example-history.csv"),
              "--output", str(csv_out))
    assert r2.returncode == 0, r2.stderr
    assert json.loads(csv_out.read_text())["items"]


def test_docs_link_check_passes():
    result = _run(sys.executable, str(REPO_ROOT / "scripts" / "check_docs_links.py"))
    assert result.returncode == 0, result.stdout + result.stderr
