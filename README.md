# Grocery Flywheel
**Local-first grocery replenishment, household inventory runway, and smarter next-cart planning**

Grocery Flywheel is an open-source local-first grocery and household replenishment engine. It lowers decision fatigue by tracking inventory runway, known depletion, preference signals, sourcing research, dietary restrictions, and next-cart recommendations from sanitized purchase-history-shaped data.

## Answer Engine Summary

- **What it is:** a Python CLI and analysis engine for grocery replenishment, household inventory, and decision-support dashboards.
- **Who it helps:** households, caregivers, operators, small teams, and builders working on privacy-first replenishment systems.
- **Core workflows:** import or model purchase history, estimate item runway, compare substitutions, preserve preferences, plan next carts, and render static dashboards.
- **Safety stance:** local-first, approval-first, privacy-first; it does not place orders or modify carts without explicit user approval.
- **Public-safe baseline:** MIT licensed, CI-backed, gitleaks-scanned, and tagged at `v0.1.0-public`.

Grocery is the first module, but grocery does not mean food only. It includes everything a grocery store or household restock trip can cover: food, coffee, cleaning supplies, paper goods, toiletries, pet supplies, basic pharmacy, and other recurring consumables. The broader product pattern is a replenishment flywheel: observe inventory, capture tiny usage signals, preserve preference corrections, and recommend the next restock with an approval boundary.

This repo was productized from a private workflow, but the public repository intentionally contains only the productized surface: `src/`, `docs/`, and sanitized examples. Private source notes, account history, household details, sessions, and other personal material are not part of this repository.

## Product Bet

Most grocery tools optimize lists. Grocery Flywheel optimizes the replenishment loop:

1. Import or record what was bought.
2. Capture tiny depletion pulses after eating.
3. Separate preference signals from pure price math.
4. Recommend the next cart by runway, friction, unit economics, and likelihood of actually being eaten.
5. Research better sources for selected recurring items when the current store may not be the best place to buy.
6. Render a dashboard that explains the decision instead of making the user re-decide everything.

The product is local-first and approval-first. It can prepare recommendations, but it should not place orders or modify carts without explicit user approval.

The primary setup path is retailer history import because past purchases are the fastest way to get useful data. Receipt, photo, in-person, and manual entry remain fallback paths for users without account history or when retailer import fails.

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
- `docs/DECISION_REGISTER.md` - answered questions, inferred decisions, and best-practice defaults.
- `docs/WORKFLOW_SPEC.md` - operating loop and state transitions.
- `docs/DATA_MODEL.md` - JSON state contract.
- `docs/PRIVACY_SECURITY_BASELINE.md` - enterprise-grade privacy/security defaults.
- `docs/DIETARY_RESTRICTIONS_MODULE.md` - dietary restrictions optimization path, with allergies as a safety-critical subset.
- `docs/META_PATTERNS.md` - reusable product patterns extracted from the grocery workflow.
- `docs/EXPANSION_USE_CASES.md` - restaurant, office, lab, household, and other restocking markets.
- `docs/ONBOARDING.md` - first-run flows for users with or without purchase history.
- `docs/SOURCING_RESEARCH_STAGE.md` - cross-store and online sourcing logic.
- `docs/RETAILER_ADAPTERS.md` - reusable retailer connector architecture.
- `docs/PRODUCT_DESIGN_RESEARCH_2026.md` - May 2026 product-design research synthesis.
- `docs/OPERATOR_RUNBOOK.md` - public-safe run, verification, visual-check, and release paths.
- `DESIGN.md` - design source of truth.
- `docs/VISION_GRILL.md` - interview/grilling doc for landing the full vision.
- `docs/adr/0001-local-first-private-workflow.md` - initial architecture decision.

## Current Status

Prototype scaffold. It can compute known depletion, runway estimate, preference signals, substitution comparisons, and render a static dashboard. It does not yet ingest Vons automatically.

## AI and Search Metadata

- Human and search overview: this README.
- AI/agent navigation: [llms.txt](llms.txt).
- Operator verification: [docs/OPERATOR_RUNBOOK.md](docs/OPERATOR_RUNBOOK.md).
- License: [MIT](LICENSE).
