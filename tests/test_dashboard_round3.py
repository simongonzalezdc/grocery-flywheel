"""Round-3 renderer contracts: fail closed on state, one vocabulary, real layout.

These tests bind to the roast-committee findings on t_0cad5d1a (dashboard sha
``aaabfc30…c9b893``) and the Product round-2 review:

* a missing/unknown dietary status never renders a success token;
* mixed and blocked states are exercised, not only the warn-only sample;
* the ledger and freshness panel share one price vocabulary;
* the runway states its own basis beside the figure;
* the action list and the downloadable draft carry the dietary state;
* tables keep their captions outside the grid and the disclosure layer is styled.
"""

from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path

from grocery_flywheel.core import analyze_state
from grocery_flywheel.render import render_dashboard

ROOT = Path(__file__).resolve().parents[1]


def analysis():
    return analyze_state(json.loads((ROOT / 'examples/sample_state.json').read_text()))


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


def _evidence(text):
    return {"evidence_type": "label", "source": "sanitized label",
            "checked_date": "2026-06-05",
            "ingredients": [text], "allergen_statements": [], "certifications": []}


def _mixed_state():
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
        "substitutions": [{"current": "Oats", "candidate": "Store-brand oats",
                           "current_unit_price": 1.0, "candidate_unit_price": 0.9,
                           "fit": "same", "read": "Same form."}],
    })


# --- fail closed ---------------------------------------------------------

def test_missing_dietary_evaluations_never_render_a_clearance():
    a = analysis()
    for item in a['items']:
        item['dietary_status'] = 'safe'   # the engine's fail-open shape
    a['dietary_evaluations'] = []
    markup = render_dashboard(a)
    text = visible(markup)
    # The legend defines Cleared; no item may carry the success token or raw safe.
    assert "data-raw-status='safe'" not in markup
    ledger = markup.split("The ledger</h2>")[1].split('</article>')[0]
    assert ledger.count("data-raw-status='not_evaluated'") == len(a['items'])
    assert '>Cleared<' not in ledger
    assert '13/13' in markup and 'items unverified' in text
    assert 'No item has been cleared as safe for your household diet.' in text
    assert 'All 13 items are cleared' not in text
    assert 'Not evaluated' in text


def test_unknown_dietary_status_renders_neutral_not_evaluated():
    a = analysis()
    a['items'][0]['dietary_status'] = 'mystery_state'
    markup = render_dashboard(a)
    assert "data-raw-status='mystery_state'" not in markup
    assert "data-raw-status='not_evaluated'" in markup
    assert 'Not evaluated' in visible(markup)


def test_substitution_rows_without_a_dietary_field_are_not_evaluated():
    a = analysis()
    markup = render_dashboard(a)
    for row in a['substitutions']:
        assert 'dietary_status' not in row
    assert 'Not evaluated' in visible(markup)
    assert 'not a clearance' in visible(markup)
    assert "candidate's own engine state" in visible(markup)


def test_safe_requires_current_evidence_and_a_dietary_evaluation():
    a = _mixed_state()
    markup = render_dashboard(a)
    text = visible(markup)
    # One explicit safe item with current evidence may be called Cleared.
    assert '1/2' not in text  # figure is "not cleared" (2 of 3)
    assert '2/3' in text
    assert '1 item is blocked by your household dietary restrictions.' in text
    ok_spans = [span for span in markup.split("class='mark ok'")[1:]
                if "data-raw-status='safe'" in span.split('>')[0]]
    blocked_spans = [span for span in markup.split("class='mark missing'")[1:]
                     if "data-raw-status='blocked'" in span.split('>')[0]]
    assert ok_spans and blocked_spans
    assert 'Needs review' in text


def test_mixed_states_use_their_own_tokens():
    markup = render_dashboard(_mixed_state())
    assert "data-raw-status='safe'" in markup
    assert "data-raw-status='blocked'" in markup
    assert "data-raw-status='needs_review'" in markup
    assert 'masthead-status alert' in markup
    assert 'state-legend' in markup


# --- vocabulary and basis ------------------------------------------------

def test_one_price_vocabulary_across_ledger_and_freshness():
    markup = render_dashboard(analysis())
    text = visible(markup)
    assert 'No price record' not in text
    assert 'priced but stale' not in text
    # A stale price with no check date is unknown, not asserted stale.
    assert 'Price on file · date unknown' in text
    assert 'No price captured' in text
    assert 'Estimated price' in text
    assert 'Priced' in text


