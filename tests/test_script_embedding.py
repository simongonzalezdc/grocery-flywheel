"""Regression: data can never break out of markup or a <script> block.

An item name containing ``</script><script>...`` used to break out of the
correction-capture payload and execute attacker JS when the dashboard was
opened (found by adversarial QA, 2026-08-14). The renderer now keeps data in
escaped HTML text/attributes only, and the native wrapper authorizes every
inline script by hash.
"""

from __future__ import annotations

import re
from html import escape

from grocery_flywheel.core import analyze_state
from grocery_flywheel.rendering import render_dashboard

_CONSENT = {"correction_telemetry": "local_only", "hosted_sync": False,
            "retailer_session_storage": "none", "password_storage": "forbidden"}

_STATE = {
    "as_of": "2026-06-10",
    "order": {"store": "S", "date": "2026-06-01", "total": 5.0},
    "consent": _CONSENT,  # consent present → correction capture panel renders
}


def test_item_name_cannot_break_out_of_scripts_or_markup():
    payload = "</script><script>alert('pwned')//"
    state = dict(_STATE)
    state["items"] = [{"name": payload, "spend": 1.0}]
    html = render_dashboard(analyze_state(state))
    assert "</script><script>" not in html
    # It appears only as inert escaped text in the select and the ledger.
    assert escape(payload) in html
    # Every script block is a fixed, data-free literal from the renderer.
    for block in re.findall(r"<script>(.*?)</script>", html, re.S):
        assert "pwned" not in block
        assert "alert(" not in block


def test_payload_survives_unicode_line_separators():
    state = dict(_STATE)
    state["items"] = [{"name": "evil" + chr(0x2028) + "linesep" + chr(0x2029), "spend": 1.0}]
    html = render_dashboard(analyze_state(state))
    for block in re.findall(r"<script>(.*?)</script>", html, re.S):
        assert chr(0x2028) not in block and chr(0x2029) not in block


def test_body_panels_still_escape_html():
    state = dict(_STATE)
    state["items"] = [{"name": "<img src=x onerror=alert(1)>", "spend": 1.0}]
    html = render_dashboard(analyze_state(state))
    markup = html.split("<script>")[0] + html.rsplit("</script>", 1)[-1]
    assert "<img src=x" not in markup
    assert "&lt;img src=x" in markup


def test_no_storage_or_network_api_is_reachable_from_the_page():
    html = render_dashboard(analyze_state(_STATE))
    for token in ("localStorage", "sessionStorage", "indexedDB", "fetch(", "XMLHttpRequest",
                  "sendBeacon", "WebSocket", "EventSource", "importScripts", "http://", "https://"):
        assert token not in html, token
    assert "<link" not in html and "<img" not in html


def test_renderer_emits_only_fixed_script_bodies():
    """Every script body is a renderer literal; no household data is interpolated."""
    state = dict(_STATE)
    state["items"] = [{"name": "x", "spend": 1.0, "consumed_fraction": 1.0}]
    document = render_dashboard(analyze_state(state))
    scripts = re.findall(r"<script>(.*?)</script>", document, re.S)
    assert scripts and all("dataset.plan" in block or "log.map" in block for block in scripts)

