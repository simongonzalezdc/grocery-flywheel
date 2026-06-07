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
