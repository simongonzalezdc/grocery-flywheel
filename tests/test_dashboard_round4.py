"""Round-4 renderer contracts from the Product r3 HOLD and committee round 2.

Binding findings (dashboard sha ``530de63b…4c79fc5``):

* B1 long content blew the ledger to 17,100 px and the dietary table to
  17,056 px inside ~1,100 px panels;
* B2 the empty state could not be verified because the browser verifier
  assumed a five-column ledger;
* M1 mobile sub-lines landed under the label column;
* M2 a preference-tier warning wore the brick blocker uniform;
* M3 the ledger headline total did not reconcile to its rows;
* M4 the price aggregate counted an estimated-today item as stale;
* M5 sourcing prices had no unit, check date or confidence basis;
* M6 Easy Food and sourcing alternatives omitted dietary state;
* M7 row-level dietary marks were tier-blind;
* M9 sage meant both Cleared and Priced.
"""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

from grocery_flywheel.core import analyze_state
from grocery_flywheel.render import render_dashboard

ROOT = Path(__file__).resolve().parents[1]


def analysis():
    return analyze_state(json.loads((ROOT / 'examples/sample_state.json').read_text()))


def empty_analysis():
    return analyze_state({
        "as_of": "2026-06-06",
        "order": {"store": "Sanitized store", "date": "2026-05-20", "total": 0},
        "items": [],
        "sourcing_research": [],
    })


