# Ralplan: Grocery Flywheel MVP Implementation Plan

Created: 2026-05-26T05:29:23Z
Status: Consensus approved by Architect and Critic
Mode: Deliberate consensus, because the MVP touches auth/imports, privacy, dietary safety, hosted testers, and external cart boundaries.

## Requirements Summary

Build Grocery Flywheel from the current prototype into a real MVP:

- retailer adapter setup rather than one-off retailer connectors
- retailer history import as the happy path
- estimated savings plus sourcing alternatives as the first wow
- local web command center and mobile-responsive tester surface
- approval-safe cart/restock draft guidance
- dietary restrictions optimization path, with allergies as safety-critical subset
- privacy/security baseline suitable for hosted testers

Grounding evidence:

- `docs/DECISION_REGISTER.md:21` says the user is first user and outside testers are personal household users.
- `docs/DECISION_REGISTER.md:22` says first wow is estimated savings plus sourcing alternatives.
- `docs/DECISION_REGISTER.md:29` infers CLI for dev, local web app for product, hosted web app for testers, mobile-responsive/PWA baseline.
- `docs/DECISION_REGISTER.md:47` defines purchase history as the first value unlock and price lookup as sourcing unlock.
- `docs/RETAILER_ADAPTERS.md:7` defines the adapter mapping into canonical objects.
- `docs/RETAILER_ADAPTERS.md:158` says Vons can be a first fixture but not the architecture.
- `docs/DIETARY_RESTRICTIONS_MODULE.md:3` states allergies are a subset of broader dietary restrictions.
- `docs/PRIVACY_SECURITY_BASELINE.md:8` requires private handling of purchase history, household inventory, dietary profiles, and retailer sessions.
- `DESIGN.md:13` defines guided setup, command center dashboard, and assistant loop as the primary surface.

## RALPLAN-DR Summary

### Principles

1. Adapter contract before retailer-specific code.
2. First wow before full restock automation.
3. Local-first and approval-first by default.
4. Human-readable evidence over black-box optimization.
5. Dietary and privacy-sensitive data receives stricter handling than normal preferences.

### Decision Drivers

1. Fast first value for testers: retailer history import -> savings/sourcing dashboard.
2. Generality: works across retailers, household categories, and future operator use cases.
3. Trust: no stored passwords, no unauthorized checkout, evidence and correction loops.

### Viable Options

#### Option A: CLI-first adapter engine, then local web app

Pros:

- Fastest path from current repo.
- Highly testable.
- Avoids auth/browser complexity while proving core model.
- Good base for hosted app later.

Cons:

- Less impressive for non-technical testers until web app arrives.
- Import UX still rough at first.

#### Option B: Local web app first, adapter engine behind it

Pros:

- Better product feel earlier.
- Lets design and onboarding be tested sooner.
- More aligned with "beautiful and easy to use."

Cons:

- Higher frontend setup cost.
- Risk of building UI before the import/sourcing engine is strong enough.

#### Option C: Browser extension first

Pros:

- Directly addresses retailer history and cart contexts.
- Could reduce import friction for supported retailers.

Cons:

- Fragile, retailer-specific, and easy to overfit.
- Slower to make general.
- Higher security and store-distribution complexity.

### Chosen Direction

Synthesis of Option A and the strongest Option B critique: define stable contracts first, then build one thin vertical slice before broad feature work. The first slice is fixture import -> canonical contracts -> savings/sourcing analysis -> mobile dashboard -> correction chip smoke. This keeps the engine testable while proving user comprehension early.

## Pre-Mortem

1. Failure: The product becomes a Vons script.
   Mitigation: keep Vons data as a private fixture only; all code paths use adapter profiles and canonical imports.

2. Failure: Testers do not reach first wow quickly.
   Mitigation: optimize setup around retailer history import, prepared fixtures, clear adapter status, and first dashboard under 5 minutes.

