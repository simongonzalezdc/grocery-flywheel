"""Golden dashboard gate.

The committed golden was generated from the pre-refactor renderer
(ticket 02). A diff here means rendered output changed: either fix the
regression or, if the change is intentional, regenerate deliberately
with human review — never blindly.
"""

from __future__ import annotations

import json
from pathlib import Path

from grocery_flywheel.core import analyze_state
from grocery_flywheel.render import render_dashboard

REPO_ROOT = Path(__file__).resolve().parent.parent
GOLDEN = REPO_ROOT / "tests" / "golden" / "sample_dashboard.html"


def test_sample_dashboard_is_byte_identical_to_golden():
    state = json.loads((REPO_ROOT / "examples" / "sample_state.json").read_text())
    html = render_dashboard(analyze_state(state))
    assert html == GOLDEN.read_text(), (
        "Rendered dashboard diverged from the committed golden. "
        "If intentional: regenerate tests/golden/sample_dashboard.html "
        "and note why in the PR."
    )
