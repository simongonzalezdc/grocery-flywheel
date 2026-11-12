"""Round-7 contracts: the download mirrors the page, and every surface reads
the same dietary authority.

The r6 committee found two fail-open surfaces on the artifact a household acts
on (the downloaded draft restocked an item the page held, and Easy Food told an
uncleared item to rotate) plus majors where a surface still decided for itself
(ledger caption from a raw result, one-row evidence drawer, substitution status
discarded, at-risk table diet-blind, exact-string join, stamped receipt
attributes, a mobile qualifier that shrank, a draft that covered ledger items
only). Each test below binds one of those to the page or the export.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from grocery_flywheel.core import analyze_state
from grocery_flywheel.render import render_dashboard
from grocery_flywheel.rendering.panels import (
    _action_text,
    _dietary_context,
    _dietary_mark,
    _dietary_verdict,
    _draft_payload,
    _easy_food,
    _item_verdict,
    _money,
    _norm_name,
    _price_bucket_text,
    _price_buckets,
    _substitution_verdict,
    _verdict_for,
)

ROOT = Path(__file__).resolve().parents[1]
MARK_RE = re.compile(r"<span class='mark ([a-z]+)'(.*?)>(.*?)</span>", re.S)


def sample_state() -> dict:
    return json.loads((ROOT / "examples" / "sample_state.json").read_text())


def mixed_state() -> dict:
    state = sample_state()
    state["dietary_profiles"] = [{
        "profile_id": "native-mixed",
        "label": "Sanitized household",
        "restrictions": [{"value": "peanut_allergy", "safety_tier": "critical",
                          "behavior": "block"}],
    }]
    checked = state["as_of"]
    state["items"][0]["product_evidence"] = [{
        "evidence_type": "label", "source": "sanitized label",
        "checked_date": checked, "ingredients": ["oats"],
        "allergen_statements": [], "certifications": []}]
    state["items"][1]["product_evidence"] = [{
        "evidence_type": "label", "source": "sanitized label",
        "checked_date": checked, "ingredients": ["oats and peanut"],
        "allergen_statements": ["peanut"], "certifications": []}]
    return state


def visible(markup: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", markup, flags=re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text))


def action_items(markup: str) -> list[str]:
    return [re.sub(r"\s+", " ", item).strip() for item in
            re.findall(r"<li[^>]*data-action-item='([^']*)'", markup)]


def cart_only_analysis() -> dict:
    """A cart row the ledger does not hold, with its own engine evaluation."""
    a = analyze_state(mixed_state())
    a["cart_plan"]["items"].append({
        "item": "Cart-only oats", "action": "restock", "source": "normal_store",
        "reason": "Depletion pace suggests a restock.", "approval_state": "needs_human_approval",
    })
    a["dietary_evaluations"].append({
        "item": "Cart-only oats", "result": "needs_review", "evidence_status": "missing",
        "safety_tier": "critical", "reason": "No label evidence on file.",
    })
    return a


# --- B1: the downloaded draft mirrors the action area ---------------------

def test_draft_action_list_mirrors_every_rendered_action_row():
    a = analyze_state(mixed_state())
    markup = render_dashboard(a)
    draft = _draft_payload(a, a["cart_plan"])
    action_list = draft["presentation"]["action_list"]

    assert action_items(markup) == [row["item"] for row in action_list]
    assert len(action_list) == 5
    waffles = next(row for row in action_list
                   if row["item"] == "Homestyle waffles")
    assert waffles["held"] is True and waffles["cleared"] is False
    assert waffles["display_action"] == "Do not buy"
    assert "blocked: Evidence matched: peanut" in waffles["qualifier"]
    pizza = next(row for row in action_list if row["item"] == "Rising crust pizza")
    assert pizza["cleared"] is False and pizza["display_action"] == "Hold restock"
    assert "resolve evidence first" in pizza["qualifier"]
    cleared = [row for row in action_list if row["cleared"]]
    assert [row["item"] for row in cleared] == ["Bean and cheese burritos"]
    assert cleared[0]["display_action"] == "Restock"


def test_draft_keeps_the_engine_cart_plan_verbatim_and_adds_the_page_view():
    a = analyze_state(mixed_state())
    draft = _draft_payload(a, a["cart_plan"])
    assert draft["items"] == a["cart_plan"]["items"]
    assert "Homestyle waffles" not in [row["item"] for row in draft["items"]]
    assert len(draft["presentation"]["action_list"]) == 5


def test_no_exported_action_can_restock_a_non_cleared_item():
    a = analyze_state(mixed_state())
    draft = _draft_payload(a, a["cart_plan"])
    for row in draft["presentation"]["action_list"]:
        assert row["cleared"] == (row["state"] == "cleared")
        if not row["cleared"]:
            assert row["display_action"] != "Restock"
            assert row["qualifier"], row


# --- B2: Easy Food and the sourcing sentence gate on the verdict ----------

def test_easy_food_only_tells_a_cleared_item_to_rotate():
    profile = {"profile_id": "p", "label": "P",
               "restrictions": [{"value": "avoid", "safety_tier": "preference",
                                 "behavior": "warn"}]}
    base = {"items": [{"name": "Soup"}], "dietary_profiles": [profile],
            "easy_food": {"count": 1, "items": [
                {"name": "Soup", "role": "bridge_food", "age_label": "2d ago"}]}}
    cleared = dict(base, dietary_evaluations=[{
        "item": "Soup", "result": "safe", "evidence_status": "current",
        "safety_tier": "preference", "reason": "No match."}])
    assert "rotate into a meal" in _easy_food(cleared)
    review = dict(base, dietary_evaluations=[{
        "item": "Soup", "result": "needs_review", "evidence_status": "missing",
        "safety_tier": "critical", "reason": "No label evidence."}])
    copy = _easy_food(review)
    assert "rotate into a meal" not in copy
    assert "do not rotate until current evidence clears it" in copy
    none = dict(base, dietary_evaluations=[])
    assert "do not rotate until a dietary evaluation clears it" in _easy_food(none)


def test_sourcing_best_move_carries_a_dietary_mark():
    a = analyze_state(sample_state())
    markup = render_dashboard(a)
    assert "Best recorded move" in visible(markup)
    segment = markup.split("Best recorded move", 1)[1][:700]
    assert "class='mark " in segment


# --- M1: ledger caption from the display state, not the raw result --------

def test_ledger_caption_never_says_cleared_from_a_raw_safe_result():
    a = analyze_state(mixed_state())
    for row in a["dietary_evaluations"]:
        row["result"] = "safe"
        row["evidence_status"] = "stale"
    markup = render_dashboard(a)
    ledger = markup.split("The ledger</h2>")[1].split("</article>")[0]
    caption = visible(ledger.split("<table", 1)[0])
    assert "Cleared" not in caption
    assert "Not evaluated" in caption


# --- M2: one row per engine evaluation ------------------------------------

def test_evidence_drawer_renders_every_evaluation_one_row_each():
    state = mixed_state()
    state["dietary_profiles"].append({
        "profile_id": "second", "label": "Second",
        "restrictions": [{"value": "example disliked ingredient",
                          "safety_tier": "preference", "behavior": "warn"}]})
    a = analyze_state(state)
    assert len(a["dietary_evaluations"]) == 26
    markup = render_dashboard(a)
    assert "26 dietary evaluations" in visible(markup)
    drawer = markup.split("See the evidence and the five-state legend", 1)[1]
    drawer = drawer.split("</details>", 1)[0]
    assert drawer.count("data-raw-result=") == 26
    assert "13 dietary evaluations" not in visible(markup)


def test_orphan_evaluation_is_still_rendered_and_never_clears():
    a = analyze_state(sample_state())
    a["dietary_evaluations"] = [{
        "item": "Not on this page", "result": "safe", "evidence_status": "current",
        "safety_tier": "preference", "reason": "No match."}]
    verdict = _dietary_verdict(a)
    assert len(verdict["orphans"]) == 1
    markup = render_dashboard(a)
    assert "data-orphan='true'" in markup
    assert "26 dietary evaluations" not in visible(markup)
    assert "1 dietary evaluation" in visible(markup)


# --- M3: substitutions keep the candidate's own engine state --------------

def test_substitution_verdict_reads_the_rows_own_engine_state():
    a = analyze_state(mixed_state())
    verdict = _dietary_verdict(a)
    blocked = _substitution_verdict(
        {"candidate": "Peanut granola", "dietary_status": "blocked",
         "evidence_status": "candidate_evidence_reviewed", "safety_tier": "critical"}, verdict)
    assert blocked["state"] == "blocked" and blocked["cleared"] is False
    missing = _substitution_verdict(
        {"candidate": "Oat bites", "dietary_status": "needs_review",
         "evidence_status": "missing_candidate_evidence", "safety_tier": "critical"}, verdict)
    assert missing["state"] == "needs_review"
    assert "No candidate evidence" in missing["detail"]
    current = _substitution_verdict(
        {"candidate": "Clean oats", "dietary_status": "safe",
         "evidence_status": "candidate_evidence_current", "safety_tier": "preference"}, verdict)
    assert current["cleared"] is True
    absent = _substitution_verdict({"candidate": "Unmodelled"}, verdict)
    assert absent["state"] == "not_evaluated"


# --- M4: the at-risk table shows dietary state ----------------------------

def test_what_will_run_out_rows_carry_a_dietary_mark():
    a = analyze_state(mixed_state())
    markup = render_dashboard(a)
    runway = markup.split("What will run out", 1)[1].split("</article>", 1)[0]
    rows = runway.split("<tbody>", 1)[1].split("</tbody>", 1)[0]
    assert rows.count("<tr>") >= 3
    assert rows.count("class='mark ") == rows.count("<tr>")
    assert "Dietary" in runway


# --- M5: the join tolerates case and whitespace, never rewrites names -----

def test_join_tolerates_case_and_whitespace_drift():
    a = analyze_state(sample_state())
    a["dietary_evaluations"] = [{
        "item": "  BEAN and cheese   Burritos ", "result": "safe",
        "evidence_status": "current", "safety_tier": "preference", "reason": "No match."}]
    verdict = _dietary_verdict(a)
    assert verdict["orphans"] == []
    matched = _verdict_for(verdict, "Bean and cheese burritos")
    assert matched["cleared"] is True
    assert matched["item"] == "Bean and cheese burritos"


# --- M6: the mark copies its receipt and cannot be stamped ---------------

def test_mark_copies_result_and_evidence_from_the_verdict():
    cleared = _item_verdict("X", {"result": "safe", "evidence_status": "current",
                                  "safety_tier": "preference"})
    markup = _dietary_mark(cleared)
    assert "data-result='safe'" in markup and "data-evidence='current'" in markup
    blocked = _item_verdict("X", {"result": "blocked", "evidence_status": "current",
                                  "safety_tier": "critical"})
    markup = _dietary_mark(blocked)
    assert "data-result='blocked'" in markup and "data-evidence='current'" in markup
    forged = {"item": "X", "state": "cleared", "cleared": False,
              "result": "safe", "evidence": "current", "tier": "Preference", "detail": ""}
    assert "class='mark ok'" not in _dietary_mark(forged)
    assert "data-verdict='not_evaluated'" in _dietary_mark(forged)


# --- M7: the mobile contract keeps the qualifier and a sticky status ------

def test_mobile_css_keeps_the_qualifier_size_and_a_sticky_status():
    css = (ROOT / "src/grocery_flywheel/rendering/layout.py").read_text()
    mobile = css.split("@media (max-width:760px)", 1)[1].split("@media", 1)[0]
    assert ".attention-qualifier { font-size" not in mobile
    assert "position:sticky" in css.split(".masthead-status {", 1)[1].split("}", 1)[0]
    shell = css.split("<main id=\"dashboard\"", 1)[1]
    assert shell.index("</header>") < shell.index("{status_html}")


# --- M8: the download covers cart and held names, not just ledger items ---

def test_dietary_context_covers_a_cart_row_the_ledger_does_not_hold():
    a = cart_only_analysis()
    context = _dietary_context(a)
    names = [row["item"] for row in context["items"]]
    assert "Cart-only oats" in names
    row = next(row for row in context["items"] if row["item"] == "Cart-only oats")
    assert row["state"] == "needs_review" and row["cleared"] is False
    assert context["items_total"] == 13
    assert context["cart_items_total"] == 6
    markup = render_dashboard(a)
    assert "data-item='Cart-only oats'" in markup
    assert "data-verdict='needs_review'" in markup


# --- minors --------------------------------------------------------------

def test_money_renders_a_negative_credit_without_malformed_currency():
    assert _money(-1) == "-$1.00"
    assert _money(None) == "not recorded"
    assert _money(0) == "$0.00"


def test_price_words_count_undated_rows_separately_from_stale_rows():
    a = analyze_state(sample_state())
    counts = _price_buckets(a)
    assert counts == {"priced": 1, "stale": 0, "unknown": 9,
                      "unpriced": 2, "estimated": 1, "gift": 0}
    text = _price_bucket_text(a)
    assert "9 price date unknown" in text and "9 stale" not in text


def test_status_line_uses_the_blocked_count_for_grammar_and_states_the_open_count():
    markup = render_dashboard(analyze_state(mixed_state()))
    status = visible(markup.split("class='masthead-status", 1)[1].split("</p>", 1)[0])
    assert "1 item is blocked" in status
    assert "12 of 13 items are not cleared" in status


def test_action_card_price_buckets_state_their_scope():
    markup = render_dashboard(analyze_state(sample_state()))
    assert "whole ledger (13 items)" in visible(markup)


def test_restock_verb_is_held_on_a_non_cleared_row():
    review = _item_verdict("X", {"result": "needs_review", "evidence_status": "missing",
                                 "safety_tier": "critical"})
    assert _action_text("restock", review) == (
        "Hold restock", "— not dietarily cleared: resolve evidence first")
    cleared = _item_verdict("X", {"result": "safe", "evidence_status": "current",
                                  "safety_tier": "preference"})
    assert _action_text("restock", cleared) == ("Restock", "")


def test_norm_name_only_collapses_case_and_whitespace():
    assert _norm_name("  A  B ") == "a b"
    assert _norm_name(None) == ""