3. Failure: Trust breaks due to wrong cart mutation, wrong dietary warning, or privacy mishandling.
   Mitigation: no checkout, visible cart-draft approval, confidence labels, dietary `needs_review` defaults, no password storage, export/delete design.

## Architecture

### Architectural Invariants

- Stable contracts come before feature modules. Importers, sourcing, dietary checks, corrections, and dashboard rendering all depend on the same versioned canonical objects.
- Dietary safety cannot infer `safe` for safety-critical restrictions without current evidence. Missing or ambiguous evidence returns `needs_review`.
- Privacy class and consent behavior are part of the data model, not hosted-mode cleanup.
- MVP cart output is an internal `cart_plan` / `restock_draft`. External retailer cart mutation is `external_cart_draft` and requires a later ADR plus explicit user approval.

### Core Modules

- `src/grocery_flywheel/contracts.py`
  - versioned dataclass/typed-dict contracts for `OrderHistory`, `OrderItem`, `ProductIdentity`, `ProductEvidence`, `RetailerProfile`, `SourcingCandidate`, `DietaryEvaluation`, `CorrectionEvent`, and `CartPlan`
  - privacy class per sensitive field

- `src/grocery_flywheel/retailer_adapter.py`
  - existing adapter profile validation and ranking
  - expand with profile loading, capability inspection, adapter health reporting, and profile building from user-supplied store names/capabilities

- `src/grocery_flywheel/importers/`
  - normalized JSON/CSV importer
  - browser export importer later
  - email/receipt importer later

- `src/grocery_flywheel/normalization.py`
  - item identity, category, size, unit, unit price, confidence
  - produce `ProductEvidence` when ingredient/allergen/certification evidence exists

- `src/grocery_flywheel/sourcing.py`
  - candidate detection, effective price, savings, trip friction, source confidence

- `src/grocery_flywheel/optimization.py`
  - user-selectable objective scoring for `lowest_cost`, `fewer_trips`, `balanced_roi`, `dietary_restrictions`, `allergy_safe`, `best_quality`, and `lowest_decision_fatigue`
  - objective-aware ranking for sourcing and restock/cart plans
  - custom weighted objectives are post-MVP unless a later ADR defines syntax, validation, tie-breaking, labels, and tests

- `src/grocery_flywheel/dietary.py`
  - dietary profile loading, restriction classification, conflict evaluation

- `src/grocery_flywheel/corrections.py`
  - correction chips, explicit preference signals, draft edit telemetry
  - consent-aware local-only default for correction telemetry

- `src/grocery_flywheel/draft.py`
  - internal `cart_plan` and in-person run sheet only
  - no external retailer mutation in MVP

- `src/grocery_flywheel/web/`
  - local web app or generated dashboard shell
  - mobile-responsive command center

### CLI Contract

The MVP CLI should expose these commands before web work expands:

```bash
grocery-flywheel adapters validate examples/retailer_profiles.json
grocery-flywheel adapters inspect examples/retailer_profiles.json --format table
grocery-flywheel adapters create --name "Example Store" --type grocery --channels pickup,delivery --acquisition-methods retailer_history_import,browser_assisted --capabilities purchase_history,product_search,price_lookup,unit_price --output examples/retailer_profiles.local.json
grocery-flywheel import normalized examples/imports/example-history.json --profiles examples/retailer_profiles.json --output dist/state.json
grocery-flywheel import csv examples/imports/example-history.csv --profiles examples/retailer_profiles.json --output dist/state.json
grocery-flywheel analyze dist/state.json --objective balanced_roi --output dist/analysis.json
grocery-flywheel render dist/analysis.json --output dist/sample-dashboard.html
grocery-flywheel run examples/imports/example-history.json --profiles examples/retailer_profiles.json --objective lowest_cost --output dist/sample-dashboard.html
```

Command contract:

- Every command supports `--format json` when useful for the future web UI.
- `adapters create` requires explicit `--acquisition-methods`; MVP does not infer acquisition methods from retailer name or channel.
- Import commands preserve source provenance and confidence.
- `analyze` accepts an optimization objective and writes reusable analysis JSON.
- `render` can render from analysis JSON, not only raw state.
- `run` is the one-command vertical slice for demos and tester fixtures.

