#!/usr/bin/env python3
"""Exercise a staged bundle through the installed Hermes host (no model calls).

Run with the chosen Hermes runtime interpreter and its source on PYTHONPATH.
Every report assertion is an observed check, not an acceptance waiver.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys


def run(bundle, scratch, offline):
    require = check
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
    long_state["items"][-1]["notes"] = "Sanitized long note " + "y" * 2500
    variants["long"] = long_state
    for label, state in variants.items():
        response = call("grocery_dashboard", {"state_json": json.dumps(state)})
        require(response.get("ok"), label + " native dashboard")
        output = home / "plugin-data/grocery-flywheel" / response["data"]["artifact"]
        shutil.copyfile(output, scratch / (label + "-dashboard.html"))
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
