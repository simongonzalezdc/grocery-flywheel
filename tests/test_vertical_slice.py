import json
from pathlib import Path

from grocery_flywheel.core import analyze_state
from grocery_flywheel.importers import import_normalized_history
from grocery_flywheel.render import render_dashboard


ROOT = Path(__file__).resolve().parents[1]


def test_imported_fixture_produces_first_wow_and_correction_chip():
    payload = json.loads((ROOT / "examples" / "imports" / "example-history.json").read_text())
    state = import_normalized_history(payload)
    analysis = analyze_state(state, objective="balanced_roi")
    html = render_dashboard(analysis)

    assert analysis["first_wow"]["estimated_unit_savings"] > 0
    assert analysis["sourcing_research"]
    assert "Potential Unit Savings" in html
    assert "data-correction='wrong_format'" in html
    assert "window.groceryFlywheelCreateCorrection" in html
    assert "correction-export" in html
    assert html.index("Potential Unit Savings") < html.index("Items")


def test_dashboard_contains_operator_sections():
    payload = json.loads((ROOT / "examples" / "imports" / "example-history.json").read_text())
    analysis = analyze_state(import_normalized_history(payload), objective="allergy_safe")
    html = render_dashboard(analysis)

    for text in [
        "Adapter Status",
        "Dietary Restrictions",
        "Correction Actions",
        "Evidence Drawer",
        "Internal Cart Plan",
        "checkout unavailable",
    ]:
        assert text in html


def test_dashboard_escapes_script_json_and_sanitizes_invalid_consent():
    payload = json.loads((ROOT / "examples" / "imports" / "example-history.json").read_text())
    analysis = analyze_state(import_normalized_history(payload), objective="balanced_roi")
    analysis["schema_version"] = "</script><script>window.GROCERY_XSS=1</script>"
    analysis["consent"]["correction_telemetry"] = "</script><script>window.GROCERY_XSS=2</script>"

    html = render_dashboard(analysis)

    assert "</script><script>window.GROCERY_XSS" not in html
    assert "\\u003c/script\\u003e\\u003cscript\\u003ewindow.GROCERY_XSS=1\\u003c/script\\u003e" in html
    assert 'const storage = "disabled";' in html


def test_dashboard_tolerates_missing_consent_object():
    payload = json.loads((ROOT / "examples" / "imports" / "example-history.json").read_text())
    analysis = analyze_state(import_normalized_history(payload), objective="balanced_roi")
    analysis.pop("consent")

    html = render_dashboard(analysis)

    assert 'const storage = "local_only";' in html


def test_dashboard_disables_malformed_explicit_consent():
    payload = json.loads((ROOT / "examples" / "imports" / "example-history.json").read_text())
    analysis = analyze_state(import_normalized_history(payload), objective="balanced_roi")
    analysis["consent"] = False

    html = render_dashboard(analysis)

    assert 'const storage = "disabled";' in html
    assert "data-correction='wrong_format' title='Wrong format' disabled" in html