### State Files

- `examples/sample_state.json`
- `examples/retailer_profiles.json`
- add `examples/imports/*.json`
- add `examples/imports/*.csv`
- add `examples/expected/*.json`

## Implementation Phases

### Phase 0: Plan And Repo Hygiene

Deliverables:

- Save ralplan artifacts under `.omx/plans/`.
- Keep `docs/DECISION_REGISTER.md` canonical.
- Ensure generated cache and `dist/` policy is intentional.

Acceptance:

- `git status` clean after committing plan.
- Existing tests pass.

### Phase 1: Adapter CLI And Capability Matrix

Deliverables:

- CLI command: `grocery-flywheel adapters inspect examples/retailer_profiles.json`
- CLI command: `grocery-flywheel adapters validate examples/retailer_profiles.json`
- CLI command: `grocery-flywheel adapters create --name ... --type ... --channels ... --acquisition-methods ... --capabilities ... --output ...`
- Human-readable adapter capability output.
- JSON output flag for downstream UI.
- Minimal profile builder that creates a valid adapter profile without hand-editing JSON.

Files:

- `src/grocery_flywheel/cli.py`
- `src/grocery_flywheel/retailer_adapter.py`
- `tests/test_core.py` or new `tests/test_retailer_adapter.py`

Acceptance:

- Valid profiles pass.
- Invalid profiles print actionable errors.
- Stronger history import profiles rank above local-market fallback.
- CLI output includes purchase history, search, price lookup, unit price, availability, substitutions, internal cart plan, order submit status.
- Profile builder creates a valid profile from store name, type, channels, acquisition methods, and capabilities.
- Profile builder never sets `order_submit: true`.

### Phase 1A: Canonical Contracts, Schema Versioning, And Privacy Classes

Deliverables:

- Versioned canonical data contracts.
- `schema_version` in state and imported history.
- Privacy class metadata for purchase history, household inventory, dietary profile, correction telemetry, retailer session, and cart plan fields.
- Product evidence contract for ingredients, allergen statements, certifications, nutrition facts, source, and checked date.
- Consent model for correction telemetry and hosted-mode export/delete mapping.
- Clear naming split:
  - `cart_plan` / `restock_draft`: internal MVP output.
  - `external_cart_draft`: future retailer mutation capability behind ADR.
  - `order_submit`: invalid for MVP.

Files:

- `src/grocery_flywheel/contracts.py`
- `src/grocery_flywheel/privacy.py`
- `docs/DATA_MODEL.md`
- `docs/PRIVACY_SECURITY_BASELINE.md`
- `tests/test_contracts.py`

Acceptance:

- Every canonical object has a schema version.
- Safety-sensitive fields have privacy class metadata.
- Dietary evaluation cannot return `safe` for Tier 1 restrictions without `ProductEvidence` containing source and checked date.
- Correction telemetry cannot persist unless consent/default local-only behavior is explicit.
- `external_cart_draft` is excluded from MVP code paths.

### Phase 2: Import Normalization Engine

Deliverables:

- Canonical order history schema.
- Importer for normalized JSON fixtures.
- Importer for simple CSV/export fixtures.
- Unit-size parser for count, oz, lb, fl oz, ct.
- Confidence field for unknown sizes.

Files:

- `src/grocery_flywheel/importers/normalized.py`
- `src/grocery_flywheel/importers/csv_importer.py`
- `src/grocery_flywheel/normalization.py`
- `examples/imports/`
- `tests/test_importers.py`

Acceptance:

- A fixture with food and non-food items imports into canonical state.
- Unit prices are computed when size is parseable.
- Unknown size keeps raw data and lowers confidence.
- Import provenance is preserved.
- Imported items include privacy class and confidence metadata.
- Imported product evidence is optional, but its absence is explicit.

