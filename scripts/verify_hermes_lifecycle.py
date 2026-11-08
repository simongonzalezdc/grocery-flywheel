#!/usr/bin/env python3
"""Isolated CLI enable/remove/reinstall and fresh-process dispatch receipt."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

PROBE = r'''
import json
from hermes_cli.plugins import PluginManager
from hermes_cli.plugin_command_dispatch import invoke_plugin_command
from tools.registry import registry
from hermes_cli.version_info import get_version_info
identity=get_version_info()
if identity.base_version == 'unknown' or identity.dirty:
 raise RuntimeError('Known clean Hermes runtime identity required')
m=PluginManager();m.discover_and_load()
names=sorted(x for x in registry._merged_tools(m.scope_key) if x.startswith('grocery_'))
result={'tools':names,'slash':'grocery' in m._plugin_commands,'skill':m.find_plugin_skill('grocery-flywheel:grocery') is not None}
if result['slash']:
 result['sample']=json.loads(invoke_plugin_command(m._plugin_commands['grocery']['handler'],'sample',source='cli'))['ok']
 result['named']=json.loads(registry.dispatch('grocery_analyze',{'state_name':'sample.json'},scope=m.scope_key))['ok']
print('GROCERY_RECEIPT='+json.dumps(result))
'''


def main(bundle, scratch):
    scratch.mkdir(parents=True, exist_ok=False)
    home = scratch / "profile"
    home.mkdir(mode=0o700)
    env = dict(os.environ, HERMES_HOME=str(home), PYTHONDONTWRITEBYTECODE="1")
    for key in list(env):
        if key.startswith("HERMES_KANBAN_") or key in ("HERMES_PROFILE", "HERMES_SAFE_MODE", "HERMES_SAFE_WORKER"):
            env.pop(key, None)
    receipts = []

    def execute(argv):
        result = subprocess.run([sys.executable, *argv], env=env, text=True, capture_output=True, timeout=60)
        receipts.append({"argv": [sys.executable, *argv], "exit": result.returncode,
                         "stdout": result.stdout, "stderr": result.stderr})
        (scratch / "lifecycle.json").write_text(json.dumps(receipts, indent=2))
        if result.returncode:
            raise RuntimeError("Host command failed; see lifecycle.json")
        return result.stdout

    def probe(enabled):
        text = execute(["-c", PROBE])
        receipt = json.loads(next(x for x in text.splitlines() if x.startswith("GROCERY_RECEIPT=")).split("=", 1)[1])
        if receipt["slash"] != enabled or receipt["skill"] != enabled or len(receipt["tools"]) != (5 if enabled else 0):
            raise RuntimeError("Fresh-process registration mismatch")
        if enabled and not (receipt["sample"] and receipt["named"]):
            raise RuntimeError("Fresh-process sample/named dispatch failed")

    target = home / "plugins/grocery-flywheel"
    shutil.copytree(bundle, target)
    # Explicit sanitized user import, independent of plugin execution.
    data = home / "plugin-data/grocery-flywheel/state"
    data.mkdir(mode=0o700, parents=True)
    data.parent.chmod(0o700)
    data.parent.parent.chmod(0o700)
    source = (bundle / "examples/sample_state.json").read_bytes()
    (data / "sample.json").write_bytes(source)
    (data / "sample.json").chmod(0o600)
    probe(False)
    for verb in ("doctor", "validate"):
        execute(["-m", "hermes_cli.main", "plugins", verb, str(target), *(["--ci"] if verb == "doctor" else [])])
    execute(["-m", "hermes_cli.main", "plugins", "list"])
    execute(["-m", "hermes_cli.main", "plugins", "enable", "grocery-flywheel"])
    execute(["-m", "hermes_cli.main", "plugins", "list"])
    probe(True)
    execute(["-m", "hermes_cli.main", "plugins", "disable", "grocery-flywheel"])
    probe(False)
    execute(["-m", "hermes_cli.main", "plugins", "remove", "grocery-flywheel"])
    if target.exists() or (data / "sample.json").read_bytes() != source:
        raise RuntimeError("Code-only removal did not preserve data")
    probe(False)
    shutil.copytree(bundle, target)
    execute(["-m", "hermes_cli.main", "plugins", "enable", "grocery-flywheel"])
    probe(True)
    execute(["-m", "hermes_cli.main", "plugins", "disable", "grocery-flywheel"])
    # An incompatible installed manifest must be refused by the real host.
    manifest = target / "plugin.yaml"
    manifest.write_text(manifest.read_text().replace('>=0.23.0', '>=999.0.0'))
    result = subprocess.run([sys.executable, "-m", "hermes_cli.main", "plugins", "enable", "grocery-flywheel"],
                            env=env, text=True, capture_output=True, timeout=60)
    receipts.append({"version_gate_argv": ["plugins", "enable", "grocery-flywheel"],
                     "exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
    (scratch / "lifecycle.json").write_text(json.dumps(receipts, indent=2))
    probe(False)
    gate_message = result.stdout + result.stderr
    if "999" not in gate_message:
        raise RuntimeError("Host did not explain incompatible requires_hermes")
    print(json.dumps({"ok": True, "commands": len(receipts), "receipt": str(scratch / "lifecycle.json")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--scratch", required=True, type=Path)
    args = parser.parse_args()
    main(args.bundle.resolve(), args.scratch.resolve())
