"""grocery_flywheel.freshness — small helpers for surfacing data-freshness signals.

The dashboard uses these to show how confident we are in prices and sourcing
research. The point is not to enforce a freshness policy; it is to make the
user notice when data is going stale so they can either refresh it or
downgrade confidence.
"""

from __future__ import annotations

from datetime import date
from typing import Any

STALE_DAYS = 7


def age_in_days(checked: str | None, *, today: date) -> int | None:
    if not checked:
        return None
    try:
        return (today - date.fromisoformat(checked)).days
    except (TypeError, ValueError):
        return None


def is_stale(age_days: int | None) -> bool:
    if age_days is None:
        return True
    return age_days >= STALE_DAYS


def freshness_badge(age_days: int | None) -> str:
    if age_days is None:
        return "unknown"
    if age_days == 0:
        return "today"
    return f"{age_days}d ago"


def item_freshness(item: dict[str, Any], *, today: date) -> dict[str, Any]:
    """Return a small dict describing how fresh an item's pricing is."""
    pricing_status = item.get("pricing_status", "priced")
    last_check = item.get("last_price_check") or item.get("added_on")
    age = age_in_days(last_check, today=today)
    stale = is_stale(age) or pricing_status == "unknown"

    if pricing_status == "unknown":
        reason = "unpriced top-up"
    elif pricing_status == "gift":
        reason = "gift (price optional)"
    elif stale:
        reason = "priced but stale"
    else:
        reason = "priced recently"

    return {
        "name": item.get("name", ""),
        "pricing_status": pricing_status,
        "age_label": freshness_badge(age),
        "pricing_stale": stale,
        "reason": reason,
    }


def sourcing_freshness(row: dict[str, Any], *, today: date) -> dict[str, Any]:
    """Return a small dict describing how fresh a sourcing research row is."""
    alternatives = row.get("alternatives", []) or []
    last_check = alternatives[0].get("checked_date") if alternatives else None
    age = age_in_days(last_check, today=today)
    return {
        "item": row.get("item", ""),
        "age_label": freshness_badge(age),
        "stale": is_stale(age),
    }
