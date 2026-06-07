from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

from .freshness import summarize_freshness


def item_consumed_fraction(item: dict[str, Any]) -> float:
    """Return the best-known consumed fraction for an item."""
    if "remaining_fraction" in item and item["remaining_fraction"] is not None:
        return clamp(1.0 - float(item["remaining_fraction"]))

    total = item.get("units_total")
    remaining = item.get("units_remaining")
    if total not in (None, 0) and remaining is not None:
        return clamp((float(total) - float(remaining)) / float(total))

    if "consumed_fraction" in item and item["consumed_fraction"] is not None:
        return clamp(float(item["consumed_fraction"]))

    return 0.0


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def analyze_state(state: dict[str, Any]) -> dict[str, Any]:
    order = state["order"]
    items = state.get("items", [])
    order_total = float(order["total"])
    as_of = date.fromisoformat(state["as_of"])
    order_date = date.fromisoformat(order["date"])
    days_elapsed = max(1, (as_of - order_date).days)

    item_rows = []
    consumed_value = 0.0
    role_spend: dict[str, float] = defaultdict(float)
    role_consumed: dict[str, float] = defaultdict(float)

    for item in items:
        spend = float(item.get("spend", 0))
        role = str(item.get("role", "unknown"))
        consumed_fraction = item_consumed_fraction(item)
        consumed = spend * consumed_fraction
        consumed_value += consumed
        role_spend[role] += spend
        role_consumed[role] += consumed
        item_rows.append(
            {
                "name": item["name"],
                "role": role,
                "category": item.get("category", ""),
                "storage": item.get("storage", ""),
                "spend": spend,
                "consumed_fraction": consumed_fraction,
                "consumed_value": consumed,
                "notes": item.get("notes", ""),
                "pricing_status": item.get("pricing_status"),
                "last_price_check": item.get("last_price_check"),
                "added_on": item.get("added_on"),
            }
        )

    known_consumed_fraction = consumed_value / order_total if order_total else 0.0
    estimated_total_days = (
        round(days_elapsed / known_consumed_fraction, 1)
        if known_consumed_fraction > 0
        else None
    )
    estimated_days_remaining = (
        round(max(0.0, estimated_total_days - days_elapsed), 1)
        if estimated_total_days is not None
        else None
    )

    substitutions = sorted(
        state.get("substitutions", []),
        key=lambda row: substitution_score(row),
        reverse=True,
    )

    return {
        "order": order,
        "as_of": state["as_of"],
        "inventory_surface": state.get("inventory_surface", {}),
        "acquisition_channel": state.get("acquisition_channel", "unknown"),
        "days_elapsed": days_elapsed,
        "items": item_rows,
        "consumed_value": round(consumed_value, 2),
        "known_consumed_fraction": round(known_consumed_fraction, 4),
        "estimated_total_days": estimated_total_days,
        "estimated_days_remaining": estimated_days_remaining,
        "role_summary": summarize_roles(role_spend, role_consumed),
        "freshness": summarize_freshness(
            items, state.get("sourcing_research", []), today=as_of,
        ),
        "preferences": state.get("preferences", []),
        "dietary_profiles": state.get("dietary_profiles", []),
        "substitutions": substitutions,
        "sourcing_research": state.get("sourcing_research", []),
        "pulses": state.get("pulses", []),
    }


def substitution_score(row: dict[str, Any]) -> float:
    fit = row.get("fit", "")
    fit_bonus = {
        "better": 2.0,
        "better_if_storage_ok": 1.0,
        "same": 0.0,
        "worse": -2.0,
    }.get(fit, 0.0)
    current = float(row.get("current_unit_price", 0) or 0)
    candidate = float(row.get("candidate_unit_price", 0) or 0)
    unit_delta = current - candidate
    return fit_bonus + unit_delta


def summarize_roles(
    role_spend: dict[str, float], role_consumed: dict[str, float]
) -> list[dict[str, Any]]:
    rows = []
    for role in sorted(role_spend):
        spend = role_spend[role]
        consumed = role_consumed.get(role, 0.0)
        rows.append(
            {
                "role": role,
                "spend": round(spend, 2),
                "consumed": round(consumed, 2),
                "consumed_fraction": round(consumed / spend, 4) if spend else 0.0,
            }
        )
    return rows
