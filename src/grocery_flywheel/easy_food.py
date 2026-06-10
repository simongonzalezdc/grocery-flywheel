"""grocery_flywheel.easy_food — surface unopened top-ups before they expire.

The flywheel knows which items the user bought as a top-up, how much of
each has been consumed, and when the item entered the run. The easy-food
panel surfaces items that are still unopened (or barely used) so the
user can rotate them into meals before the next top-up duplicates the
stock, or before a perishable goes past its window.

The matching rules are intentionally narrow:

- Item role must be ``bridge_food`` or ``protein`` (cooking-lane
  items are not easy food and are out of scope here).
- Item must not be a baseline order item — we identify baseline items
  by the absence of an ``added_on`` field, or by ``source == "baseline"``
  when the state records one.
- Consumed fraction must be 0.0 (or ``units_remaining == units_total``).
- ``added_on`` must be within the last 30 days. Beyond that, the
  item is no longer a fresh top-up.

This is the visible surface of two Meta Patterns:
- Pattern 4 (Friction Budget): the user benefits from noticing
  low-friction food before it duplicates effort.
- Pattern 6 (Bridge Inventory): immediate food is the bridge between
  full cooking days; an unopened bridge is wasted runway.
"""

from __future__ import annotations

from datetime import date, datetime
from html import escape
from typing import Any

EASY_FOOD_ROLES = {"bridge_food", "protein"}
EASY_FOOD_WINDOW_DAYS = 30
EASY_FOOD_MAX_CONSUMED = 0.10  # treat anything <= 10% as effectively unopened


def _age_days(added_on: Any, today: date) -> int | None:
    if not added_on or not isinstance(added_on, str):
        return None
    try:
        return (today - date.fromisoformat(added_on)).days
    except ValueError:
        # Try full ISO datetime
        try:
            return (today - datetime.fromisoformat(added_on).date()).days
        except ValueError:
            return None


def _consumed_fraction(item: dict[str, Any]) -> float:
    """Return the best-known consumed fraction for a top-up item."""
    if "consumed_fraction" in item and item["consumed_fraction"] is not None:
        return float(item["consumed_fraction"])
    total = item.get("units_total")
    remaining = item.get("units_remaining")
    if total not in (None, 0) and remaining is not None:
        return max(0.0, min(1.0, (float(total) - float(remaining)) / float(total)))
    return 0.0


def _is_baseline(item: dict[str, Any]) -> bool:
    """Baseline items came in on the original order, not as a top-up.

    The signal is the presence of ``added_on``: a top-up is any item with
    a recorded entry date. Baseline items do not have one. This is
    deliberately a presence test, not a value test, so a user can store
    whatever string they want in ``source`` (e.g. ``Vons baseline``) and
    the easy-food matcher still works.
    """
    return "added_on" not in item


def easy_food_summary(
    state: dict[str, Any],
    *,
    today: date,
    window_days: int = EASY_FOOD_WINDOW_DAYS,
) -> dict[str, Any]:
    """Return a small dict describing the unopened top-ups in the run.

    The dict has ``count`` and ``items`` (each with name, role, age_label).
    Used by the dashboard to render a rotation panel.
    """
    rows: list[dict[str, Any]] = []
    for item in state.get("items", []):
        role = item.get("role")
        if role not in EASY_FOOD_ROLES:
            continue
        if _is_baseline(item):
            continue
        if _consumed_fraction(item) > EASY_FOOD_MAX_CONSUMED:
            continue
        age = _age_days(item.get("added_on"), today)
        if age is None or age > window_days:
            continue
        rows.append({
            "name": item.get("name", ""),
            "role": role,
            "age_label": "today" if age == 0 else f"{age}d ago",
        })
    rows.sort(key=lambda r: r["age_label"])
    return {"count": len(rows), "items": rows}


def render_easy_food(summary: dict[str, Any]) -> str:
    """Render the easy-food summary as an HTML panel body."""
    if not summary or summary.get("count", 0) == 0:
        return "<p class='muted'>No unopened top-ups in the easy-food window.</p>"
    items = summary["items"]
    parts = [f"<p><strong>{summary['count']} unopened top-up(s):</strong></p><ul>"]
    for row in items:
        parts.append(
            f"<li><strong>{escape(str(row['name']))}</strong> "
            f"({escape(str(row['role']))}, {escape(str(row['age_label']))}) — "
            f"rotate into a meal before the next top-up duplicates it.</li>"
        )
    parts.append("</ul>")
    return "".join(parts)
