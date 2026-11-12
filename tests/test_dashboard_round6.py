"""Round-6 contracts: one dietary verdict authority and the surfaces it feeds.

The r2/r4/r5 defects were the same class: each surface decided clearance for
itself. Round 6 replaces those decisions with ``_item_verdict`` and makes
``_dietary_mark`` accept nothing else, then asserts the invariant over every
fixture and every call site:

    mark_token == cleared  iff  result == safe AND evidence == current

The action area is also fail-closed: every blocked item appears there (held even
when the engine's cart plan has no row), and no non-cleared item carries an
unqualified Restock.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from grocery_flywheel.core import analyze_state
from grocery_flywheel.render import render_dashboard
from grocery_flywheel.rendering.panels import (
    _dietary_mark,
    _dietary_verdict,
    _item_verdict,
    _spend_cell,
    _verdict_parts,
)

ROOT = Path(__file__).resolve().parents[1]
MARK_RE = re.compile(r"<span class='mark ([a-z]+)'(.*?)>(.*?)</span>", re.S)


def sample_state() -> dict:
    return json.loads((ROOT / "examples" / "sample_state.json").read_text())


def mixed_state() -> dict:
    """Block/critical restriction: one cleared item, one blocked, eleven open."""
    state = sample_state()
    state["dietary_profiles"] = [{
        "profile_id": "native-mixed",
        "label": "Sanitized household",
        "restrictions": [{"value": "peanut_allergy", "safety_tier": "critical",
                          "behavior": "block"}],
    }]
    checked = state["as_of"]
    state["items"][0]["product_evidence"] = [{
        "evidence_type": "label", "source": "sanitized label", "checked_date": checked,
        "ingredients": ["oats"], "allergen_statements": [], "certifications": []}]
    state["items"][1]["product_evidence"] = [{
        "evidence_type": "label", "source": "sanitized label", "checked_date": checked,
        "ingredients": ["oats and peanut"], "allergen_statements": ["peanut"],
        "certifications": []}]
    return state


def orphan_analysis() -> dict:
    """Mixed analysis plus one blocked evaluation that names no page item."""
    analysis = analyze_state(mixed_state())
    analysis["dietary_evaluations"] = list(analysis.get("dietary_evaluations") or []) + [{
        "item": "Renamed waffles", "result": "blocked", "evidence_status": "current",
        "safety_tier": "critical", "reason": "Evidence matched: peanut."}]
    return analysis


def parsed_marks(markup: str) -> list[dict]:
    rows = []
    for token, attrs, label in MARK_RE.findall(markup):
        item = re.search(r"data-item='([^']*)'", attrs)
        verdict = re.search(r"data-verdict='([^']*)'", attrs)
        result = re.search(r"data-result='([^']*)'", attrs)
        evidence = re.search(r"data-evidence='([^']*)'", attrs)
        rows.append({
            "token": token,
            "item": item.group(1) if item else "",
            "state": verdict.group(1) if verdict else "",
            "result": result.group(1) if result else "",
            "evidence": evidence.group(1) if evidence else "",
            "label": label,
        })
    return rows


def visible(markup: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", markup).split())


# --- the authority ---------------------------------------------------------

@pytest.mark.parametrize("evaluation,state,cleared", [
    ({"result": "safe", "evidence_status": "current"}, "cleared", True),
    ({"result": "safe", "evidence_status": "stale"}, "not_evaluated", False),
    ({"result": "safe", "evidence_status": "missing"}, "not_evaluated", False),
    ({"result": "blocked", "evidence_status": "current"}, "blocked", False),
    ({"result": "needs_review", "evidence_status": "missing"}, "needs_review", False),
    ({"result": "warn", "evidence_status": "missing"}, "warning", False),
    ({"result": "mystery"}, "not_evaluated", False),
    ({"evidence_status": "current"}, "not_evaluated", False),
    (None, "not_evaluated", False),
])
def test_verdict_truth_table(evaluation, state, cleared):
    verdict = _item_verdict("item", evaluation)
    assert verdict["state"] == state
    assert verdict["cleared"] is cleared
    assert verdict["label"] == {
        "cleared": "Cleared", "blocked": "Blocked", "needs_review": "Needs review",
        "warning": "Warning", "not_evaluated": "Not evaluated"}[state]


def test_mark_renders_only_the_authority_and_carries_its_receipt():
    cleared = _dietary_mark(_item_verdict("Oats", {
        "result": "safe", "evidence_status": "current"}))
    assert "class='mark ok'" in cleared and "data-verdict='cleared'" in cleared
    assert "data-result='safe'" in cleared and "data-evidence='current'" in cleared

    blocked = _dietary_mark(_item_verdict("Peanuts", {
        "result": "blocked", "evidence_status": "current"}))
    assert "class='mark missing'" in blocked
    assert "data-verdict='blocked'" in blocked
    assert "data-result='safe'" not in blocked


# --- the invariant, over every fixture and every surface --------------------

@pytest.mark.parametrize("factory", [
    lambda: analyze_state(sample_state()),
    lambda: analyze_state(mixed_state()),
    orphan_analysis,
])
def test_every_surface_renders_the_same_verdict_for_an_item(factory):
    analysis = factory()
    markup = render_dashboard(analysis)
    authority = _dietary_verdict(analysis)
    marks = [row for row in parsed_marks(markup) if row["item"]]
    assert marks, "no dietary marks rendered"

    # One item, one verdict everywhere it appears (ledger, action list,
    # substitutions, sourcing, easy food, evidence drawer).
    seen: dict[str, str] = {}
    for row in marks:
        if row["item"] in seen:
            assert seen[row["item"]] == row["state"], (
                f"{row['item']} renders {seen[row['item']]} and {row['state']}")
        else:
            seen[row["item"]] = row["state"]

    # mark_token == cleared iff safe AND current evidence.
    for row in marks:
        assert (row["token"] == "ok") is (row["state"] == "cleared"), row
        if row["state"] == "cleared":
            assert row["result"] == "safe" and row["evidence"] == "current", row

    # The authority's own clearance count is what the page paints, never more.
    cleared_items = {name for name, row in authority["verdicts"].items() if row["cleared"]}
    ok_items = {row["item"] for row in marks if row["token"] == "ok"}
    assert ok_items <= cleared_items
    for name in cleared_items:
        assert name in ok_items, f"cleared item {name} is not painted ok anywhere"


def test_no_surface_can_paint_a_clearance_from_an_item_field():
    """The r2/r4 shape: item says safe, evaluation disagrees or is absent."""
    analysis = analyze_state(mixed_state())
    for item in analysis["items"]:
        item["dietary_status"] = "safe"
    markup = render_dashboard(analysis)
    ledger = markup.split("The ledger</h2>")[1].split("</article>")[0]
    assert "data-verdict='cleared'" in ledger or "data-verdict='blocked'" in ledger
    assert ledger.count("data-verdict='cleared'") == 1
    for row in parsed_marks(ledger):
        if row["token"] == "ok":
            assert row["result"] == "safe" and row["evidence"] == "current"


# --- BLOCKER: the action area carries every blocked item -------------------

def test_blocked_item_absent_from_the_cart_plan_is_held_in_the_action_area():
    analysis = analyze_state(mixed_state())
    cart_names = {row["item"] for row in analysis["cart_plan"]["items"]}
    assert "Homestyle waffles" not in cart_names  # the r5 shape
    markup = render_dashboard(analysis)
    today = markup.split("id='today'")[1].split("</article>")[0]
    assert "Homestyle waffles" in today
    assert "class='action-hold'" in today
    assert "Do not buy — blocked: Evidence matched: peanut." in visible(today)


def test_no_unqualified_restock_on_a_non_cleared_item():
    analysis = analyze_state(mixed_state())
    markup = render_dashboard(analysis)
    today = markup.split("id='today'")[1].split("</article>")[0]
    rows = re.findall(r"<li[^>]*data-action-item='([^']+)'.*?</li>", today, re.S)
    assert rows
    for row in re.findall(r"<li[^>]*data-action-item=.*?</li>", today, re.S):
        name_match = re.search(r"data-action-item='([^']+)'", row)
        assert name_match is not None
        name = name_match.group(1)
        verdict = re.search(r"data-verdict='([^']+)'", row)
        qualifier = re.search(r"class='action-qualifier'", row)
        if verdict and verdict.group(1) != "cleared":
            assert qualifier, f"{name} has an unqualified action"
        else:
            assert not qualifier, f"{name} is cleared but carries a qualifier"


# --- MAJORS: spend, restriction copy, sourcing count, orphans, price -------

def test_unpriced_placeholder_is_not_rendered_as_a_recorded_zero():
    assert "not recorded" in _spend_cell(
        {"spend": 0, "consumed_fraction": 0.17},
        {"pricing_status": "unpriced", "pricing_stale": False})
    recorded_zero = _spend_cell(
        {"spend": 0, "consumed_fraction": 0.5},
        {"pricing_status": "gift", "pricing_stale": False})
    assert "$0.00" in recorded_zero


def test_ledger_unpriced_row_does_not_show_a_fabricated_zero():
    markup = render_dashboard(analyze_state(sample_state()))
    ledger = markup.split("The ledger</h2>")[1].split("</article>")[0]
    row = [row for row in ledger.split("<tr>") if "Example top-up frozen meal" in row]
    assert row
    assert "not recorded" in row[0]
    assert "$0.00" not in row[0]


def test_restriction_copy_is_derived_from_the_actual_behaviour():
    warn_markup = render_dashboard(analyze_state(sample_state()))
    assert "configured to warn" in warn_markup
    assert "data gap, not proof of a safety failure" in warn_markup

    block_markup = render_dashboard(analyze_state(mixed_state()))
    assert "set to block" in block_markup
    assert "never as cleared" in block_markup
    assert "data gap, not proof of a safety failure" not in block_markup


def test_sourcing_counts_the_real_candidates():
    markup = render_dashboard(analyze_state(sample_state()))
    assert "Sourcing candidates" in markup
    assert "2 modelled saving rows" in markup
    assert "One sourcing candidate" not in markup


def test_orphan_blocked_evaluation_is_surfaced_not_dropped():
    analysis = orphan_analysis()
    verdict = _dietary_verdict(analysis)
    assert len(verdict["orphans"]) == 1
    assert verdict["orphans"][0]["state"] == "not_evaluated"
    assert verdict["orphans"][0]["cleared"] is False
    markup = render_dashboard(analysis)
    assert "Renamed waffles" in markup
    assert "Evidence did not match an item on this page" in markup
    assert "could not be applied" in markup
    assert "data-orphan='true'" in markup


def test_stale_price_without_a_check_date_is_unknown_not_asserted():
    markup = render_dashboard(analyze_state(sample_state()))
    assert "Price · date unknown" in markup
    # The label is chosen from the row's own detail, not asserted from `stale`.
    from grocery_flywheel.rendering.panels import _price_state
    unknown, _css, _detail = _price_state({}, {
        "pricing_status": "priced", "pricing_stale": True, "age_label": "no check date"})
    assert unknown == "Price · date unknown"
    stale, _css, _detail = _price_state({}, {
        "pricing_status": "priced", "pricing_stale": True, "age_label": "12 days"})
    assert stale == "Stale price on file"


def test_legend_states_the_behaviour_dependency():
    markup = render_dashboard(analyze_state(mixed_state()))
    assert "A blocking restriction the engine cannot verify; never cleared." in markup
    assert "A warn-tier restriction. A warning is not a clearance." in markup
    assert "Evidence missing, stale or ambiguous." not in markup


def test_pulse_notes_are_labelled_as_unverified_free_text():
    markup = render_dashboard(analyze_state(sample_state()))
    assert "unverified note" in markup
    assert "not reconciled against the ledger or the depletion model" in markup


def test_counts_name_the_cleared_items_and_never_claim_absolute_safety():
    sample = _dietary_verdict(analyze_state(sample_state()))
    assert _verdict_parts(sample).startswith("0 of 13 cleared")
    mixed = _dietary_verdict(analyze_state(mixed_state()))
    assert _verdict_parts(mixed).startswith("1 of 13 cleared")
