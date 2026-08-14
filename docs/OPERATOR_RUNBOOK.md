# Grocery Flywheel Operator Runbook

This runbook is the public-safe path for running, verifying, and extending Grocery Flywheel after the June 2026 cleanup.

## Repo Boundary

This public repository should contain source code, tests, docs, and sanitized examples only.

Do not commit account history, retailer credentials, household details, receipts, private source notes, personal sessions, `.omx`, `.env`, generated local caches, or unsanitized dashboard exports.

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Operator Paths

### Render the Sample Dashboard

```bash
python -m grocery_flywheel.cli examples/sample_state.json --output dist/sample-dashboard.html
```

### Run the Installed Entrypoint

```bash
grocery-flywheel examples/sample_state.json --output dist/sample-dashboard-entrypoint.html
```

### Visual Check

Serve the generated dashboard over local HTTP before taking screenshots.

```bash
python3 -m http.server 8765 --directory dist
```

Open `http://127.0.0.1:8765/sample-dashboard.html` and confirm:

- dashboard title renders
- known depletion section renders
- runway section renders
- role summary renders
- sourcing research section renders
- dietary restrictions section renders
- data freshness section renders
- easy food section renders
- trip overhead section renders
- browser console has no errors

## Verification Gate

Run this before pushing public work.

```bash
python -m grocery_flywheel.cli examples/sample_state.json --output dist/sample-dashboard.html
grocery-flywheel examples/sample_state.json --output dist/sample-dashboard-entrypoint.html
pytest -q
```

```bash
gitleaks git . --no-banner --redact
git rev-list --objects --all | rg '(^|/)(\.omx|source-material)(/|$)' && exit 1 || true
```

If dashboard UI changed, rerun the visual check and save a screenshot.

## Release Baseline

Use annotated public tags after the verification gate passes.

```bash
git tag -a v0.1.0-public -m "Grocery Flywheel public-safe baseline"
git push origin main v0.1.0-public
```

## Working Safely

- Keep new examples fake or carefully sanitized.
- Keep retailer imports approval-first and local-first.
- Treat allergies and dietary restrictions as safety-sensitive data.
- Never add automatic cart modification or ordering without explicit user approval.


## Entrypoints (v0.2.0)

- `grocery-flywheel STATE -o OUT.html [--objective OBJ]` — render dashboard
- `grocery-flywheel import normalized|csv PAYLOAD -o STATE.json` — canonical import (fail-closed)
- `grocery-flywheel corrections add STATE --item X --signal never_again` — consent-gated
- `grocery-flywheel-capture-visit STATE --type in_store --started-at ... --duration-min N`
- `grocery-flywheel-mcp` — MCP server (5 tools: analyze, render, sourcing, evaluate_dietary, plan_next_cart)

## Gates every PR passes

- `pytest` (155+ tests; both dashboard goldens live in tests/golden/)
- `ruff check .` (pinned rule set E4/E7/E9/F)
- docs link check (relative links in markdown resolve)
- secret scanning (gitleaks in CI)
