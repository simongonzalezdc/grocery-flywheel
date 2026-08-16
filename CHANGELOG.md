# Changelog

All notable changes to Grocery Flywheel are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/); versions match
the single-sourced `__version__`.

## [Unreleased] — 2026-08-16

### Security (from the adversarial QA pass: three-way independent review + dynamic e2e)

- **Fixed stored XSS** in the dashboard's correction-capture panel: item
  names containing `</script>` broke out of the inline JSON payload.
  JSON embedded in `<script>` is now escaped (`<`, `>`, `&`, U+2028/9)
  and cannot terminate the script context; payload round-trips exactly.
- **Dietary engine fails closed on stale or unrecognized evidence**:
  product evidence older than 365 days no longer counts as "current"
  (items return to `needs_review` with a `stale` status), and critical
  restrictions with empty/unrecognized values never evaluate `safe`.
- Dietary-**blocked** substitution candidates can no longer rank first
  under any objective weighting (previously possible under `fewer_trips`).
- Contract validation rejects `NaN`/infinities, negative
  spend/quantity/unit_price, out-of-range fractions, and present-but-null
  `added_on`.
- MCP server: JSON-RPC shape validation (−32600 for non-object or
  oversized requests, 16 MB line cap before parsing, `RecursionError`
  caught); explicit `id: null` requests are answered; `arguments` must be
  an object (−32602). The `plan_next_cart` approval boundary is enforced
  with `RuntimeError` instead of `assert` (survives `python -O`).

### Fixed

- `first_wow` savings headline sums all sourcing rows (was first-row only).
- `run_sheet` carries the state's `schema_version` (was always `None`).
- CLI refuses `--output` paths that resolve to the input state file.
- Importer treats empty-string numerics as absent (no more confusing
  `float("")` crashes) and preserves depletion/storage/recurring fields
  through normalization.
- Correction-capture download emits date-only `created_at` (round-trips
  through the contract).

### Hardening

- All state and artifact writes are atomic (temp file + `os.replace`) —
  a crash mid-write can no longer truncate a state or dashboard.
- `capture-visit` validates ISO timestamps, rejects fractional minutes,
  and writes through the shared atomic IO path.
- Trip summaries survive hand-edited garbage `duration_min` values.
- CSV import fails closed on multi-order exports (lists the orders found)
  instead of silently collapsing them; `csv.Error` becomes a clean error.
- Contract now validates `visits`, `retailer_profiles`, and `hourly_value`.
- Future-dated orders (order date after `as_of`) surface a visible data
  warning instead of silently clamping to one day.

## [0.2.0] — 2026-08-14

The major redesign release: the 2026-05 WIP branch harvested as a library
layer onto a restructured, contract-first core.

### Added

- **Canonical state contract** (`2026-08-14.mvp2`): versioned, fail-closed
  validation at write/import; lenient reads forever (all schema vintages
  coexist by design — unversioned, `2026-05-26.mvp1`, current).
- **Importers**: `grocery-flywheel import normalized|csv` — retailer
  history exports become canonical states with privacy classes, consent,
  provenance, and evidence.
- **Privacy layer**: privacy classes per field, local-first consent
  defaults, correction-telemetry gating, hosted-beta gate (ADR 0002).
- **Dietary engine**: evidence-gated restriction evaluation with
  fail-closed safety semantics; `evaluate_dietary` MCP tool.
- **Corrections**: seven durable signals recorded via
  `grocery-flywheel corrections add` (consent-gated) that override
  price-only preferences.
- **Objectives**: seven named optimization objectives for substitution
  and sourcing ranking (`--objective lowest_cost|fewer_trips|allergy_safe|…`).
- **Sourcing research generation** from a built-in alternatives library,
  gated on dietary status and the active objective.
- **Dark command-center dashboard** (decision D1): panel registry
  (ordered `(name, span, render)` callables), first-look cards, dietary
  chips, evidence drawers, consent-gated correction capture, internal
  cart plan — with main's freshness/easy-food/trip panels rebuilt inside.
- **Structural approval boundary**: cart plans always require human
  approval; `checkout_available` is asserted `false` end to end.
- **MCP server** grown to five tools (analyze, render, sourcing,
  evaluate_dietary, plan_next_cart); JSON-RPC 2.0 notification semantics
  pinned by tests.
- `hourly_value` wired into real amortized trip costs.

### Changed

- One home per fact: `model/` owns the state contract and depletion/date
  math (previously duplicated with divergent semantics); `rendering/`
  owns all HTML; `state_io` owns file IO; version single-sourced.
- Docs collapsed ~20 → 11 surfaces with a named merge target for every
  retired doc; README rewritten with one positioning and an honest
  "what it actually does today" section; private workflow residue
  scrubbed; 30-second quick start verified e2e in CI.

### CI & trust

- Canonical (Forgejo) pipeline actually blocks — no `|| true` guards;
  lint rule set pinned explicitly; gitleaks secret scanning in both
  pipelines (verified red on a planted realistic token); docs link
  check; golden dashboards gate every PR.
