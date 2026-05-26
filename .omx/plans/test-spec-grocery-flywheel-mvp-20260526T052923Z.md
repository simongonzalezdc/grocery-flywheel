# Test Spec: Grocery Flywheel MVP

Created: 2026-05-26T05:29:23Z
Status: Consensus approved by Architect and Critic

## Test Strategy

Testing must prove that Grocery Flywheel can ingest purchase history, normalize it, find savings/sourcing opportunities, respect safety boundaries, and render a usable dashboard without relying on live checkout or hardcoded retailer logic.

## Unit Tests

### Canonical Contracts

- Every canonical object includes `schema_version`.
- Purchase history, household inventory, dietary profile, correction telemetry, retailer session, and cart plan fields carry privacy class metadata.
- Product evidence requires evidence type, source, and checked date when used for safety-critical decisions.
- Internal `cart_plan` is distinct from future `external_cart_draft`.

### Retailer Adapter

- Valid adapter profiles pass validation.
- Missing required fields produce clear errors.
- `order_submit: true` fails MVP validation.
- `retailer_history_import` requires purchase history capability.
- Capability matrix ranks stronger import profiles above fallback-only profiles.
- Profile builder creates a valid profile from store name, type, channels, acquisition methods, and capabilities.
- Profile builder does not require hand-editing JSON.
- Profile builder requires explicit acquisition methods and does not infer them from store name or channel.

### CLI Contracts

- `adapters validate` returns success for valid profiles and nonzero/actionable errors for invalid profiles.
- `adapters inspect` returns table and JSON formats.
- `adapters create` writes a valid adapter profile when passed explicit `--acquisition-methods`.
- `adapters create` fails with an actionable error when acquisition methods are omitted.
- `import normalized` and `import csv` produce canonical state JSON.
- `analyze` reads canonical state and writes analysis JSON.
- `render` reads analysis JSON and writes dashboard HTML.
- `run` executes import -> analyze -> render in one command.
- `analyze --objective` changes recommendation ranking.

### Import Normalization

- Raw normalized order fixtures become canonical order items.
- Unit sizes parse into comparable unit prices.
- Unknown sizes preserve raw value and lower confidence.
- Food and non-food categories map into shared item roles.
- Duplicate recurring products cluster correctly.

### Savings And Sourcing

- Unit price comparisons include package size.
- Effective price includes coupons, shipping, membership, delivery fees, and trip friction when supplied.
- Recurring, high-spend, shelf-stable items trigger sourcing research.
- Subscription suggestions are opt-in only.
- Bulk buys are penalized when storage constraints are not met.

### Optimization Objective

- `lowest_cost` ranks by effective price first while preserving warnings.
- `fewer_trips` penalizes split-store recommendations.
- `balanced_roi` combines savings, friction, quality, and confidence.
- `allergy_safe` prioritizes safety-critical dietary outcomes above savings.
- Active objective is serialized in analysis output.
- Custom weighted objectives are excluded from MVP and require a later ADR plus tests before implementation.

### Dietary Restrictions

- Dietary profiles load from state.
- Safety-critical restrictions default to `needs_review` on missing data.
- Safety-critical restrictions can return `safe` only when product evidence includes source and checked date.
- Lifestyle/preference restrictions warn rather than block by default.
- Allergy conflicts outrank price savings.

### Correction Telemetry

- User edit events persist as preference/correction signals.
- Correction telemetry requires explicit consent or local-only default behavior.
- Explicit corrections outrank inferred behavior.
- Cart edits after draft creation are captured as learning telemetry.

## Integration Tests

- Import fixture -> canonical state -> analysis -> dashboard HTML.
- Imported fixture -> first wow savings/sourcing appears above fold.
- Retailer profiles + imported orders -> adapter status + sourcing results.
- Adapter setup/profile-builder flow -> valid profile -> inspectable capability matrix.
- Dietary profile + cart item conflict -> warning in dashboard.
- Safety-critical dietary profile + missing evidence -> `needs_review`, not `safe`.
- In-person mode produces restock run sheet without cart mutation.
- Pickup/delivery mode produces internal cart plan without checkout or external cart mutation.
- Same candidates under different objectives produce different top recommendations.

## E2E / Browser Smoke

- Mobile viewport renders without clipped primary actions.
- Desktop viewport shows first wow cards above the fold.
- Keyboard navigation reaches all main actions.
- Correction chips are visible and operable.
- Evidence drawers can open and close.
- Sourcing cards show provenance, date, confidence, and constraints.

## Security / Privacy Verification

- No retailer password storage.
- No secrets in repo or logs.
- Hosted-mode design includes export/delete.
- Hosted beta gate checks encryption plan, retention criteria, session clearing, secrets/log hygiene, and export/delete before outside tester launch.
- Correction telemetry consent and retention behavior are testable.
- Adapter provenance is visible.
- Checkout is absent or hard-blocked behind explicit approval.

## Observability

- Record import success/failure events.
- Record source confidence and adapter health.
- Record time to first dashboard.
- Record recommendation accepted/rejected counts.
- Record user corrections without leaking sensitive item details in aggregate logs.

## Manual QA Checklist

- Try a tester with 3+ months of sample order history.
- Try a tester with only one order and verify low confidence.
- Try no retailer history and verify fallback path is honest.
- Try dietary restriction profile and verify warnings.
- Try high-spend coffee/cleaning item and verify sourcing research appears.
