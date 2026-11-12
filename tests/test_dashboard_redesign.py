"""Presentation contracts: truthful state, retained evidence and local exports.

These are the renderer contracts Product reviewed on t_0cad5d1a: the dietary
verdict leads, the action list carries each item's own reason, warnings never
wear the success token, runway is a shape plus a table, and the ledger admits
the unattributed remainder of the order total.
"""
import json
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path

import pytest

from grocery_flywheel.core import analyze_state
from grocery_flywheel.render import render_dashboard

ROOT = Path(__file__).resolve().parents[1]


def analysis():
    return analyze_state(json.loads((ROOT / 'examples/sample_state.json').read_text()))


class Document(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.tags = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class Text(HTMLParser):
    """Visible text only: attributes and markup do not count as prose."""

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


def test_reading_order_is_attention_action_runway_ledger_then_evidence():
    a = analysis()
    before = deepcopy(a)
    markup = render_dashboard(a)
    assert a == before, 'rendering must not mutate the analysis'
    order = ['Needs attention today', 'Today &middot; one thing', 'What will run out',
             'The ledger', 'Savings and sourcing overview']
    positions = [markup.index(item) for item in order]
    assert positions == sorted(positions)
    # Easy Food is no longer a half-width orphan between full-width sections.
    assert markup.index('Easy Food') > markup.index('The ledger')


def test_dietary_attention_renders_the_fail_closed_verdict():
    markup = render_dashboard(analysis())
    assert '13/13' in markup
    assert 'items unverified' in markup
    assert 'No item has been cleared as safe for your household diet.' in markup
    assert 'the engine returns a warning for every item and clears none of them' in markup
    assert '13 of 13 items have no current ingredient, allergen, or certification evidence' in markup
    assert '13 dietary evaluations' in markup
    assert "data-raw-result='warn'" in markup
    assert "data-raw-evidence='missing'" in markup
    # Every evaluation carries its own item, result, evidence and reason.
    for row in analysis()['dietary_evaluations']:
        assert row['item'] in markup
        assert row['reason'] in markup
    # The masthead states the count; the panel owns the full verdict (no 3x repeat).
    assert '13 of 13 items are unverified' in markup
    assert 'state-legend' in markup


def test_warn_never_uses_the_success_token_and_depletion_is_not_success():
    markup = render_dashboard(analysis())
    assert "<span class='tag ok'>warn" not in markup
    assert "class='mark ok' data-raw-status='warn'" not in markup
    assert "class='mark warn' data-raw-status='warn'" in markup
    css = markup.split('<style>')[1].split('</style>')[0]
    assert '.bar > span { display:block; height:100%; background:var(--copper); }' in css
    assert '.bar.hot > span { background:var(--brick); }' in css
    assert "class='bar hot'" in markup  # 100% drawdown reads as depletion, not success


def test_cart_review_shows_each_reason_and_source_in_visible_prose():
    a = analysis()
    markup = render_dashboard(a)
    text = visible(markup)
    for item in a['cart_plan']['items']:
        assert item['item'] in text
        assert item['reason'] in text
        shown_source = {'normal store': 'your usual store'}.get(str(item['source'] or ''), str(item['source'] or ''))
        assert shown_source in text
    assert '01' in text and '04' in text
    # Raw enum slugs are for machines, not for the household reading the page.
    assert '>review_alternate_source' not in markup
    assert '>needs_human_approval' not in markup
    assert 'review_alternate_source' not in text
    assert 'needs_human_approval' not in text


def test_visible_copy_humanizes_engine_vocabulary_and_plurals():
    text = visible(render_dashboard(analysis()))
    for raw in ('bridge_food', 'critical_household_essential', 'pantry_base', 'flavor_unlock',
                'frozen_meal', 'ready_drink', 'refrigerated_protein', 'in_store',
                'retailer_history_import', '2026-05-20', '2026-05-24'):
        assert raw not in text, raw
    assert 'Bridge food' in text
    assert 'Household essential' in text
    assert '20 May 2026' in text
    assert '24 May 2026' in text
    assert '4 days observed' in text
    assert '(s) ' not in text and 'top-up(s)' not in text and 'day(s)' not in text


def test_ledger_carries_dietary_price_and_product_evidence_columns():
    markup = render_dashboard(analysis())
    assert '<th>Price</th><th>Dietary</th><th>Product evidence</th>' in markup
    assert 'No label evidence' in markup
    # One price vocabulary: the ledger uses the freshness record's resolved state.
    assert 'Stale price on file' in markup
    assert 'No price record' not in markup
    text = visible(markup)
    assert 'Priced' in text and 'No price captured' in text
    assert 'Warning' in text


def test_ledger_reconciles_tracked_and_unattributed_order_value():
    markup = render_dashboard(analysis())
    assert '$117.18' in markup and '$83.26' in markup and '$33.92' in markup
    assert 'not attributed to any tracked item' in markup


def test_runway_ruler_and_at_risk_table_are_present():
    markup = render_dashboard(analysis())
    assert "aria-label='Runway ruler: 4 days observed, 20.4 days remaining.'" in markup
    assert 'Days of runway left' in markup and 'Days since the order' in markup
    assert 'Items at or past half their observed life' in markup
    assert '$19.22' in markup and 'seen consumed' in markup


def test_attention_figure_outranks_metric_numbers_in_the_stylesheet():
    markup = render_dashboard(analysis())
    css = markup.split('<style>')[1].split('</style>')[0]
    assert '.attention-figure { font-family:var(--display); font-size:var(--step-4)' in css
    assert '.math-value { font-family:var(--display); font-size:var(--step-2)' in css
    assert '2.4rem' not in css


@pytest.mark.parametrize('consent,visible_controls', [(None, False), ({}, False),
    ({'correction_telemetry': 'disabled'}, False),
    ({'correction_telemetry': 'local_only'}, True),
    ({'correction_telemetry': 'hosted_opt_in'}, True)])
def test_consent_is_not_granted_by_presentation(consent, visible_controls):
    a = analysis()
    a['consent'] = consent
    markup = render_dashboard(a)
    assert ('id="correction-item"' in markup) is visible_controls
    if visible_controls:
        assert 'nothing is saved to household state' in markup
        assert '<label for="correction-item">' in markup


def test_download_contains_actual_draft_not_prototype_sample():
    a = analysis()
    a['order']['store'] = 'Different sanitized store'
    markup = render_dashboard(a)
    attrs = next(attrs for tag, attrs in Document(markup).tags if attrs.get('id') == 'buy-list-download')
    payload = json.loads(attrs['data-plan'])
    # Every engine field of the real draft is retained verbatim.
    for key, value in a['cart_plan'].items():
        assert payload[key] == value
    assert payload['approval_required'] is True
    assert payload['checkout_available'] is False
    # The download now carries the dietary state the page shows.
    context = payload['presentation']['dietary_context']
    assert context['items_total'] == 13
    assert context['items_not_cleared'] == 13
    assert all(row['cleared'] is False for row in context['items'])
    assert 'not a clearance' in context['note']


def test_empty_state_does_not_claim_clearance_or_invent_a_cart():
    a = analysis()
    for key in ('items', 'dietary_profiles', 'dietary_evaluations', 'role_summary', 'preferences',
                'pulses', 'substitutions', 'sourcing_research'):
        a[key] = []
    a['cart_plan']['items'] = []
    a['easy_food'] = {}
    markup = render_dashboard(a)
    assert 'No dietary restriction profile configured' in markup
    assert 'No cart plan yet' in markup
    assert 'buy-list-download' not in markup
    assert 'All items are cleared' not in markup
    assert 'No items in the ledger yet' in markup


def test_hostile_and_long_content_stays_text_in_all_views():
    a = analysis()
    payload = '</td></tr></table><script>window.GROCERY_INJECTED=1</script>' + 'x' * 2000
    a['items'][0]['name'] = payload
    a['items'][0]['notes'] = payload
    a['dietary_evaluations'][0]['item'] = payload
    markup = render_dashboard(a)
    assert payload not in markup
    assert '&lt;script&gt;window.GROCERY_INJECTED=1&lt;/script&gt;' in markup
    assert markup.count("<script>") == markup.count("</script>") >= 1
