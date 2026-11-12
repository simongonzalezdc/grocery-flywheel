#!/usr/bin/env python3
"""Build an offline self-contained native plugin from this repository's engine."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def build(output):
    target = Path(output) / "grocery-flywheel"
    target.mkdir(parents=True, exist_ok=False)
    for path in sorted((ROOT / "integrations/hermes").rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            relative = path.relative_to(ROOT / "integrations/hermes")
            dest = target / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dest)
    engine = target / "engine/grocery_flywheel"
    shutil.copytree(ROOT / "src/grocery_flywheel", engine,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (target / "engine/__init__.py").write_text("")
    (target / "examples").mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "examples/sample_state.json", target / "examples/sample_state.json")
    shutil.copyfile(ROOT / "LICENSE", target / "LICENSE")
    stray = [str(p.relative_to(target)) for p in target.rglob("*")
             if p.is_file() and ("__pycache__" in p.parts or p.suffix == ".pyc")]
    if stray:
        raise SystemExit("bundle would ship cache files: " + ", ".join(stray[:5]))
    hashes = {str(p.relative_to(engine)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(engine.rglob("*")) if p.is_file()}
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    manifest = {"source_commit": sha, "engine_files": hashes,
                "bundle_files": {str(p.relative_to(target)): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sorted(target.rglob("*")) if p.is_file()}}
    (target / "ENGINE-MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    print(build(parser.parse_args().output))