### Phase 3: Savings And Sourcing Engine

Deliverables:

- Recurring item detection.
- Sourcing trigger logic.
- Effective price model: unit price, coupons, membership, shipping, delivery fee, pickup minimum, trip friction.
- "Worth buying elsewhere" label.

Files:

- `src/grocery_flywheel/sourcing.py`
- `docs/SOURCING_RESEARCH_STAGE.md`
- `tests/test_sourcing.py`

Acceptance:

- Coffee-like recurring shelf-stable item triggers sourcing.
- Dish-soap-like household consumable triggers sourcing when recurring/high-spend.
- Extra-trip friction can suppress a weak savings suggestion.
- Bulk buy is penalized when storage is not available.
- Subscriptions are not recommended unless opt-in.

### Phase 3A: User-Selectable Optimization Objective

Deliverables:

- Optimization objective contract in state and analysis.
- Scoring policies for:
  - `lowest_cost`
  - `fewer_trips`
  - `balanced_roi`
  - `dietary_restrictions`
  - `allergy_safe`
  - `best_quality`
  - `lowest_decision_fatigue`
- UI/render labels explaining the active objective.
- CLI flag: `--objective`.
- Post-MVP placeholder/ADR note for custom weighted objectives; no MVP CLI syntax or hidden behavior.

Files:

- `src/grocery_flywheel/optimization.py`
- `src/grocery_flywheel/core.py`
- `src/grocery_flywheel/render.py`
- `docs/DECISION_REGISTER.md`
- `tests/test_optimization.py`

Acceptance:

- Same candidate set ranks differently for `lowest_cost`, `fewer_trips`, `balanced_roi`, and `allergy_safe`.
- `allergy_safe` and safety-critical dietary restrictions outrank savings.
- `fewer_trips` penalizes split-store recommendations.
- `lowest_cost` still shows friction/quality warnings.
- Active objective appears in analysis JSON and dashboard.

### Phase 4: Dietary Restrictions Engine

Deliverables:

- Dietary profile schema in code.
- Preset restriction catalog.
- Safety-tier evaluation.
- Product conflict result: `safe`, `warn`, `needs_review`, `blocked`.

Files:

- `src/grocery_flywheel/dietary.py`
- `docs/DIETARY_RESTRICTIONS_MODULE.md`
- `tests/test_dietary.py`

Acceptance:

- Allergies and celiac/gluten cross-contact are safety-critical.
- Missing data for safety-critical restriction returns `needs_review`.
- Safety-critical dietary result cannot be `safe` unless current product evidence includes ingredient/allergen/certification source and checked date.
- Vegan/kosher/halal/lifestyle restrictions warn by default unless user config says block.
- Dietary conflicts outrank savings in recommendation ranking.

### Phase 5: Correction Telemetry And Learning

Deliverables:

- Correction event schema.
- Correction chips mapped to durable preference signals.
- Draft edit telemetry model.
- Explicit corrections outrank inferred behavior.
- Consent-aware telemetry storage with local-only default.

Files:

- `src/grocery_flywheel/corrections.py`
- `src/grocery_flywheel/core.py`
- `examples/sample_state.json`
- `tests/test_corrections.py`

Acceptance:

- `never again`, `buy elsewhere`, `wrong format`, `too expensive`, `dietary conflict`, `good default`, and `emergency only` produce distinct signals.
- User cart edits are recorded as telemetry only after consent/local-only storage behavior is explicit.
- Recommendation engine respects explicit correction over repeated purchase inference.

### Phase 5A: Thin Vertical Slice For Product Truth

Deliverables:

- One fixture import that creates canonical state.
- First wow analysis from imported fixture, not hand-authored sample state.
- Mobile dashboard render that shows savings/sourcing above the fold.
- Correction chip smoke path.

Files:

- `examples/imports/`
- `src/grocery_flywheel/importers/`
- `src/grocery_flywheel/render.py`
- `tests/test_vertical_slice.py`

