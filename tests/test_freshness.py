"""Tests for grocery_flywheel.freshness — data-freshness signals on items and sourcing research."""

from __future__ import annotations

from datetime import date, timedelta

from grocery_flywheel.freshness import (
    age_in_days,
    freshness_badge,
    is_stale,
    item_freshness,
    sourcing_freshness,
)


def test_age_in_days_handles_missing():
    assert age_in_days(None, today=date(2026, 6, 6)) is None
    assert age_in_days("2026-06-01", today=date(2026, 6, 6)) == 5
    assert age_in_days("2026-06-06", today=date(2026, 6, 6)) == 0


def test_is_stale_thresholds():
    assert is_stale(0) is False
    assert is_stale(6) is False
    assert is_stale(7) is True
    assert is_stale(30) is True
    assert is_stale(None) is True


def test_freshness_badge_text():
    assert freshness_badge(0) == "today"
    assert freshness_badge(3) == "3d ago"
    assert freshness_badge(None) == "unknown"


def test_item_freshness_unpriced_marks_stale():
    item = {
        "name": "Costco tofu 4-pack",
        "source": "Costco top-up",
        "pricing_status": "unknown",
        "last_price_check": None,
        "added_on": "2026-06-01",
    }
    info = item_freshness(item, today=date(2026, 6, 6))
    assert info["pricing_stale"] is True
    assert info["age_label"] == "5d ago"
    assert info["reason"] == "unpriced top-up"


def test_item_freshness_priced_recent_is_fresh():
    item = {
        "name": "Calrose rice 20 lb",
        "source": "Vons baseline",
        "pricing_status": "priced",
        "last_price_check": "2026-06-05",
        "added_on": "2026-05-20",
    }
    info = item_freshness(item, today=date(2026, 6, 6))
    assert info["pricing_stale"] is False
    assert info["reason"] == "priced recently"


def test_sourcing_freshness_flags_old_research():
    row = {
        "item": "Cafe Bustelo bricks",
        "alternatives": [
            {"checked_date": "2026-05-20", "unit_price": 0.596}
        ],
    }
    info = sourcing_freshness(row, today=date(2026, 6, 6))
    assert info["stale"] is True
    assert info["age_label"] == "17d ago"


def test_sourcing_freshness_fresh_when_recent():
    row = {
        "item": "Dish soap",
        "alternatives": [{"checked_date": "2026-06-05", "unit_price": 0.12}],
    }
    info = sourcing_freshness(row, today=date(2026, 6, 6))
    assert info["stale"] is False
    assert info["age_label"] == "1d ago"
