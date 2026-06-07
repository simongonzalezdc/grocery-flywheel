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

def test_dashboard_command_writes_updated_html(tmp_path):
    out = tmp_path / "dashboard.html"
    result = run_cli("--state", "examples/sample_state.json", "dashboard", "--output", str(out), "--no-open")

    assert result.returncode == 0
    html = out.read_text()
    assert "2026-06-06" in html
    assert "Costco tofu 4-pack" in html
    assert "Family-gifted nuggets box" in html
    assert "Brown sugar half-size bag" in html
    assert "Written to" in result.stdout