Acceptance:

- Fixture import -> analysis -> dashboard render works in one command.
- First wow appears above fold in generated HTML.
- At least one correction chip appears and maps to a correction event.
- Mobile viewport screenshot/smoke does not show clipped primary actions.

### Phase 6: Local Web Command Center

Deliverables:

- Local web app or generated static app with richer state.
- Guided setup screen: "Which retailers do you use?"
- Adapter capability cards.
- First wow cards: estimated savings and sourcing alternatives.
- Dashboard cards: runway, sourcing, dietary restrictions, correction chips, evidence drawer.
- Mobile-responsive layout.

Files:

- keep Python static renderer if fastest, or introduce a small web stack after explicit execution planning
- `src/grocery_flywheel/render.py`
- optional `web/` or `src/grocery_flywheel/web/`
- `docs/design-preview.html`
- tests/smoke scripts

Acceptance:

- Desktop and mobile screenshots show no overlap or clipping.
- First wow appears above fold.
- Adapter status is human-readable.
- Sourcing cards show provenance/date/confidence/constraints.
- Dietary restrictions section appears when profile exists.
- Correction chips are visible and operable.

### Phase 7: Cart Draft And In-Person Run Sheet

Deliverables:

- Pickup/delivery mode: internal approval-gated `cart_plan` / `restock_draft`.
- In-person mode: store-agnostic run sheet.
- Checkout remains absent.
- External retailer add/remove/set-quantity cart mutation is not part of MVP and requires later ADR as `external_cart_draft`.

Files:

- `src/grocery_flywheel/draft.py`
- `src/grocery_flywheel/render.py`
- `tests/test_draft.py`

Acceptance:

- Internal cart plan can be generated from recommendations.
- In-person run sheet can be generated instead.
- No checkout command exists.
- No external retailer cart mutation module exists in MVP.
- Any future external cart mutation requires explicit approval flag plus ADR.

### Phase 8: Hosted Tester Readiness

Deliverables:

- Explicit decision: hosted beta is not required for local MVP completion, but is the gate for outside testers.
- Hosted-mode architecture note.
- Export/delete flow spec.
- Privacy notice draft.
- Secret handling and session policy.
- Deployment checklist.

Files:

- `docs/PRIVACY_SECURITY_BASELINE.md`
- `docs/adr/0002-hosted-beta-privacy-boundary.md`
- deployment config only after stack choice

Acceptance:

- Local MVP can complete without hosted deployment.
- Hosted beta cannot launch without export/delete story.
- Hosted beta cannot launch without encryption-at-rest plan or hosting provider equivalent.
- Hosted beta cannot launch without retention criteria, session clearing, and secrets/log hygiene checklist.
- No password storage.
- Secrets not in repo.
- User data classes are documented.

## Acceptance Criteria

- `python3 -m pytest -q` passes.
- CLI supports adapter inspect/validate/import/analyze/render flows.
- CLI supports adapter profile creation without hand-editing JSON.
- CLI supports `--objective` for analysis.
- At least one import fixture creates a dashboard with savings and sourcing insights.
- First wow is proven from imported fixture, not only hand-authored sample state.
- Dashboard is mobile-responsive and human-readable.
- Dietary profile conflicts are shown and safety-critical unknowns default to `needs_review`.
- Safety-critical dietary `safe` requires product evidence with source and checked date.
- Internal cart plan is approval-gated; external retailer cart mutation and checkout are absent.
- Privacy/security baseline is traceable to implementation boundaries.
- Hosted beta is explicitly gated and not silently included in local MVP.

## Expanded Test Plan

### Unit

- adapter validation
- import parsing
- canonical contract validation
- privacy class mapping
- unit normalization
- sourcing ranking
- optimization objective ranking
- dietary conflict evaluation
- correction telemetry
- draft generation

### Integration

