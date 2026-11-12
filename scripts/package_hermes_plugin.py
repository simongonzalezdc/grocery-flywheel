#!/usr/bin/env python3
"""Build a clean installable bundle and a deterministic tarball.

A bundle is only installable if the engine manifest covers every file in it:
an unmanifested ``__pycache__/*.pyc`` would execute ahead of the manifest-covered
source. This script refuses to package such a directory and excludes caches by
construction instead of cleaning them afterwards.
"""
import argparse
import hashlib
import json
import tarfile
import tempfile
from pathlib import Path

import build_hermes_plugin

ROOT = Path(__file__).resolve().parents[1]


def assert_clean(target: Path) -> list[str]:
    files = sorted(str(path.relative_to(target)) for path in target.rglob("*") if path.is_file())
    stray = [name for name in files
             if "__pycache__" in Path(name).parts or name.endswith(".pyc")]
    if stray:
        raise SystemExit("refusing to package cache files: " + ", ".join(stray[:5]))
    manifest = json.loads((target / "ENGINE-MANIFEST.json").read_text())
    covered = set(manifest["bundle_files"]) | {"ENGINE-MANIFEST.json"}
    unmanifested = sorted(set(files) - covered)
    if unmanifested:
        raise SystemExit("refusing to package unmanifested files: " + ", ".join(unmanifested[:5]))
    return files


def package(output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as scratch:
        target = build_hermes_plugin.build(Path(scratch))
        files = assert_clean(target)
        with tarfile.open(output, "w:gz") as archive:
            for name in files:
                source = target / name
                info = archive.gettarinfo(str(source), arcname=f"grocery-flywheel/{name}")
                info.mtime = 0
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                with source.open("rb") as handle:
                    archive.addfile(info, handle)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(json.dumps({"ok": True, "bundle": str(output), "sha256": digest,
                      "files": len(files)}))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    package(parser.parse_args().output)
