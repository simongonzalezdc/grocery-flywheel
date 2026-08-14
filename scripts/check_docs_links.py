#!/usr/bin/env python3
"""Check that every relative markdown link and llms.txt pointer resolves.

Runs in CI (both pipelines) so a doc rename can never dangle silently.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LINK_RE = re.compile(r"\]\(([^)#\s]+)(?:#[^)\s]*)?\)")
errors: list[str] = []

md_files = sorted(REPO.rglob("*.md"))
md_files = [p for p in md_files if ".venv" not in p.parts and "node_modules" not in p.parts]

for md in md_files:
    rel_root = md.parent
    for target in LINK_RE.findall(md.read_text()):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        candidate = (rel_root / target).resolve()
        if not candidate.exists():
            errors.append(f"{md.relative_to(REPO)}: dangling link -> {target}")

for line_no, line in enumerate((REPO / "llms.txt").read_text().splitlines(), 1):
    for target in re.findall(r"(?:^|[-:] )(\w[\w./-]*\.(?:md|html|txt))", line):
        if not (REPO / target).exists():
            errors.append(f"llms.txt:{line_no}: dangling pointer -> {target}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"docs link check passed ({len(md_files)} markdown files scanned)")
