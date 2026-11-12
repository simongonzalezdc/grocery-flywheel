"""Round-10 contracts: one count sentence in the sticky banner, honest stacked money.

The round-9 review found two regressions the r9 delta introduced: at 761-1439px
the banner rendered both the compact counts and the full verdict sentence (so
sample/long read "0 of 13 cleared · 13 of 13 not cleared. 13 of 13 items are
not cleared." and mixed doubled its blocked sentence), and the tabular
``text-align:right`` on money columns leaked into the stacked mobile ledger, so
Spend/Price labels and values zig-zagged against every other cell.

Each test below binds one of those to the renderer or the committed CSS contract.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from grocery_flywheel.core import analyze_state
from grocery_flywheel.importers import import_normalized_history
from grocery_flywheel.render import render_dashboard
from test_dashboard_round7 import mixed_state, sample_state

REPO_ROOT = Path(__file__).resolve().parent.parent


def _css(markup: str) -> str:
    return markup.split("<style>")[1].split("</style>")[0]


def _media_block(css: str, header: str) -> str:
    return css.split(header + " {", 1)[1].split("\n}", 1)[0]


def _status_spans(markup: str) -> tuple[str, str]:
    status = re.search(r"<p class='masthead-status[^']*'>(.*?)</p>", markup)
    assert status is not None
    compact = re.search(r"<span class='status-compact'>(.*?)</span>", status.group(1))
    verdict = re.search(r"<span class='status-verdict'>(.*?)</span>", status.group(1))
    assert compact is not None and verdict is not None
    return compact.group(1), verdict.group(1)


# --- B1: exactly one count sentence at every width ------------------------

def test_compact_status_omits_the_zero_cleared_bucket():
    compact, verdict = _status_spans(render_dashboard(analyze_state(sample_state())))
    # Nothing is cleared in the sample fixture; the compact form must not print
    # a zero bucket (r9 B1 measured "0 of 13 cleared · 13 of 13 not cleared.").
    assert compact == "13 of 13 not cleared."
    assert "0 of" not in compact
    # The full sentence keeps the same one-fact shape for the middle band.
    assert verdict.strip() == "13 of 13 items are not cleared."


def test_compact_status_keeps_a_real_cleared_bucket():
    # A warn-tier fixture with one current-evidence safe item and no blocker
    # takes the non-blocked branch, where the cleared bucket must survive.
    state = json.loads((REPO_ROOT / "examples" / "sample_state.json").read_text())
    state["dietary_profiles"] = [{
        "profile_id": "fixture", "label": "Sanitized household",
        "restrictions": [{"value": "peanut_allergy", "safety_tier": "critical",
                          "behavior": "warn"}],
    }]
    state["items"][0]["product_evidence"] = [{
        "evidence_type": "label", "source": "sanitized label",
        "checked_date": state["as_of"], "ingredients": ["oats"],
        "allergen_statements": [], "certifications": [],
    }]
    compact, _verdict = _status_spans(render_dashboard(analyze_state(state)))
    assert compact == "1 of 13 cleared &middot; 12 of 13 not cleared."
    assert "0 of" not in compact


def test_blocked_status_states_the_blocked_count_without_a_zero_bucket():
    compact, verdict = _status_spans(render_dashboard(analyze_state(mixed_state())))
    assert compact == "1 item blocked &middot; 12 of 13 not cleared."
    assert "0 of" not in compact
    assert "1 item is blocked" in verdict
    payload = json.loads((REPO_ROOT / "examples" / "imports" / "example-history.json").read_text())
    canonical_compact, _canonical_verdict = _status_spans(
        render_dashboard(analyze_state(import_normalized_history(payload))))
    assert canonical_compact.startswith("1 item blocked")
    assert "0 of" not in canonical_compact


def test_every_width_renders_exactly_one_of_the_two_count_spans():
    css = _css(render_dashboard(analyze_state(sample_state())))
    desktop = _media_block(css, "@media (max-width:760px)")
    middle = _media_block(css, "@media (min-width:761px) and (max-width:1439px)")
    wide = _media_block(css, "@media (min-width:1440px)")
    # Mutually exclusive coverage: mobile hides the verdict, the middle band
    # hides the compact counts, and >=1440 hides the verdict again.
    assert ".masthead-status .status-verdict { display:none; }" in desktop
    assert ".masthead-status .status-compact { display:none; }" in middle
    assert ".masthead-status .status-verdict { display:none; }" in wide
    # The bands are contiguous, so no width is left rendering both spans.
    assert "@media (max-width:760px)" in css
    assert "@media (min-width:761px) and (max-width:1439px)" in css
    assert "@media (min-width:1440px)" in css
    # And each markup carries one of each span (one hidden at any given width).
    markup = render_dashboard(analyze_state(mixed_state()))
    assert markup.count("class='status-compact'") == 1
    assert markup.count("class='status-verdict'") == 1


# --- B2: money alignment is tabular-only ---------------------------------

def test_stacked_ledger_resets_the_money_alignment():
    markup = render_dashboard(analyze_state(sample_state()))
    css = _css(markup)
    stacked = _media_block(css, "@media (max-width:820px)")
    assert ".ledger td.money-col, .ledger td.money-col::before { text-align:left; }" in stacked
    # The right-alignment survives where the table is still a table.
    assert ".money-col, th.money-col { text-align:right; }" in css
    assert ".money-col, th.money-col { text-align:right; }" not in stacked
