"""grocery_flywheel.easy_food — surface unopened easy-food top-ups.

The flywheel's real product win is preventing the "nothing to eat" moment by
rotating through unopened easy food. This module finds the items that look
easy (bridge_food, frozen, protein) but have not been touched, and surfaces
them so the dashboard can prompt rotation.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from html import escape as _escape

EASY_ROLES = {"bridge_food", "protein"}
# Easy food = unopened top-up that can replace a delivery decision.
# Includes frozen easy food and unopened refrigerated protein like tofu.
EASY_STORAGE = {"frozen", "fridge"}
UNOPENED_THRESHOLD = 0.0  # any non-zero consumption counts as "started"


def _added_date(item: dict[str, Any]) -> date | None:
    raw = item.get("added_on") or item.get("last_price_check")
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except (TypeError, ValueError):
        return None


def easy_food_summary(state: dict[str, Any], *, today: date | None = None) -> dict[str, Any]:
    """Accept either a raw state or an analysis dict (which has 'items' and 'as_of')."""
    today = today or date.fromisoformat(state.get("as_of", date.today().isoformat()))
    unopened = []
    for item in state.get("items", []):
        role = item.get("role", "")
        storage = item.get("storage", "")
        consumed = float(item.get("consumed_fraction", 0) or 0)
        # Heuristic: easy food = bridge_food or protein in frozen storage that hasn't been touched.
        if role in EASY_ROLES and storage in EASY_STORAGE and consumed <= UNOPENED_THRESHOLD:
            added = _added_date(item)
            age_days = (today - added).days if added else None
            unopened.append({
                "name": item.get("name", ""),
                "role": role,
                "added_on": added.isoformat() if added else None,
                "age_days": age_days,
                "notes": item.get("notes", ""),
            })
    # Oldest first so the most-overlooked item is at the top.
    unopened.sort(key=lambda x: x["age_days"] if x["age_days"] is not None else 9999, reverse=True)
    return {
        "unopened_count": len(unopened),
        "unopened": unopened[:6],
    }


def render_easy_food(summary: dict[str, Any]) -> str:
    if summary["unopened_count"] == 0:
        return "<p class='muted'>No unopened easy-food top-ups. Rotate in the freezer / fridge if you want to use them before they lose quality.</p>"
    items = summary["unopened"]
    bullets = "".join(
        f"<li><strong>{_escape(i['name'])}</strong>"
        + (f" (added {i['age_days']}d ago)" if i["age_days"] is not None else "")
        + f": open one before the next Costco run to use it before the easy-food window narrows.</li>"
        for i in items
    )
    return (
        f"<p><strong>{summary['unopened_count']} unopened easy-food items:</strong></p>"
        f"<ul>{bullets}</ul>"
        f"<p class='muted'>Tip: rotate through these before defaulting to delivery.</p>"
    )
