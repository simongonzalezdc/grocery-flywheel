"""Presentation contracts: truthful state, retained evidence and local exports."""
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


def test_review_precedes_metrics_and_evidence_is_available():
    a = analysis()
    before = deepcopy(a)
    markup = render_dashboard(a)
    assert a == before
    assert markup.index('Dietary Restrictions') < markup.index('Review your next grocery run') < markup.index('Known Depletion')
    assert 'Complete household ledger — all items and evidence' in markup
    assert 'reviewing does not record approval' in markup
    assert 'does not save approvals' in markup
    for row in a['items']:
        from html import escape
        assert escape(row['name']) in markup
    cells = [attrs for tag, attrs in Document(markup).tags if tag == 'td']
    assert cells and all(row.get('data-label') for row in cells)


@pytest.mark.parametrize('consent,visible', [(None, False), ({}, False),
    ({'correction_telemetry': 'disabled'}, False),
    ({'correction_telemetry': 'local_only'}, True),
    ({'correction_telemetry': 'hosted_opt_in'}, True)])
def test_consent_is_not_granted_by_presentation(consent, visible):
    a = analysis()
    a['consent'] = consent
    markup = render_dashboard(a)
    assert ('id="correction-item"' in markup) is visible
    if visible:
        assert 'nothing is saved to household state' in markup
        assert '<label for="correction-item">' in markup


def test_download_contains_actual_draft_not_prototype_sample():
    a = analysis()
    a['order']['store'] = 'Different sanitized store'
    markup = render_dashboard(a)
    attrs = next(attrs for tag, attrs in Document(markup).tags if attrs.get('id') == 'buy-list-download')
    assert json.loads(attrs['data-plan']) == a['cart_plan']
    assert json.loads(attrs['data-plan'])['approval_required'] is True
    assert json.loads(attrs['data-plan'])['checkout_available'] is False


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


def test_hostile_and_long_content_stays_text_in_all_views():
    a = analysis()
    payload = '</td></tr></table><script>window.GROCERY_INJECTED=1</script>' + 'x' * 2000
    a['items'][0]['name'] = payload
    a['items'][0]['notes'] = payload
    markup = render_dashboard(a)
    assert payload not in markup
    assert '&lt;script&gt;window.GROCERY_INJECTED=1&lt;/script&gt;' in markup
    assert 'data-label="Notes"' in markup
