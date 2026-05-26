# Grocery Flywheel

Local-first grocery operations for lowering decision fatigue, tracking pantry runway, and turning real purchase history into better next carts.

This repo was productized from a private brain-dump workflow. The original source notes are copied under `source-material/private-brain-dump-snapshot/` for traceability. The product surface lives in `src/`, `docs/`, and `examples/`.

## Product Bet

Most grocery tools optimize lists. Grocery Flywheel optimizes the loop:

1. Import or record what was bought.
2. Capture tiny depletion pulses after eating.
3. Separate preference signals from pure price math.
4. Recommend the next cart by runway, friction, unit economics, and likelihood of actually being eaten.
5. Render a dashboard that explains the decision instead of making the user re-decide everything.

The product is local-first and approval-first. It can prepare recommendations, but it should not place orders or modify carts without explicit user approval.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m grocery_flywheel.cli examples/sample_state.json --output dist/sample-dashboard.html
pytest
```

Open `dist/sample-dashboard.html` in a browser to see the generated dashboard.

## Repo Map

- `src/grocery_flywheel/` - small standard-library CLI and analysis engine.
- `examples/sample_state.json` - sanitized example state based on the original workflow shape.
- `docs/PRD.md` - product requirements and MVP boundary.
- `docs/WORKFLOW_SPEC.md` - operating loop and state transitions.
- `docs/DATA_MODEL.md` - JSON state contract.
- `docs/VISION_GRILL.md` - interview/grilling doc for landing the full vision.
- `docs/adr/0001-local-first-private-workflow.md` - initial architecture decision.
- `source-material/private-brain-dump-snapshot/` - copied private source material.

## Current Status

Prototype scaffold. It can compute known depletion, runway estimate, preference signals, substitution comparisons, and render a static dashboard. It does not yet ingest Vons automatically.

