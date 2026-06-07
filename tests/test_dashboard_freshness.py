"""Test that the dashboard surfaces data-freshness signals for unpriced items and stale sourcing research."""

import json
from datetime import date
from pathlib import Path

from grocery_flywheel.core import analyze_state
from grocery_flywheel.render import render_dashboard

ROOT = Path(__file__).resolve().parents[1]


def _mutate_state(state: dict) -> dict:
    """Add a few last_price_check dates to make freshness varied."""
    today = date(2026, 6, 6).isoformat()
    for item in state["items"]:
        if item.get("source") == "Costco top-up":
            item["last_price_check"] = "2026-06-01"  # 5 days old, but unpriced
        elif item.get("source") == "Vons baseline":
            item["last_price_check"] = "2026-06-05"  # 1 day old
        elif item.get("source") == "unclear top-up":
            item["last_price_check"] = None
        elif item.get("source") == "family gift":
            item["last_price_check"] = None
    # Make the Bustelo research row clearly stale
    for row in state.get("sourcing_research", []):
        if row.get("item") == "Cafe Bustelo bricks":
            for alt in row.get("alternatives", []):
                alt["checked_date"] = "2026-05-20"  # 17 days old
    return state


def test_dashboard_surfaces_freshness_signals():
    state = json.loads((ROOT / "examples" / "sample_state.json").read_text())
    state = _mutate_state(state)
    html = render_dashboard(analyze_state(state))

    assert "Data freshness" in html
    # Unpriced top-up should be flagged
    assert "unpriced top-up" in html
    # Sourcing row should show a stale badge
    assert "stale" in html
    # At least one row should be marked not-stale (recently priced)
    assert "priced recently" in html