class Text(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.chunks = []
        self.feed(markup)

    def handle_data(self, data):
        self.chunks.append(data)

    @property
    def text(self):
        return ' '.join(' '.join(self.chunks).split())


def visible(markup):
    return Text(markup).text


# --- B1: long content cannot change table width --------------------------

def test_long_content_tables_are_fixed_layout_with_colgroups():
    state = json.loads((ROOT / 'examples/sample_state.json').read_text())
    state['items'][-1]['name'] = "Sanitized long item " + "x" * 2000
    state['items'][0]['notes'] = "Sanitized long note " + "y" * 2500
    markup = render_dashboard(analyze_state(state))
    css = markup.split('<style>')[1].split('</style>')[0]
    assert 'table-layout:fixed' in css
    tables = re.findall(r'<table>.*?</table>', markup, re.S)
    assert len(tables) >= 3
    for table in tables:
        assert '<colgroup>' in table, table[:120]
    # The over-long note is disclosed, not poured into a fixed-width cell.
    assert 'Read the note (2520 characters)' in markup
    assert 'y' * 2500 in markup


def test_empty_state_renders_copy_instead_of_a_ledger_table():
    markup = render_dashboard(empty_analysis())
    text = visible(markup)
    assert 'No items in the ledger yet.' in text
    assert 'No prices on file.' in text
    assert 'No dietary restriction profile configured.' in text
    ledger = markup.split("The ledger</h2>")[1].split('</article>')[0]
    assert '<table>' not in ledger


# --- M1: mobile records keep the sub-line under the value ----------------

def test_mobile_ledger_grid_places_sub_lines_under_the_value():
    markup = render_dashboard(analysis())
    css = markup.split('<style>')[1].split('</style>')[0]
    assert ".ledger td > .cell-value { grid-column:2; grid-row:1;" in css
    assert ".ledger td > .cell-sub, .ledger td > .mark-detail { grid-column:2;" in css
    ledger = markup.split("The ledger</h2>")[1].split('</article>')[0]
    # Every ledger value cell carries the wrapper the mobile grid depends on.
    assert ledger.count("<span class='cell-value'>") == 5 * 13


# --- M2: brick is reserved for blocking evidence -------------------------

def test_preference_warning_uses_ochre_not_the_blocker_uniform():
    markup = render_dashboard(analysis())
    assert "class='panel span-12 attention warn-tier'" in markup
    css = markup.split('<style>')[1].split('</style>')[0]
    assert '.attention.warn-tier { border-left-color:var(--ochre); }' in css
    assert '.attention.warn-tier .attention-figure { color:var(--ochre); }' in css
    assert "class='attention-qualifier'>Missing evidence is a data gap" in markup
    text = visible(markup)
    assert 'Missing evidence is a data gap, not proof of a safety failure.' in text


def test_blocking_evidence_keeps_the_brick_uniform():
    a = analyze_state({
        "as_of": "2026-06-10",
        "order": {"store": "Sanitized store", "date": "2026-06-01", "total": 8.0},
        "items": [{"name": "Peanut bar", "role": "bridge_food", "category": "snack",
                   "spend": 4.0,
                   "product_evidence": [{"evidence_type": "label", "source": "label",
                                         "checked_date": "2026-06-05",
                                         "ingredients": ["peanut"],
                                         "allergen_statements": ["peanut"],
                                         "certifications": []}]}],
        "dietary_profiles": [{"profile_id": "qa", "restrictions": [
            {"value": "peanut_allergy", "safety_tier": "critical", "behavior": "block"}]}],
    })
    markup = render_dashboard(a)
    assert "class='panel span-12 attention'" in markup
    assert 'warn-tier' not in markup.split("class='panel span-12 attention'")[1][:40]
    assert "class='attention-figure'" in markup


# --- M3/M4: one reconciled headline and four price buckets ---------------

def test_ledger_headline_reconciles_tracked_unattributed_and_order():
    markup = render_dashboard(analysis())
    assert ('13 items &middot; $83.26 tracked &middot; $33.92 unattributed '
            '&middot; $117.18 order') in markup


def test_price_aggregate_renders_the_four_buckets():
    markup = render_dashboard(analysis())
    assert '1 priced &middot; 9 stale &middot; 2 no price &middot; 1 estimated' in markup
    assert '12 of 13 stale or unpriced' not in visible(markup)
    assert 'stale or unpriced' not in visible(markup)


def test_price_state_never_uses_the_sage_clearance_token():
    markup = render_dashboard(analysis())
    ledger = markup.split("The ledger</h2>")[1].split('</article>')[0]
    assert "class='mark plain'" in ledger          # Priced
    assert "class='mark ok'" not in ledger         # no clearance in a price cell
    css = markup.split('<style>')[1].split('</style>')[0]
    assert '.mark.plain { color:var(--ink); }' in css


# --- M5/M6/M7: sourced basis, secondary dietary state, tier marks --------

def test_sourcing_states_its_unit_and_confidence_basis():
    markup = render_dashboard(analysis())
    text = visible(markup)
    assert 'Unit prices' in text and 'per-unit figures' in text
    assert 'no unit label can be stated' in text
    assert 'modelled' in text and 'not a checked shelf price' in text
    assert 'confidence; checked 20 May 2026' in text
    assert 'Best sourcing move' not in text
    assert 'Sourcing candidates' in text
    assert '2 modelled saving rows' in text


def test_easy_food_and_sourcing_alternatives_carry_dietary_state():
    markup = render_dashboard(analysis())
    easy = markup.split('>Easy Food</summary>')[1].split('</details>')[0]
    assert 'Dietary' in easy and "data-raw-status='warn'" in easy
    sourcing = markup.split('>Sourcing Research</summary>')[1].split('</details>')[0]
    assert "data-tier='Preference'" in sourcing
    assert "data-raw-status='warn'" in sourcing


def test_dietary_marks_carry_the_safety_tier():
    markup = render_dashboard(analysis())
    assert "data-tier='Preference'" in markup
    assert 'Warning</span><span class=\'mark-detail\'>No label evidence &middot; Preference tier' in markup


# --- minors: single disclosure titles, one percentage --------------------

def test_disclosure_titles_are_not_duplicated():
    markup = render_dashboard(analysis())
    blocks = re.findall(r"<details class='disclosure'><summary>(.*?)</summary>"
                        r"<div class='disclosure-grid'>(.*?)</div></details>", markup, re.S)
    assert len(blocks) >= 8
    for title, body in blocks:
        # One visible title (the summary); the panel's own heading survives for
        # heading navigation but is not drawn twice.
        assert "<h2 class='visually-hidden'>" in body, title
        assert '<h2>' not in body, title
    titles = [title for title, _ in blocks]
    assert 'Easy Food' in titles and 'Sourcing Research' in titles


def test_all_unpriced_items_use_the_no_price_bucket():
    state = json.loads((ROOT / 'examples/sample_state.json').read_text())
    for item in state['items']:
        item['pricing_status'] = 'unpriced'
    markup = render_dashboard(analyze_state(state))
    assert ('0 priced &middot; 0 stale &middot; 13 no price &middot; 0 estimated') in markup
    assert 'No price captured' in markup
    assert "class='mark ok'" not in markup.split("The ledger</h2>")[1].split('</article>')[0]


def test_runway_percentage_is_one_number():
    markup = render_dashboard(analysis())
    assert '16.4%' in markup
    assert '16%' not in visible(markup)
