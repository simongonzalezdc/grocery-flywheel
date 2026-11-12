"""Round-9 contracts: instruction-safe export, one brick meaning, hero and ledger craft.

The r8 review found the export's top-level row still carried
``engine_action: "restock"`` (the guard only scanned ``display_action``), a
drawdown bar painted brick at >=80%, the hero action below two paragraphs, and
a ledger Price column that wrapped over three lines. Each test below binds one
of those to the renderer or the export.
"""

from __future__ import annotations

import json
import re

from grocery_flywheel.core import analyze_state
from grocery_flywheel.render import render_dashboard
from grocery_flywheel.rendering.panels import _draft_payload
from test_dashboard_round7 import mixed_state, sample_state

ACTION_KEYS = ("display_action", "engine_action", "action", "instruction",
               "buy", "restock")
BUY = re.compile(r"^(?!(?:do not|hold)\b).*\b(?:restock|rotate|buy|purchase)\b", re.I)


def _action_violations(node: object, path: str = "export") -> list[str]:
    if isinstance(node, dict):
        found = []
        for key in ACTION_KEYS:
            value = node.get(key)
            if isinstance(value, str) and BUY.search(value) and node.get("cleared") is not True:
                found.append(f"{path}:{key}")
        for key, value in node.items():
            found.extend(_action_violations(value, f"{path}.{key}"))
        return found
    if isinstance(node, list):
        return [hit for index, value in enumerate(node)
                for hit in _action_violations(value, f"{path}[{index}]")]
    return []


# --- B1: the export is instruction-safe by construction -------------------

def test_export_items_never_carry_the_raw_engine_action():
    a = analyze_state(mixed_state())
    draft = _draft_payload(a, a["cart_plan"])
    assert draft["items"]
    for row in draft["items"]:
        assert "engine_action" not in row
    # The engine plan survives verbatim under its own key, last in the file.
    assert draft["engine_plan"] == a["cart_plan"]
    assert list(draft)[-1] == "engine_plan"
    assert list(draft).index("items") < list(draft).index("engine_plan")


def test_guard_catches_both_the_r7_and_r8_shapes():
    assert _action_violations(
        {"items": [{"display_action": "Restock", "cleared": False}]}
    ) == ["export.items[0]:display_action"]
    assert _action_violations(
        {"items": [{"display_action": "Hold restock", "engine_action": "restock",
                    "cleared": False}]}
    ) == ["export.items[0]:engine_action"]
    # And the current payload is clean outside the reference block.
    a = analyze_state(mixed_state())
    draft = _draft_payload(a, a["cart_plan"])
    scope = {key: value for key, value in draft.items() if key != "engine_plan"}
    assert _action_violations(scope) == []


def test_serialized_export_meets_items_before_the_engine_plan():
    draft = _draft_payload(analyze_state(mixed_state()), analyze_state(mixed_state())["cart_plan"])
    text = json.dumps(draft, sort_keys=False)
    assert text.index('"items"') < text.index('"items_note"')
    assert text.index('"items_note"') < text.index('"engine_plan_note"')
    assert text.index('"engine_plan_note"') < text.index('"engine_plan"')


def test_export_documents_both_hold_flags():
    draft = _draft_payload(analyze_state(mixed_state()), analyze_state(mixed_state())["cart_plan"])
    note = draft["items_note"]
    assert "hold=true means do not buy" in note
    assert "held_out_of_plan=true" in note
    assert "subset of hold" in note


# --- B2: brick is dietary evidence only -----------------------------------

def test_drawdown_bars_never_use_the_brick_token():
    markup = render_dashboard(analyze_state(sample_state()))
    css = markup.split("<style>")[1].split("</style>")[0]
    assert ".bar.hot" not in css
    assert ".bar > span { display:block; height:100%; background:var(--copper); }" in css
    assert "class='bar hot'" not in markup
    # A >=80% drawdown still renders the bar, with its percentage in text.
    assert "data-pct='100'" in markup


# --- Design F1/F2/F3: hero order and ledger craft -------------------------

def test_hero_puts_the_action_under_the_counts_and_demotes_the_paragraph():
    markup = render_dashboard(analyze_state(mixed_state()))
    panel = markup.split("class='attention-body'")[1].split("</article>")[0]
    counts = panel.index("class='attention-counts'")
    jump = panel.index("class='jump-link'")
    qualifier = panel.index("class='attention-qualifier'")
    support = panel.index("class='attention-support'")
    assert counts < jump < qualifier < support
    css = markup.split("<style>")[1].split("</style>")[0]
    assert ".jump-link {" in css and "font-size:var(--step-1)" in css
    assert ".attention-support { font-size:var(--step--1)" in css
    assert "align-items:center" in css.split(".attention-body {", 1)[1].split("}", 1)[0]


def test_sticky_banner_does_not_repeat_the_verdict_at_1440():
    markup = render_dashboard(analyze_state(mixed_state()))
    css = markup.split("<style>")[1].split("</style>")[0]
    assert "@media (min-width:1440px)" in css
    block = css.split("@media (min-width:1440px)", 1)[1].split("}", 1)[0]
    assert ".masthead-status .status-verdict { display:none;" in block
    # The compact counts and the full sentence are both present for narrower
    # viewports, where the banner is the only visible verdict.
    assert "class='status-compact'" in markup and "class='status-verdict'" in markup


def test_ledger_spends_and_prices_align_and_price_is_widened():
    markup = render_dashboard(analyze_state(sample_state()))
    ledger = markup.split("The ledger</h2>")[1].split("</article>")[0]
    assert "<col style='width:26%'><col style='width:13%'><col style='width:23%'>" in ledger
    assert "<th class='money-col'>Spend</th><th class='money-col'>Price</th>" in ledger
    assert "<td class='money-col' data-label=" in ledger
    css = markup.split("<style>")[1].split("</style>")[0]
    assert ".money-col, th.money-col { text-align:right; }" in css
    assert "Price · date unknown" in markup


def test_long_names_clamp_and_disclose_the_full_string():
    a = analyze_state(sample_state())
    long_name = "Sanitized long item " + "x" * 300
    a["items"][0]["name"] = long_name
    markup = render_dashboard(a)
    assert "<span class='clamp-2'>" in markup
    assert "Sanitized long item " in markup
    css = markup.split("<style>")[1].split("</style>")[0]
    assert "-webkit-line-clamp:2" in css