- retailer profile -> import -> state -> analysis -> dashboard
- dietary profile -> item conflict -> dashboard warning
- safety-critical dietary profile + missing evidence -> `needs_review`, not `safe`
- sourcing candidates -> effective price -> savings card
- same candidates ranked under lowest-cost/fewer-trips/balanced-ROI/allergy-safe objectives
- correction event -> preference update -> recommendation change
- fixture import -> first wow appears above fold

### E2E

- local web setup with sample retailer profiles
- adapter profile creation flow
- mobile viewport command center
- keyboard-only correction flow
- in-person run sheet generation
- pickup/delivery internal cart plan generation without checkout

### Observability

- time to first dashboard
- adapter import health
- sourcing trigger count
- correction accepted/rejected count
- dietary warning count
- no sensitive item details in aggregate logs unless local-only

## Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| Adapter work overfits one retailer | Require every importer to output canonical schema and pass generic fixture tests. |
| Browser imports are fragile | Start with adapter profile and normalized file import; add browser import later as adapter implementation. |
| User loses trust due to bad recommendation | Show evidence, confidence, provenance, correction chips. |
| Dietary safety issue | Safety-critical unknowns default to `needs_review`; do not claim safe without evidence. |
| Cart mutation concern | Internal `cart_plan` only for MVP; no external cart mutation or checkout; later `external_cart_draft` requires ADR and explicit approval. |
| Hosted tester privacy gap | Implement export/delete and data minimization before hosted beta. |
| Optimization feels arbitrary | Make active objective visible and test that rankings change predictably by objective. |

## ADR

### Decision

Implement Grocery Flywheel MVP as a local-first adapter-driven engine with explicit canonical contracts, CLI, and local web dashboard, using retailer history import for first value and estimated savings/sourcing alternatives as the opening wow.

### Drivers

- User wants all retailers supported through reusable abstractions.
- User wants immediate value and beautiful human-readable setup.
- Privacy, dietary restrictions, and cart mutation boundaries are safety-critical.

### Alternatives Considered

- Hardcode Vons/Albertsons first: rejected because it is too myopic.
- Build browser extension first: rejected because it is fragile and retailer-specific before the adapter contract is proven.
- Dashboard-only product: rejected because setup, assistant loop, and cart/restock action are part of the value.
- Hosted SaaS first: rejected for current MVP because privacy/auth/compliance risk would dominate.

### Why Chosen

Adapter-driven local-first engine lets the product work across retailers while keeping tests, safety, and privacy manageable. Adding contracts before feature work prevents drift across import, sourcing, dietary, correction, and dashboard lanes. The thin vertical dashboard slice proves product feel without prematurely committing to hosted infra.

### Consequences

- More schema and importer work upfront.
- Slightly slower start because contracts and privacy classes come before feature modules.
- Browser-assisted live imports come after the adapter contract.
- The product can support local markets, warehouse stores, online retailers, and restaurant suppliers without rewriting the core.

### Follow-ups

- Decide frontend stack before Phase 6.
- Decide hosted beta stack before Phase 8.
- Create ADR for hosted beta privacy boundary.
- Create ADR for browser-assisted retailer import if implemented.
- Create ADR for external retailer cart mutation before implementing `external_cart_draft`.
- Create ADR for hosted deployment stack before outside tester launch.

## Available Agent Types Roster

- `explore`: fast repo lookup and file mapping.
- `planner`: sequencing and risk flags.
- `architect`: system boundaries and tradeoffs.
- `critic`: plan/design challenge and review.
- `executor`: implementation and refactoring.
- `test-engineer`: test strategy and coverage.
- `designer`: UX/UI architecture.
- `researcher`: official docs and external references.
- `dependency-expert`: framework/package selection.
- `verifier`: completion evidence and claim validation.
- `code-reviewer`: final review.
- `git-master`: commit/history hygiene.

## Follow-up Staffing Guidance

### Ralph Path

Use `$ralph` if one persistent owner should drive the whole plan sequentially.

Suggested lane:

