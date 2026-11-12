"""Round-5 renderer contracts from the Product r4 HOLD and committee round 4.

Binding findings (native artifact ``2cc4d55f…b6e5f``):

* ``_dietary_mark`` read the item's ``dietary_status`` and could paint a green
  "Cleared" over a blocked/needs-review evaluation with current evidence;
* ``_evidence_drawer`` silently dropped list entries after the fourth;
* the aggregate headline stayed absolute ("No item has been cleared") when some
  items were cleared;
* the sourcing dietary mark was the original item's, unlabelled under candidate
  rows;
* ``_money(None)`` fabricated ``$0.00`` on a trust surface;
* the mobile first screen repeated the count and pushed the action to 1,091 px;
* captures stopped at 1,000 px and showed only the masthead;
* "every item is Needs your approval." and unlabelled mobile source lines.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from grocery_flywheel.core import analyze_state
from grocery_flywheel.render import render_dashboard
from grocery_flywheel.rendering.panels import _dietary_mark, _item_verdict, _money

ROOT = Path(__file__).resolve().parents[1]


def sample_state():
    return json.loads((ROOT / 'examples/sample_state.json').read_text())


def analysis():
    return analyze_state(sample_state())


def _evidence(text):
    return {"evidence_type": "label", "source": "sanitized label",
            "checked_date": "2026-06-05",
            "ingredients": [text], "allergen_statements": [], "certifications": []}


def _mixed_state():
    """One cleared item, one blocked item, one item with no evidence."""
    return analyze_state({
        "as_of": "2026-06-10",
        "order": {"store": "Sanitized store", "date": "2026-06-01", "total": 18.0},
        "acquisition_channel": "normal_store",
        "items": [
            {"name": "Oat cereal", "role": "pantry_base", "category": "dry_good",
             "spend": 8.0, "product_evidence": [_evidence("oats")]},
            {"name": "Peanut granola", "role": "bridge_food", "category": "dry_good",
             "spend": 6.0, "product_evidence": [_evidence("oats and peanut")]},
            {"name": "Mystery bar", "role": "flavor_unlock", "category": "snack",
             "spend": 4.0},
        ],
        "dietary_profiles": [{
            "profile_id": "qa-household", "label": "QA household",
            "restrictions": [{"value": "peanut_allergy", "safety_tier": "critical",
                              "behavior": "block"}],
        }],
        "substitutions": [
            {"current": "Oats", "candidate": "Peanut granola",
             "current_unit_price": 1.0, "candidate_unit_price": 0.9,
             "fit": "same", "read": "Same form."},
        ],
        "sourcing_research": [
            {"item": "Peanut granola", "current_source": "Example Grocery",
             "current_unit_price": 0.9,
             "alternatives": [{"source": "Bulk bin", "unit_price": 0.8,
                               "savings": "11%", "confidence": "medium",
                               "checked_date": "2026-06-05",
                               "constraints": ["bulk storage"]}],
             "recommendation": "Check the bulk bin."},
        ],
    })


def _lie_about_item_status(a):
    """The exact fail-open shape: item field says safe, evaluation disagrees."""
    for item in a["items"]:
        item["dietary_status"] = "safe"
    return a


def _with_cart_plan(a):
    a["cart_plan"] = {
        "mode": "pickup",
        "items": [
            {"item": item["name"], "action": "restock", "source": "normal store",
             "reason": "High observed depletion.", "approval_state": "needs_human_approval"}
            for item in a["items"]
        ],
    }
    return a


# --- BLOCKER: the mark derives from the evaluation, never the item field ----


def test_contradictory_pair_never_paints_a_green_clearance():
    # The authority is the only input to the mark: an item's own ``safe`` field
    # cannot be passed, so a contradictory evaluation wins by construction.
    blocked = _dietary_mark(_item_verdict("Peanut granola", {
        'result': 'blocked', 'evidence_status': 'current', 'safety_tier': 'allergy'}))
    assert "class='mark ok'" not in blocked
    assert ">Cleared<" not in blocked
    assert ">Blocked<" in blocked

    review = _dietary_mark(_item_verdict("x", {
        'result': 'needs_review', 'evidence_status': 'current'}))
    assert "class='mark ok'" not in review
    assert ">Needs review<" in review

    warn = _dietary_mark(_item_verdict("x", {
        'result': 'warn', 'evidence_status': 'current'}))
    assert "class='mark ok'" not in warn
    assert ">Warning<" in warn

    cleared = _dietary_mark(_item_verdict("x", {
        'result': 'safe', 'evidence_status': 'current'}))
    assert "class='mark ok'" in cleared and ">Cleared<" in cleared

    stale = _dietary_mark(_item_verdict("x", {
        'result': 'safe', 'evidence_status': 'stale'}))
    assert "class='mark ok'" not in stale and "Not evaluated" in stale

    assert "Not evaluated" in _dietary_mark(_item_verdict("x", None))


def test_item_status_cannot_reach_the_mark_authority():
    """The r2/r4 fail-open class is impossible at the presentation boundary."""
    import inspect
    params = list(inspect.signature(_dietary_mark).parameters)
    assert params == ["verdict"], params
    verdict = _item_verdict("Peanut granola", {
        'result': 'blocked', 'evidence_status': 'current'})
    assert verdict["cleared"] is False and verdict["state"] == "blocked"
    assert "item_status" not in repr(verdict)


def test_contradictory_pair_is_fail_closed_in_every_call_site():
    a = _with_cart_plan(_lie_about_item_status(_mixed_state()))
    markup = render_dashboard(a)
    # The ledger and cart review carry the evaluation's blocked mark, not the
    # item's claimed safe field.
    ledger = markup.split("The ledger</h2>")[1].split('</article>')[0]
    rows = [row for row in ledger.split("<tr>") if "Peanut granola" in row]
    assert rows and all("data-raw-status='blocked'" in row for row in rows)
    assert all("data-raw-status='safe'" not in row for row in rows)
    action = markup.split("Today &middot; before you shop</h2>")[1].split('</article>')[0]
    rows = [row.split('</li>')[0] for row in action.split("<li")[1:]]
    rows = [row for row in rows if ">Peanut granola<span class='action-why'>" in row]
    assert rows and all("data-raw-status='blocked'" in row for row in rows)
    assert all("data-raw-status='safe'" not in row for row in rows)
    substitution = markup.split('>Substitutions</summary>')[1].split('</details>')[0]
    rows = [row for row in substitution.split("<tr>") if "Peanut granola" in row]
    assert rows and all("data-raw-status='blocked'" in row for row in rows)
    assert all("data-raw-status='safe'" not in row for row in rows)
    sourcing = markup.split('>Sourcing Research</summary>')[1].split('</details>')[0]
    rows = [row for row in sourcing.split("class='source-row'") if "Peanut granola" in row]
    assert rows and all("data-raw-status='blocked'" in row for row in rows)
    assert all("data-raw-status='safe'" not in row for row in rows)


# --- evidence drawer: nothing is silently dropped ---------------------------


def test_evidence_drawer_shows_every_label_entry():
    a = analysis()
    a["items"][0]["product_evidence"] = [{
        "evidence_type": "label", "source": "sanitized label",
        "checked_date": "2026-05-20",
        "ingredients": ["oats", "barley", "rye", "wheat", "peanut"],
        "allergen_statements": ["peanut"], "certifications": [],
    }]
    markup = render_dashboard(a)
    ledger = markup.split("The ledger</h2>")[1].split('</article>')[0]
    for entry in ("oats", "barley", "rye", "wheat", "peanut"):
        assert entry in ledger
    assert 'showing 4 of' not in ledger


# --- aggregate counts are exact on a mixed page ----------------------------


def test_mixed_headline_states_exact_counts():
    a = _mixed_state()
    markup = render_dashboard(a)
    text = " ".join(markup.replace("&middot;", " ").split())
    assert "1 of 3 cleared" in text
    assert "1 blocked" in text
    assert "1 needs review" in text
    assert "No item has been cleared as safe" not in text


def test_one_cleared_one_open_never_uses_the_absolute_claim():
    a = _mixed_state()
    a["items"] = [item for item in a["items"] if item["name"] != "Peanut granola"]
    a["dietary_evaluations"] = [row for row in a["dietary_evaluations"]
                                if row["item"] != "Peanut granola"]
    a["substitutions"] = []
    a["sourcing_research"] = []
    for item in a["items"]:
        item["dietary_status"] = "safe"  # the engine's fail-open default shape
    text = " ".join(render_dashboard(a).replace("&middot;", " ").split())
    assert "1 of 2 items are cleared; 1 item is not cleared." in text
    assert "No item has been cleared as safe" not in text


def test_name_mismatch_evaluation_counts_as_not_evaluated():
    a = _mixed_state()
    for row in a["dietary_evaluations"]:
        if row["item"] == "Mystery bar":
            row["item"] = "Ghost item"
    text = " ".join(render_dashboard(a).replace("&middot;", " ").split())
    assert "1 not evaluated" in text
    assert "Mystery bar" in text


# --- sourcing subject, money, copy, mobile affordance ----------------------


def test_sourcing_labels_the_dietary_subject():
    text = " ".join(render_dashboard(_mixed_state()).replace("&middot;", " ").split())
    assert "Dietary this item, not the alternatives" in text
    assert "Alternatives carry no dietary evaluation here" in text


def test_money_never_fabricates_a_zero():
    assert _money(None) == "not recorded"
    assert _money("") == "not recorded"
    assert _money("bogus") == "not recorded"
    assert _money(0) == "$0.00"
    a = analysis()
    a["items"][0]["spend"] = None
    ledger = render_dashboard(a).split("The ledger</h2>")[1].split('</article>')[0]
    assert "not recorded" in ledger


def test_action_copy_and_labels_are_household_language():
    text = " ".join(render_dashboard(analysis()).replace("&middot;", " ").split())
    assert "every item needs your approval before anything is bought." in text
    assert "every item is Needs your approval" not in text
    markup = render_dashboard(analysis())
    action = markup.split("Today &middot; before you shop</h2>")[1].split('</article>')[0]
    assert "<span class='eyebrow-inline'>Action</span>" in action
    assert "<span class='eyebrow-inline'>Source</span>" in action


def test_mobile_first_screen_has_a_jump_to_the_action():
    markup = render_dashboard(analysis())
    assert "class='panel span-12 today' id='today'" in markup
    assert "class='jump-link' href='#today'" in markup
    css = markup.split('<style>')[1].split('</style>')[0]
    assert '.jump-link {' in css and 'min-height:44px' in css
    assert '.attention { padding:14px 14px 16px;' in css
    assert '.attention-verdict h3 { font-size:var(--step-1);' in css


def test_severity_has_a_text_token_not_only_hue():
    text = " ".join(render_dashboard(analysis()).replace("&middot;", " ").split())
    assert "Dietary evidence warning tier" in text
    blocked = " ".join(render_dashboard(_mixed_state()).replace("&middot;", " ").split())
    assert "Dietary evidence blocked" in blocked


def test_note_disclosure_meets_the_hit_area_floor():
    css = render_dashboard(analysis()).split('<style>')[1].split('</style>')[0]
    assert '.note-disclosure > summary { padding:6px 0; min-height:32px;' in css


def test_sample_sourcing_dates_are_not_in_the_future():
    state = sample_state()
    as_of = date.fromisoformat(state["as_of"])
    for row in state.get("sourcing_research", []):
        for alt in row.get("alternatives", []):
            assert date.fromisoformat(alt["checked_date"]) <= as_of
