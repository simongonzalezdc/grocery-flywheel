"""Test that the dashboard surfaces the easy-food rotation panel."""
import json
from pathlib import Path

from grocery_flywheel.core import analyze_state
from grocery_flywheel.render import render_dashboard

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_surfaces_easy_food_panel():
    state = json.loads((ROOT / "examples" / "sample_state.json").read_text())
    html = render_dashboard(analyze_state(state))
    assert "Easy food" in html
    # At least one unopened Costco item should appear in the panel
    assert "Costco pizza 4-pack" in html or "Costco tofu 4-pack" in html
