# Context Snapshot: Grocery Flywheel Implementation Plan

Created: 2026-05-26T05:29:23Z

## Task Statement

Create a full `$ralplan` implementation plan for Grocery Flywheel.

## Desired Outcome

Produce a consensus-ready implementation plan that can be handed to `$ralph`, `$team`, or `$ultragoal` without restarting discovery. The plan must cover the first real MVP, not only the current static prototype.

## Known Facts / Evidence

- The repo is private and lives at `/Users/simongonzalezdecruz/workspaces/grocery-flywheel`.
- Current scaffold includes CLI, analysis core, static dashboard renderer, retailer adapter validation, sample data, and tests.
- Product decision register exists at `docs/DECISION_REGISTER.md`.
- First wow result is estimated savings plus sourcing alternatives, not restock draft or stockout prevention first.
- Default setup path is retailer history import; receipt/manual/photo/in-person are fallback paths.
- Retailers must use a reusable adapter architecture, not one-off hardcoded connectors.
- Grocery scope includes food plus household consumables, cleaning supplies, paper goods, toiletries, pet supplies, basic pharmacy, and other recurring store items.
- Dietary restrictions are a broad optimization path; allergies are a safety-critical subset.
- Checkout requires direct hard approval. Cart mutation must be visible, reversible, and logged.
- Platform decision inferred: CLI for development, local web app for product, hosted web app for testers, mobile-responsive/PWA baseline, browser extension only if needed for retailer import.

## Constraints

- Do not make the repo public without explicit permission.
- Preserve local-first privacy posture.
- Do not store retailer passwords.
- Do not bypass retailer access controls or anti-bot systems.
- Keep purchase submission out of MVP.
- Build for immediate user value: retailer import -> savings/sourcing dashboard.
- Must remain accessible, human-readable, and high-quality enough for testers.

## Unknowns / Open Questions

- Exact frontend framework is not selected.
- Exact browser-assisted import method is not selected.
- Hosted beta infrastructure is not selected.
- Whether Vons/Albertsons becomes a private fixture only or first live adapter remains implementation detail, not architecture.
- Dietary restrictions module depth can expand after MVP.

## Likely Codebase Touchpoints

- `src/grocery_flywheel/core.py`
- `src/grocery_flywheel/render.py`
- `src/grocery_flywheel/cli.py`
- `src/grocery_flywheel/retailer_adapter.py`
- `examples/sample_state.json`
- `examples/retailer_profiles.json`
- `tests/test_core.py`
- `docs/DECISION_REGISTER.md`
- `docs/RETAILER_ADAPTERS.md`
- `docs/SOURCING_RESEARCH_STAGE.md`
- `docs/DIETARY_RESTRICTIONS_MODULE.md`
- `docs/PRIVACY_SECURITY_BASELINE.md`
- `DESIGN.md`

