"""Tests for grocery_flywheel.cost_log — record visit cost and emit a summary."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from grocery_flywheel.cost_log import (
    add_visit,
    add_purchase,
    visits_summary,
)


@pytest.fixture
def fresh_state():
    return {
        "as_of": "2026-06-06",
        "items": [],
        "visits": [],
    }


def test_add_visit_records_minimum_fields(fresh_state):
    v = add_visit(fresh_state, date="2026-06-06", visit_type="vons_pickup", duration_min=20)
    assert v["date"] == "2026-06-06"
    assert v["type"] == "vons_pickup"
    assert v["duration_min"] == 20
    assert v["amortized_cost"] == 0.0
    assert v["id"]
    assert fresh_state["visits"][0]["id"] == v["id"]


def test_add_visit_rejects_unknown_type(fresh_state):
    with pytest.raises(ValueError):
        add_visit(fresh_state, date="2026-06-06", visit_type="spaceship", duration_min=5)


def test_add_purchase_appends_to_visit_and_links_item(fresh_state):
    v = add_visit(fresh_state, date="2026-06-06", visit_type="costco", duration_min=45, amortized_cost=3.0)
    p = add_purchase(fresh_state, visit_id=v["id"], name="Costco tofu 4-pack", price=8.99, category="protein")
    assert p["name"] == "Costco tofu 4-pack"
    assert p["price"] == 8.99
    assert p["category"] == "protein"
    assert v["purchases"][0]["name"] == "Costco tofu 4-pack"


def test_add_purchase_rejects_unknown_visit(fresh_state):
    with pytest.raises(KeyError):
        add_purchase(fresh_state, visit_id="nope", name="x", price=1.0)


def test_visits_summary_totals_by_type(fresh_state):
    v1 = add_visit(fresh_state, date="2026-06-01", visit_type="vons_pickup", duration_min=15)
    add_purchase(fresh_state, visit_id=v1["id"], name="x", price=10.0, category="bridge_food")
    v2 = add_visit(fresh_state, date="2026-06-04", visit_type="costco", duration_min=60, amortized_cost=2.5)
    add_purchase(fresh_state, visit_id=v2["id"], name="y", price=20.0, category="protein")
    add_purchase(fresh_state, visit_id=v2["id"], name="z", price=5.0, category="paper_goods")

    s = visits_summary(fresh_state)
    assert s["visit_count"] == 2
    assert s["total_duration_min"] == 75
    assert s["total_spend"] == 35.0
    assert s["total_amortized_cost"] == 2.5
    assert s["by_type"]["vons_pickup"]["spend"] == 10.0
    assert s["by_type"]["costco"]["spend"] == 25.0
