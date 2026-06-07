"""grocery_flywheel.cost_log — record visit time, amortized cost, and purchases.

The point is to make the ROI of the flywheel provable: without these numbers
we have runway, not savings. Visits are appended to `state['visits']`; each
visit has a list of purchases linked by `visit_id`.
"""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import date
from typing import Any


VISIT_TYPES = {"vons_pickup", "vons_delivery", "costco", "online_order", "quick_store", "other"}


def add_visit(
    state: dict[str, Any],
    *,
    date: str,
    visit_type: str,
    duration_min: int,
    amortized_cost: float = 0.0,
    notes: str = "",
) -> dict[str, Any]:
    if visit_type not in VISIT_TYPES:
        raise ValueError(f"unknown visit type: {visit_type!r}; expected one of {sorted(VISIT_TYPES)}")
    if duration_min < 0:
        raise ValueError("duration_min must be >= 0")
    visit: dict[str, Any] = {
        "id": uuid.uuid4().hex[:8],
        "date": date,
        "type": visit_type,
        "duration_min": int(duration_min),
        "amortized_cost": float(amortized_cost),
        "notes": notes,
        "purchases": [],
    }
    state.setdefault("visits", []).append(visit)
    state["as_of"] = date
    return visit


def add_purchase(
    state: dict[str, Any],
    *,
    visit_id: str,
    name: str,
    price: float,
    category: str = "",
    source: str = "",
    pricing_status: str = "priced",
) -> dict[str, Any]:
    if price < 0:
        raise ValueError("price must be >= 0")
    visit = _find_visit(state, visit_id)
    purchase = {
        "name": name,
        "price": float(price),
        "category": category,
        "source": source,
        "pricing_status": pricing_status,
    }
    visit.setdefault("purchases", []).append(purchase)
    return purchase


def _find_visit(state: dict[str, Any], visit_id: str) -> dict[str, Any]:
    for v in state.get("visits", []):
        if v.get("id") == visit_id:
            return v
    raise KeyError(f"visit not found: {visit_id}")


def visits_summary(state: dict[str, Any]) -> dict[str, Any]:
    """Aggregate total spend, total time, and per-type breakdown."""
    visits = state.get("visits", [])
    total_duration = sum(int(v.get("duration_min", 0)) for v in visits)
    total_spend = 0.0
    total_amortized = 0.0
    by_type: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"visit_count": 0, "spend": 0.0, "duration_min": 0, "amortized_cost": 0.0}
    )
    for v in visits:
        v_spend = sum(float(p.get("price", 0)) for p in v.get("purchases", []))
        total_spend += v_spend
        total_amortized += float(v.get("amortized_cost", 0))
        bucket = by_type[v.get("type", "other")]
        bucket["visit_count"] += 1
        bucket["spend"] += v_spend
        bucket["duration_min"] += int(v.get("duration_min", 0))
        bucket["amortized_cost"] += float(v.get("amortized_cost", 0))
    return {
        "visit_count": len(visits),
        "total_duration_min": total_duration,
        "total_spend": round(total_spend, 2),
        "total_amortized_cost": round(total_amortized, 2),
        "by_type": {k: {kk: (round(vv, 2) if isinstance(vv, float) else vv) for kk, vv in row.items()} for k, row in by_type.items()},
    }
