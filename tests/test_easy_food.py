"""Tests for grocery_flywheel.easy_food — surface unopened easy-food top-ups."""

from __future__ import annotations

from datetime import date, timedelta

from grocery_flywheel.easy_food import easy_food_summary, render_easy_food


def _state_with(items):
    return {
        "as_of": "2026-06-06",
        "items": items,
    }


def test_easy_food_surfaces_unopened_topups():
    today = date(2026, 6, 6)
    added = (today - timedelta(days=8)).isoformat()
    items = [
        {"name": "Costco pizza 4-pack", "role": "bridge_food", "storage": "frozen",
         "consumed_fraction": 0, "notes": "Unopened as of follow-up pulse.", "added_on": added},
        {"name": "Costco tofu 4-pack", "role": "protein", "storage": "fridge",
         "consumed_fraction": 0, "notes": "Unopened as of follow-up pulse.", "added_on": added},
    ]
    s = easy_food_summary(_state_with(items), today=today)
    assert s["unopened_count"] == 2
    assert any(x["name"] == "Costco pizza 4-pack" for x in s["unopened"])


def test_easy_food_excludes_already_opened():
    today = date(2026, 6, 6)
    added = (today - timedelta(days=3)).isoformat()
    items = [
        {"name": "Costco chicken bakes box", "role": "bridge_food", "storage": "frozen",
         "consumed_fraction": 0.82, "notes": "Most chicken bakes eaten, ~2 left.", "added_on": added},
        {"name": "Costco pizza 4-pack", "role": "bridge_food", "storage": "frozen",
         "consumed_fraction": 0, "notes": "Unopened as of follow-up pulse.", "added_on": added},
    ]
    s = easy_food_summary(_state_with(items), today=today)
    assert s["unopened_count"] == 1
    assert s["unopened"][0]["name"] == "Costco pizza 4-pack"


def test_render_easy_food_returns_suggestion_text():
    today = date(2026, 6, 6)
    added = (today - timedelta(days=14)).isoformat()
    s = easy_food_summary(_state_with([
        {"name": "Costco pizza 4-pack", "role": "bridge_food", "storage": "frozen",
         "consumed_fraction": 0, "notes": "Unopened.", "added_on": added}
    ]), today=today)
    html = render_easy_food(s)
    assert "Costco pizza 4-pack" in html
    assert "use it" in html.lower() or "open" in html.lower()