def test_ledger_without_a_freshness_record_keeps_the_same_words():
    a = analysis()
    a.pop('freshness', None)
    text = visible(render_dashboard(a))
    assert 'No price record' not in text
    assert 'No price captured' in text


def test_runway_states_its_basis_beside_the_figure():
    text = visible(render_dashboard(analysis()))
    assert 'How this is estimated' in text
    assert '$117.18' in text and '$33.92' in text
    assert 'spread dollar-weighted over 4 observed days' in text
    assert 'not a pantry audit' in text


def test_action_list_and_draft_carry_dietary_context():
    a = analysis()
    markup = render_dashboard(a)
    text = visible(markup)
    assert text.count('Dietary') >= len(a['cart_plan']['items'])
    assert 'No label evidence' in text
    attrs = next(attrs for tag, attrs in _tags(markup) if attrs.get('id') == 'buy-list-download')
    context = json.loads(attrs['data-plan'])['presentation']['dietary_context']
    assert len(context['items']) == 13
    assert context['items_not_cleared'] == 13
    assert context['restrictions'][0]['safety_tier'] == 'preference'
    assert all(row['result'] == 'warn' for row in context['items'])
    assert all(row['cleared'] is False for row in context['items'])


def _tags(markup):
    class Tags(HTMLParser):
        def __init__(self):
            super().__init__()
            self.found = []

        def handle_starttag(self, tag, attrs):
            self.found.append((tag, dict(attrs)))

    parser = Tags()
    parser.feed(markup)
    return parser.found


# --- layout and disclosure ----------------------------------------------

def test_ledger_has_five_columns_and_captions_stay_outside_tables():
    markup = render_dashboard(analysis())
    ledger = markup.split("The ledger</h2>")[1].split('</article>')[0]
    assert ledger.count('<th>') == 5
    assert '<caption' not in markup
    assert "<p class='table-caption'>" in ledger
    assert 'All 13 items share the same dietary display (Warning)' in visible(markup)


def test_disclosure_layer_is_styled_and_span_classes_are_not_inert():
    markup = render_dashboard(analysis())
    css = markup.split('<style>')[1].split('</style>')[0]
    assert '.muted { color:var(--muted); }' in css
    assert '.disclosure h2 {' in css
    assert '.disclosure-grid {' in css
    assert '.wow' not in css and 'wow' not in markup
    assert "class='disclosure-grid'" in markup


def test_meaningful_graphics_use_a_three_to_one_token():
    css = render_dashboard(analysis()).split('<style>')[1].split('</style>')[0]

    def token(name):
        start = css.index(f'--{name}:')
        return css[start + len(name) + 3:].split(';')[0].strip()

    def luminance(hex_colour):
        channels = [int(hex_colour.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        channels = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
                    for c in channels]
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    def ratio(a, b):
        high, low = sorted((luminance(a), luminance(b)), reverse=True)
        return (high + 0.05) / (low + 0.05)

    strong = token('edge-strong')
    for surface in (token('bg'), token('panel')):
        assert ratio(strong, surface) >= 3.0, (strong, surface, ratio(strong, surface))
    assert "stroke='var(--edge-strong)'" in render_dashboard(analysis())
    assert 'border:1px solid var(--edge-strong)' in css


def test_skip_link_targets_the_review_section_and_print_is_styled():
    markup = render_dashboard(analysis())
    assert 'class="skip-link" href="#household-review"' in markup
    assert 'id="household-review"' in markup
    assert '@media print' in markup.split('<style>')[1].split('</style>')[0]


def test_attention_qualifier_is_weighted_and_tier_is_stated():
    text = visible(render_dashboard(analysis()))
    assert 'Missing evidence is a data gap, not proof of a safety failure.' in text
    assert 'a warning is never a safety verdict' in text
    assert 'safety tier: Preference' in text
    assert 'Blocked' in text and 'Not evaluated' in text


def test_sanitized_sample_has_no_real_brand_and_no_enum_source_leak():
    markup = render_dashboard(analysis())
    text = visible(markup)
    assert 'Tyson' not in markup
    assert 'normal store' not in text
    assert 'your usual store' in text