- `executor`, medium reasoning: implement adapter CLI/import/sourcing/dietary modules.
- `test-engineer`, medium reasoning: expand fixture tests.
- `designer`, high reasoning when Phase 6 starts: command center UX.
- `verifier`, high reasoning: final evidence pass.

### Team Path

Use `$team` when parallel delivery matters.

Suggested workers:

1. Adapter/import lane, `executor`, medium reasoning.
2. Sourcing/savings lane, `executor`, medium reasoning.
3. Dietary/corrections lane, `executor`, medium reasoning.
4. Web/design lane, `designer` + `executor`, high/medium reasoning.
5. Test/verification lane, `test-engineer`, medium reasoning.
6. Privacy/docs lane, `writer` or `architect`, medium/high reasoning.

### Launch Hints

```bash
$team "Implement Grocery Flywheel MVP from .omx/plans/implementation-plan-grocery-flywheel-mvp-20260526T052923Z.md. Use disjoint lanes: adapter/import, sourcing, dietary/corrections, web dashboard, tests, privacy/docs."
```

```bash
$ralph "Execute .omx/plans/implementation-plan-grocery-flywheel-mvp-20260526T052923Z.md sequentially. Do not implement checkout. Preserve approval-first boundaries."
```

## Team Verification Path

Team must prove:

- all lane tests pass
- CLI flows work end-to-end
- dashboard renders from imported fixture
- no checkout path exists
- dietary safety tests pass
- mobile screenshot smoke passes
- privacy docs match implementation boundaries

Ralph follow-up verifies integration and fixes cross-lane issues only after Team returns evidence.

## Goal-Mode Follow-up Suggestions

- `$ultragoal`: recommended default for durable MVP delivery because this is a multi-phase implementation goal.
- `$autoresearch-goal`: use only for a dedicated retailer import legality/best-practice research track.
- `$performance-goal`: not the right fit until import/render performance becomes measurable.

Recommended execution posture: Team + Ultragoal for parallel implementation with durable leader-owned checkpointing. Use Ralph afterward for sequential final verification and fix pressure.

## Planner Notes

This plan intentionally does not choose a frontend stack. The next execution pass should first implement contracts plus the imported-fixture vertical slice, then either preserve static HTML briefly or select a small local web stack after dependency review. The immediate blocker is proving the adapter/import/sourcing engine and first-wow dashboard from imported fixtures.

## Architect Review Changelog

Applied after Architect `ITERATE` verdict:

- Added Phase 1A for canonical contracts, schema versioning, privacy classes, product evidence, and consent model.
- Split internal `cart_plan` / `restock_draft` from future `external_cart_draft`.
- Added dietary safety rule requiring evidence before Tier 1 `safe`.
- Moved telemetry consent/local-only default before correction persistence.
- Added Phase 5A thin vertical slice to test product comprehension before broad web work.
- Added integration tests for missing dietary evidence and first-wow imported fixture dashboard.

## Critic Review Changelog

Applied after Critic `ITERATE` verdict:

- Added user-selectable optimization objective module, CLI flag, dashboard label, and objective-ranking tests.
- Added concrete CLI command contracts for adapters validate/inspect/create, import, analyze, render, and one-command run.
- Added adapter profile builder slice so users/agents can create retailer profiles without hand-editing JSON.
- Clarified hosted beta as outside local MVP completion but required for outside tester launch, with encryption/export/delete/retention/session/secrets gates.

Applied after Critic pass 2 `ITERATE` verdict:

- Made `--acquisition-methods` explicit in the `adapters create` command contract and rejected inference for MVP.
- Moved custom weighted objectives out of MVP unless a later ADR defines syntax, validation, tie-breaking, dashboard labels, and tests.

## Consensus Approval

- Architect pass 3: `APPROVE`. Contracts-first sequencing, explicit acquisition methods, named MVP objectives, internal cart plan boundary, and hosted beta gate are ready for execution.
- Critic pass 3: `APPROVE`. Prior blockers are closed; no remaining approval-blocking execution, product, or test gaps were identified.
