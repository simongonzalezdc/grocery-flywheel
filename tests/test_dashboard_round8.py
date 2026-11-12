"""Round-8 contracts: one instruction collection, honest hold flags and anchors.

The r7 review found the download's top-level engine ``items[]`` still carried a
plain restock on a needs-review row while the held peanut item was absent, the
sticky banner covered the jump and skip targets, the five-state legend defined
"Not evaluated" with the clearance's own wording, and a ``held:false`` row read
"Hold restock". Each test below binds one of those to the page or the export.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from grocery_flywheel.core import analyze_state
from grocery_flywheel.render import render_dashboard
from grocery_flywheel.rendering.panels import (
    _action_rows,
    _dietary_context,
    _draft_payload,
    _role_rows,
)
from test_dashboard_round7 import mixed_state, sample_state

ROOT = Path(__file__).resolve().parents[1]
BUY_VERB = re.compile(
    r"^(?!(?:do not|hold)\b).*\b(?:restock|rotate|buy|purchase)\b", re.I)
# Every key that can carry an action token. The r8 blocker was a guard that
# scanned only ``display_action`` while ``engine_action`` still said "restock".
ACTION_KEYS = ("display_action", "engine_action", "action", "instruction",
               "buy", "restock")


def visible(markup: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", markup, flags=re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)))


def _violations(node: object, path: str = "export") -> list[str]:
    """Every dictionary that carries a buy instruction without ``cleared``.

    Scans every action-bearing key, not just ``display_action`` (r8 B1).
    """
    if isinstance(node, dict):
        out: list[str] = []
        for key in ACTION_KEYS:
            action = node.get(key)
            if (isinstance(action, str) and BUY_VERB.search(action)
                    and node.get("cleared") is not True):
                out.append(f"{path}:{key}")
        for key, value in node.items():
            out.extend(_violations(value, f"{path}.{key}"))
        return out
    if isinstance(node, list):
        out = []
        for index, value in enumerate(node):
            out.extend(_violations(value, f"{path}[{index}]"))
        return out
    return []


# --- blocker: the download's top level is the action list -----------------

def test_top_level_items_is_the_only_instruction_collection():
    a = analyze_state(mixed_state())
    draft = _draft_payload(a, a["cart_plan"])

    assert draft["schema"] == "grocery-flywheel.dashboard-draft/2"
    assert "presentation" not in draft
    assert draft["engine_plan"] == a["cart_plan"]
    raw = {row["item"]: row for row in draft["engine_plan"]["items"]}
    assert raw["Rising crust pizza"]["action"] == "restock"
    assert "Homestyle waffles" not in raw
    action = {row["item"]: row for row in draft["items"]}
    assert action["Rising crust pizza"]["display_action"] == "Hold restock"
    assert action["Rising crust pizza"]["hold"] is True
    assert action["Rising crust pizza"]["held_out_of_plan"] is False
    assert action["Homestyle waffles"]["hold"] is True
    assert action["Homestyle waffles"]["held_out_of_plan"] is True
    assert action["Homestyle waffles"]["display_action"] == "Do not buy"
    # Instruction-safe by construction: the raw engine token is not copied into
    # the action collection (r8 B1).
    assert all("engine_action" not in row for row in draft["items"])


def test_engine_plan_serializes_last_after_the_authoritative_list():
    a = analyze_state(mixed_state())
    draft = _draft_payload(a, a["cart_plan"])
    keys = list(draft)
    assert keys.index("items") < keys.index("items_note")
    assert keys.index("items_note") < keys.index("engine_plan_note")
    assert keys.index("engine_plan_note") < keys.index("engine_plan")
    assert keys[-1] == "engine_plan"
    serialized = __import__("json").dumps(draft, sort_keys=False)
    assert serialized.index('"items"') < serialized.index('"engine_plan"')


def test_no_action_bearing_entry_outside_the_engine_plan_carries_a_buy_instruction():
    a = analyze_state(mixed_state())
    draft = _draft_payload(a, a["cart_plan"])
    scope = {key: value for key, value in draft.items() if key != "engine_plan"}

    assert _violations(scope) == []
    # Positive controls: the guard catches the r7 shape and the r8 engine_action
    # shape, whichever key carries the instruction.
    assert _violations({"items": [{"item": "x", "display_action": "Restock",
                                   "cleared": False}]}) == ["export.items[0]:display_action"]
    assert _violations({"items": [{"item": "x", "display_action": "Hold restock",
                                   "engine_action": "restock",
                                   "cleared": False}]}) == ["export.items[0]:engine_action"]
    assert _violations({"items": [{"item": "x", "action": "buy",
                                   "cleared": False}]}) == ["export.items[0]:action"]


def test_every_non_cleared_action_row_carries_hold_and_a_qualifier():
    a = analyze_state(mixed_state())
    rows, _verdict = _action_rows(a)

    assert rows
    for row in rows:
        assert row["hold"] is (not row["cleared"]), row
        if not row["cleared"]:
            assert row["qualifier"], row
            assert not BUY_VERB.search(row["display_action"]), row
    assert [row["item"] for row in rows if row["cleared"]] == ["Bean and cheese burritos"]


def test_action_counts_match_the_collections_they_name():
    a = analyze_state(mixed_state())
    draft = _draft_payload(a, a["cart_plan"])
    context = draft["dietary_context"]

    assert context["action_items_total"] == len(draft["items"]) == 5
    assert context["engine_plan_items_total"] == len(draft["engine_plan"]["items"]) == 4
    assert "cart_items_total" not in context


# --- major: legend wording -------------------------------------------------

def test_legend_states_the_orphan_case_not_the_clearance_case():
    a = analyze_state(mixed_state())
    markup = render_dashboard(a)
    legend = markup.split("class='state-legend'")[1]
    assert "named no item on this page" in legend
    assert "evidence that did not match" not in legend

    context = _dietary_context(a)
    meaning = context["state_legend"]["not_evaluated"]["meaning"]
    assert "named no item on this page" in meaning
    assert "evidence that did not match" not in meaning
    assert meaning == next(
        row for row in re.findall(r"<dd>(.*?)</dd>", legend) if "named no item" in row)


# --- majors and minors: vocabulary, counts and anchors ---------------------

def test_action_rows_use_the_page_source_vocabulary():
    a = analyze_state(sample_state())
    rows, _verdict = _action_rows(a)
    sources = {row["source"] for row in rows if row["engine_action"] == "restock"}
    assert sources == {"your usual store"}
    raw = {row["item"]: row for row in a["cart_plan"]["items"]}
    assert raw["Rising crust pizza"]["source"] == "normal store"


def test_role_rows_add_to_the_figure_the_runway_prints():
    a = analyze_state(sample_state())
    rows = _role_rows(a)
    engine = {row["role"]: row["consumed"] for row in a["role_summary"]}
    assert sum(round(float(row["consumed"]) * 100) for row in rows) == round(
        float(a["consumed_value"]) * 100)
    for row in rows:
        assert abs(round(float(row["consumed"]) * 100)
                   - round(engine[row["role"]] * 100)) <= 1


def test_layout_offsets_clear_the_sticky_banner_and_stack_wide_tables():
    layout = (ROOT / "src/grocery_flywheel/rendering/layout.py").read_text()
    assert "#today, #household-review { scroll-margin-top:6.5rem; }" in layout
    assert "scroll-margin-top:9.5rem" in layout
    assert "@media (max-width:820px)" in layout
    assert "@media (max-width:700px)" not in layout


def test_action_heads_and_approval_copy_match_the_rows_they_describe():
    markup = render_dashboard(analyze_state(sample_state()))
    assert "Today &middot; before you shop" in markup
    assert "Every purchasable item needs your approval." in markup
    assert "Everything needs your approval" not in markup


def test_action_headline_counts_cleared_and_held_rows():
    mixed = visible(render_dashboard(analyze_state(mixed_state())))
    assert "5 items · 1 cleared · 4 need a decision" in mixed
    assert "Review the 4 items that need a decision" in mixed
    # One count vocabulary: the Today headline counts the rows that need a
    # decision, and explains the cleared row that is also listed (r8 major).
    assert "Review 4 items before your next shop." in mixed
    assert "The 1 cleared item is listed for reference." in mixed
    assert "Review 5 items" not in mixed
    sample = visible(render_dashboard(analyze_state(sample_state())))
    assert "4 items · none cleared" in sample
    assert "Review the 4 items that need a decision" in sample
    assert "Review 4 items before your next shop." in sample


def test_every_held_page_row_carries_the_same_marker():
    markup = render_dashboard(analyze_state(mixed_state()))
    today = markup.split("id='today'")[1].split("</article>")[0]
    held_rows = re.findall(r"<li class='action-hold' data-action-item='([^']+)'"
                           r" data-hold='true' data-held-out-of-plan='(true|false)'", today)
    assert dict(held_rows) == {
        "Homestyle waffles": "true",
        "Rising crust pizza": "false",
        "Espresso bricks": "false",
        "Dish soap": "false",
    }
    # A held row is never rendered without the marker, and the cleared row is
    # never marked held.
    assert today.count("data-hold='true'") == 4
    assert today.count("data-hold='false'") == 1


def test_savings_copy_separates_recorded_from_modelled():
    markup = render_dashboard(analyze_state(sample_state()))
    text = visible(markup)
    assert "Recorded savings" in text
    assert "not recorded savings" in text
    assert "Engine's headline move" in text
    assert "Best recorded move" not in text
    assert "unrounded unit prices" in text
    assert "14% modelled saving" in text or "modelled saving" in text
