#!/usr/bin/env python3
"""Exercise a staged bundle through the installed Hermes host (no model calls).

Run with the chosen Hermes runtime interpreter and its source on PYTHONPATH.
Every report assertion is an observed check, not an acceptance waiver.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys


def run(bundle, scratch, offline):
    require = check
    manifest = json.loads((bundle / "ENGINE-MANIFEST.json").read_text())
    present = {str(p.relative_to(bundle)) for p in bundle.rglob("*") if p.is_file()}
    unmanifested = sorted(present - set(manifest["bundle_files"]) - {"ENGINE-MANIFEST.json"})
    require(not unmanifested, "bundle has no unmanifested files: " + ", ".join(unmanifested[:5]))
    require(not [p for p in present if "__pycache__" in p or p.endswith(".pyc")],
            "bundle ships no bytecode caches")
    home = scratch / "profile-a"
    home.mkdir(parents=True, exist_ok=False)
    os.environ["HERMES_HOME"] = str(home)
    for key in list(os.environ):
        if key.startswith("HERMES_KANBAN_") or key in ("HERMES_PROFILE", "HERMES_SAFE_MODE", "HERMES_SAFE_WORKER"):
            os.environ.pop(key, None)
    (home / "plugins").mkdir()
    target = home / "plugins/grocery-flywheel"
    shutil.copytree(bundle, target)
    from hermes_cli.plugins import PluginManager
    from tools.registry import registry
    from hermes_cli.plugin_command_dispatch import invoke_plugin_command
    from hermes_cli.version_info import get_version_info
    identity = get_version_info()
    require(identity.base_version != "unknown" and not identity.dirty,
            "known clean runtime identity required")
    if offline:
        def forbidden(*args, **kwargs):
            raise AssertionError("Plugin attempted network/subprocess")
        socket.socket.connect = forbidden
        socket.create_connection = forbidden
        socket.getaddrinfo = forbidden
        subprocess.Popen = forbidden
    manager = PluginManager()
    manager.discover_and_load()
    require("grocery" not in manager._plugin_commands, "disabled before enable")
    (home / "config.yaml").write_text('plugins:\n  enabled: [grocery-flywheel]\n')
    manager.discover_and_load(force=True)
    entries = manager._plugin_commands
    require("grocery" in entries, "slash registered")
    registered = sorted(name for name in registry._merged_tools(manager.scope_key) if name.startswith("grocery_"))
    expected = sorted("grocery_" + x for x in ("analyze", "dietary", "sourcing", "plan", "dashboard"))
    require(registered == expected, "exact five native tools")
    from tools.registry import session_tool_scope
    with session_tool_scope(manager.scope_key):
        require(registry.get_tool_names_for_toolset("grocery") == expected, "grocery toolset exposed")
        require(sorted(row["function"]["name"] for row in registry.get_definitions(set(expected))) == expected,
                "five model-visible native schemas")
    skill = manager.find_plugin_skill("grocery-flywheel:grocery")
    require(skill is not None, "namespaced skill discovered")
    # Read through the host skill loader, not just the registration table.
    from tools.skills_tool import skill_view
    loaded = skill_view("grocery-flywheel:grocery")
    require("Grocery Flywheel" in str(loaded), "namespaced skill loaded")
    handler = entries["grocery"]["handler"]
    def call(name, args):
        return json.loads(registry.dispatch(name, args, scope=manager.scope_key))

    def slash(args):
        return invoke_plugin_command(handler, args, source="cli")
    sample = (target / "examples/sample_state.json").read_text()
    results = {}
    require("No checkout" in slash("help") or "No checkout" in slash("help").capitalize(), "slash help")
    require(json.loads(slash("status"))["checkout_available"] is False, "slash status")
    require(json.loads(slash("sample"))["ok"], "slash sample")
    # Explicit manual sanitized import; no plugin mutation API.
    state_dir = home / "plugin-data/grocery-flywheel/state"
    state_dir.mkdir(parents=True, mode=0o700)
    for parent in (state_dir.parent, state_dir.parent.parent):
        parent.chmod(0o700)
    (state_dir / "sample.json").write_text(sample)
    (state_dir / "sample.json").chmod(0o600)
    for name in expected:
        result = call(name, {"state_name": "sample.json"})
        require(result.get("ok"), name + " native success: " + str(result.get("error")))
        results[name] = result
        routed = json.loads(slash(name.removeprefix("grocery_") + ' {"state_name":"sample.json"}'))
        require(routed.get("ok"), name + " slash success")
    plan = results["grocery_plan"]["data"]
    require(plan["approval_required"] is True and plan["checkout_available"] is False, "approval boundary")
    require(all(x["approval_state"] == "needs_human_approval" for x in plan["items"]), "all rows approval")
    # Unit seam is deliberately used only for corruption/security probes.
    module = sys.modules[handler.__module__]
    tools = sys.modules[module.__package__ + ".tools"]
    from unittest.mock import patch
    for bad in ({}, {"state_json": sample, "state_name": "sample.json"}, {"state_path": "/etc/passwd"},
                {"state_json": "[]"}, {"state_json": '{"x":1,"x":2}'}, {"state_json": '{"x":NaN}'},
                {"state_json": sample, "unknown": True}, {"state_name": "../sample.json"},
                {"state_name": "/etc/passwd"}, {"state_name": "C:\\state.json"},
                {"state_name": "%2e%2e.json"}, {"state_name": "\\\\host\\state.json"}):
        for name in expected:
            require(call(name, bad).get("ok") is False, "invalid native input")
    for name in ("grocery_dietary", "grocery_plan"):
        require(not call(name, {"state_json": sample, "objective": "not-real"})["ok"], "invalid objective")
    require(not call("grocery_plan", {"state_json": sample, "mode": "checkout"})["ok"], "invalid mode")
    sentinel = scratch / "sentinel.json"
    sentinel.write_text(sample)
    (state_dir / "linked.json").symlink_to(sentinel)
    require(call("grocery_analyze", {"state_name": "linked.json"})["error"]["code"] == "UNSAFE_PATH", "symlink rejected")
    os.mkfifo(state_dir / "fifo.json")
    require(call("grocery_analyze", {"state_name": "fifo.json"})["error"]["code"] == "UNSAFE_PATH", "FIFO rejected")
    original = tools.HANDLERS["grocery_plan"]
    corruptions = [dict(plan, checkout_available=True), dict(plan, approval_required=False),
                   dict(plan, items=[{"approval_state": "approved"}])]
    for corrupt in corruptions:
        with patch.dict(tools.HANDLERS, {"grocery_plan": lambda args, value=corrupt: value}):
            require(call("grocery_plan", {"state_json": sample})["error"]["code"] == "APPROVAL_BOUNDARY", "corrupt draft rejected")
    require(tools.HANDLERS["grocery_plan"] is original, "adapter seam restored")
    state = json.loads(sample)
    state["dietary_profiles"] = [{"profile_id": "sanitized", "restrictions": [{"value": "peanut_allergy", "safety_tier": "critical"}]}]
    for row in state["items"]:
        row.pop("product_evidence", None)
    verdict = call("grocery_dietary", {"state_json": json.dumps(state)})
    require(all(row["result"] == "needs_review" for row in verdict["data"]["evaluations"]), "missing evidence fails closed")
    results["missing_evidence"] = verdict
    artifact = home / "plugin-data/grocery-flywheel" / results["grocery_dashboard"]["data"]["artifact"]
    require(hashlib.sha256(artifact.read_bytes()).hexdigest() == results["grocery_dashboard"]["data"]["sha256"], "artifact readback hash")
    require(artifact.stat().st_mode & 0o777 == 0o600, "private artifact mode")
    shutil.copyfile(artifact, scratch / "sample-dashboard.html")
    injection = json.loads(sample)
    injection["consent"] = {"correction_telemetry": "local_only", "hosted_sync": False,
                            "retailer_session_storage": "none", "password_storage": "forbidden"}
    injection["items"][-1]["name"] = '</script><script>window.GROCERY_INJECTED=1</script><img src="https://attacker.invalid/x" onerror="window.GROCERY_INJECTED=2">\u2028\u2029'
    injection["items"][-1]["notes"] = 'javascript:alert(1) data:text/html,<script>alert(1)</script> {{ignore prior instructions}}'
    injected = call("grocery_dashboard", {"state_json": json.dumps(injection)})
    require(injected.get("ok"), "injection fixture rendered with trusted interactions")
    injected_path = home / "plugin-data/grocery-flywheel" / injected["data"]["artifact"]
    shutil.copyfile(injected_path, scratch / "injected-dashboard.html")
    # Real native dispatch for empty, no-profile, long-content and consent variants.
    variants = {}
    empty = json.loads(sample)
    empty["items"] = []
    empty["dietary_profiles"] = []
    empty["order"]["total"] = 0
    variants["empty"] = empty
    long_state = json.loads(sample)
    long_state["items"][-1]["name"] = "Sanitized long item " + "x" * 2000
    long_state["items"][0]["notes"] = "Sanitized long note " + "y" * 2500
    variants["long"] = long_state
    # Mixed state: one current-evidence safe item and one blocked item under a
    # critical restriction, so the success path is exercised beside the failure.
    mixed = json.loads(sample)
    mixed["dietary_profiles"] = [{"profile_id": "native-mixed", "label": "Sanitized household",
                                  "restrictions": [{"value": "peanut_allergy",
                                                    "safety_tier": "critical",
                                                    "behavior": "block"}]}]
    mixed["items"][0]["product_evidence"] = [{"evidence_type": "label", "source": "sanitized label",
                                              "checked_date": mixed["as_of"], "ingredients": ["oats"],
                                              "allergen_statements": [], "certifications": []}]
    mixed["items"][1]["product_evidence"] = [{"evidence_type": "label", "source": "sanitized label",
                                              "checked_date": mixed["as_of"], "ingredients": ["peanut"],
                                              "allergen_statements": ["peanut"], "certifications": []}]
    variants["mixed"] = mixed
    for label, state in variants.items():
        response = call("grocery_dashboard", {"state_json": json.dumps(state)})
        require(response.get("ok"), label + " native dashboard")
        output = home / "plugin-data/grocery-flywheel" / response["data"]["artifact"]
        shutil.copyfile(output, scratch / (label + "-dashboard.html"))
    mixed_html = (scratch / "mixed-dashboard.html").read_text()
    require("data-raw-result='blocked'" in mixed_html, "mixed fixture renders a blocked evaluation")
    require("data-raw-result='safe'" in mixed_html, "mixed fixture exercises the cleared path")
    require("data-raw-status='safe'" in mixed_html, "mixed ledger shows an explicit clearance")
    require("Not evaluated" in mixed_html, "mixed ledger marks unevaluated items neutral")
    counts = mixed_html.split("class='attention-counts'")[1].split("</p>")[0]
    require("1 of 13 cleared" in counts and "1 blocked" in counts,
            "mixed fixture states exact cleared and blocked counts")
    # Authority invariant: every sage mark carries an explicit safe+current receipt.
    ok_spans = [span.split(">")[0] for span in mixed_html.split("class='mark ok'")[1:]]
    ok_spans = [span for span in ok_spans if "data-verdict=" in span]
    require(ok_spans and all("data-verdict='cleared'" in span
                             and "data-result='safe'" in span
                             and "data-evidence='current'" in span for span in ok_spans),
            "every sage clearance mark is an explicit safe+current verdict")
    ledger = mixed_html.split("The ledger</h2>")[1].split("</article>")[0]
    require("not recorded" in ledger and "$0.00" not in ledger,
            "unpriced placeholder renders not recorded, never a fabricated $0.00")
    require("Price · date unknown" in mixed_html,
            "a stale price with no check date is unknown, not asserted stale")
    require("set to block" in mixed_html
            and "data gap, not proof of a safety failure" not in mixed_html,
            "restriction copy derives from the configured behaviour")
    require("Sourcing candidates" in mixed_html and "2 modelled saving rows" in mixed_html,
            "sourcing card states the real candidate count")
    today = mixed_html.split("id='today'")[1].split("</article>")[0]
    require("Homestyle waffles" in today and "class='action-hold'" in today
            and "Do not buy" in today,
            "blocked item absent from the cart plan is held in the action area")
    require("data-hold='true'" in today and "data-hold='false'" in today,
            "every held page row carries data-hold and the cleared row does not")
    require("class='bar hot'" not in mixed_html and ".bar.hot" not in mixed_html,
            "drawdown bars never borrow the brick dietary token")
    require("Review 4 items before your next shop." in mixed_html
            and "Review the 4 items that need a decision" in mixed_html,
            "hero and action headline count the rows that need a decision")
    action_rows = [row.split("</li>")[0] for row in today.split("<li")[1:]]
    for row in action_rows:
        if "data-action-item=" not in row:
            continue
        verdict = re.search(r"data-verdict='([^']+)'", row)
        if verdict and verdict.group(1) != "cleared":
            require("class='action-qualifier'" in row,
                    "non-cleared action carries its dietary qualifier")
    require("Dietary evidence &middot; blocked" in mixed_html,
            "mixed fixture names its severity in text")
    # r10: one count sentence per width. The compact counts and the full verdict
    # sentence are mutually exclusive, and a zero cleared bucket is never printed.
    require(mixed_html.count("class='status-compact'") == 1
            and mixed_html.count("class='status-verdict'") == 1,
            "status line carries one compact span and one verdict span")
    mixed_compact_match = re.search(r"<span class='status-compact'>(.*?)</span>", mixed_html)
    assert mixed_compact_match is not None, "mixed dashboard carries compact status counts"
    mixed_compact = mixed_compact_match.group(1)
    require("1 item blocked" in mixed_compact and "12 of 13 not cleared" in mixed_compact,
            "compact status states the blocked row and the open count once")
    sample_html = (scratch / "sample-dashboard.html").read_text()
    sample_compact_match = re.search(r"<span class='status-compact'>(.*?)</span>", sample_html)
    assert sample_compact_match is not None, "sample dashboard carries compact status counts"
    sample_compact = sample_compact_match.group(1)
    require("0 of" not in sample_compact and "13 of 13 not cleared" in sample_compact,
            "compact status omits a zero cleared bucket")
    css = mixed_html.split("<style>")[1].split("</style>")[0]
    require("@media (min-width:761px) and (max-width:1439px)" in css
            and ".masthead-status .status-compact { display:none; }" in css
            and "@media (min-width:1440px)" in css
            and "@media (max-width:760px)" in css,
            "mutually exclusive status spans cover every width band")
    stacked_block = css.split("@media (max-width:820px)", 1)[1].split("\n}", 1)[0]
    require(".ledger td.money-col, .ledger td.money-col::before { text-align:left; }" in stacked_block,
            "stacked ledger resets money alignment with the other cells")
    # The draft is what the household reads after clicking download; it must
    # carry the same rows, the same holds and the same qualifiers as the page.
    plan_attr = re.search(r"data-plan='([^']*)'", mixed_html)
    assert plan_attr is not None, "mixed dashboard embeds its draft payload"
    check(True, "mixed dashboard embeds its draft payload")
    draft = json.loads(html.unescape(plan_attr.group(1)))
    action_list = draft["items"]
    require(draft.get("schema") == "grocery-flywheel.dashboard-draft/2",
            "draft declares the action-list schema")
    require(len(action_list) == 5, "draft action list mirrors the five rendered rows")
    require(all("engine_action" not in row for row in action_list),
            "draft items[] never copies the raw engine action token")
    keys = list(draft)
    require(keys.index("items") < keys.index("items_note")
            < keys.index("engine_plan_note") < keys.index("engine_plan")
            and keys[-1] == "engine_plan",
            "draft serializes items first and the reference plan last")
    require("hold=true" in draft["items_note"] and "held_out_of_plan=true"
            in draft["items_note"],
            "draft documents both hold flags")
    def _buy_violations(node, path="export"):
        hits = []
        if isinstance(node, dict):
            for key in ("display_action", "engine_action", "action", "instruction",
                        "buy", "restock"):
                value = node.get(key)
                if isinstance(value, str) and node.get("cleared") is not True:
                    if re.search(r"^(?!(?:do not|hold)\b).*\b(?:restock|rotate|buy|purchase)\b",
                                 value, re.I):
                        hits.append(f"{path}:{key}")
            for key, value in node.items():
                hits.extend(_buy_violations(value, f"{path}.{key}"))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                hits.extend(_buy_violations(value, f"{path}[{index}]"))
        return hits
    scope = {key: value for key, value in draft.items() if key != "engine_plan"}
    require(_buy_violations(scope) == [],
            "no action-bearing entry outside engine_plan carries a buy instruction")
    engine_plan = draft.get("engine_plan") or {}
    require(len(engine_plan.get("items") or []) == 4,
            "engine cart plan is preserved verbatim under engine_plan")
    raw_pizza = next(row for row in engine_plan["items"]
                     if row["item"] == "Rising crust pizza")
    require(raw_pizza["action"] == "restock",
            "engine plan keeps its raw action under the reference key")
    held = [row for row in action_list if row["held_out_of_plan"]]
    require(len(held) == 1 and held[0]["item"] == "Homestyle waffles"
            and held[0]["cleared"] is False and held[0]["hold"] is True
            and "peanut" in held[0]["qualifier"],
            "draft holds the peanut-blocked waffles with its reason")
    for row in action_list:
        if not row["cleared"]:
            require(row.get("hold") is True,
                    "every non-cleared draft row carries hold=true")
            require(not re.search(r"^(?!(?:do not|hold)\b).*\b(?:restock|rotate|buy|purchase)\b",
                                  str(row.get("display_action") or ""), re.I),
                    "a non-cleared draft row never carries a buy instruction")
            require(bool(row["qualifier"]),
                    "a non-cleared draft row carries its dietary qualifier")
    pizza = next(row for row in action_list if row["item"] == "Rising crust pizza")
    require(pizza["cleared"] is False and pizza["hold"] is True
            and pizza["held_out_of_plan"] is False
            and pizza["display_action"] == "Hold restock",
            "draft never restocks a non-cleared item")
    context = draft["dietary_context"]
    context_names = [row["item"] for row in context["items"]]
    require(all(row["item"] in context_names for row in action_list),
            "draft dietary context covers every action row")
    require(context["action_items_total"] == len(action_list),
            "dietary context counts the action list it names")
    require(context["engine_plan_items_total"] == len(draft["engine_plan"]["items"]),
            "dietary context counts the engine plan it names")
    require("named no item on this page" in
            context["state_legend"]["not_evaluated"]["meaning"],
            "draft legend states the orphan case, not the clearance wording")
    require("rotate into a meal" not in mixed_html,
            "no uncleared easy-food rotation copy")
    require("13 dietary evaluations" in mixed_html,
            "evidence drawer counts every evaluation")
    long_html = (scratch / "long-dashboard.html").read_text()
    require("Read the note (2520 characters)" in long_html, "long note is disclosed, not clipped")
    require("<span class='clamp-2'>" in long_html and "Sanitized long item " in long_html,
            "long item name is clamped with the full string disclosed")
    require(all("<colgroup>" in table for table in long_html.split("<table>")[1:]),
            "every table declares fixed column widths")
    empty_html = (scratch / "empty-dashboard.html").read_text()
    require("No items in the ledger yet." in empty_html, "empty state states its own copy")
    require("No dietary restriction profile configured." in empty_html, "empty state names the missing profile")
    empty_ledger = empty_html.split("The ledger</h2>")[1].split("</article>")[0]
    require("<table>" not in empty_ledger, "empty ledger renders no table")
    for consent, visible in ((None, False), ({}, False), ({"correction_telemetry": "disabled"}, False),
                             ({"correction_telemetry": "local_only"}, True),
                             ({"correction_telemetry": "hosted_opt_in"}, True)):
        state = json.loads(sample)
        if consent is None:
            state.pop("consent", None)
        else:
            state["consent"] = consent
        response = call("grocery_dashboard", {"state_json": json.dumps(state)})
        require(response.get("ok"), "consent variant native dashboard")
        output = home / "plugin-data/grocery-flywheel" / response["data"]["artifact"]
        require(('id="correction-item"' in output.read_text()) == visible, "consent visibility")
    # A consent artifact is captured for the browser run (downloads under CSP).
    consent_state = json.loads(sample)
    consent_state["consent"] = {"correction_telemetry": "local_only", "hosted_sync": False,
                                "retailer_session_storage": "none",
                                "password_storage": "forbidden"}
    response = call("grocery_dashboard", {"state_json": json.dumps(consent_state)})
    require(response.get("ok"), "consent artifact native dashboard")
    output = home / "plugin-data/grocery-flywheel" / response["data"]["artifact"]
    shutil.copyfile(output, scratch / "consent-dashboard.html")
    results["malformed_state"] = call("grocery_dashboard", {"state_json": "{"})
    require(results["malformed_state"]["ok"] is False, "malformed state returns error not dashboard")
    # Same-process profile rebinding via the supported effective-home resolver.
    second = scratch / "profile-b"
    second.mkdir(mode=0o700)
    os.environ["HERMES_HOME"] = str(second)
    require(call("grocery_analyze", {"state_name": "sample.json"})["error"]["code"] == "STATE_NOT_FOUND", "profile isolation")
    from hermes_constants import set_hermes_home_override, reset_hermes_home_override
    from concurrent.futures import ThreadPoolExecutor

    def profile_call(profile):
        token = set_hermes_home_override(profile)
        try:
            return call("grocery_analyze", {"state_name": "sample.json"})
        finally:
            reset_hermes_home_override(token)

    with ThreadPoolExecutor(max_workers=2) as pool:
        a, b = list(pool.map(profile_call, (home, second)))
    require(a.get("ok") is True and b.get("error", {}).get("code") == "STATE_NOT_FOUND",
            "same-host simultaneous context-local profile isolation")
    os.environ["HERMES_HOME"] = str(home)
    (home / "config.yaml").write_text('plugins:\n  disabled: [grocery-flywheel]\n')
    manager.discover_and_load(force=True)
    require("grocery" not in manager._plugin_commands, "disable removes command")
    require((state_dir / "sample.json").read_text() == sample, "disable preserves state")
    return {"ok": True, "checks": CHECKS, "runtime_python": sys.version,
            "runtime_version": identity.derived_version, "runtime_commit": identity.commit,
            "runtime_dirty": identity.dirty,
            "runtime_source": str(Path(__import__('hermes_cli').__file__).parent.parent),
            "results": results, "dashboard": str(scratch / "sample-dashboard.html")}


CHECKS = []


def check(condition, label):
    if not condition:
        raise AssertionError(label)
    CHECKS.append(label)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--scratch", required=True, type=Path)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    args.scratch.mkdir(parents=True, exist_ok=True)
    try:
        report = run(args.bundle.resolve(), args.scratch.resolve(), args.offline)
    except Exception as exc:
        report = {"ok": False, "checks": CHECKS, "failure": str(exc), "exception": type(exc).__name__}
        args.report.write_text(json.dumps(report, indent=2))
        raise
    args.report.write_text(json.dumps(report, indent=2))
    print(json.dumps({"ok": True, "checks": len(CHECKS), "report": str(args.report)}))
