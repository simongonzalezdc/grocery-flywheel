# Grocery Flywheel dashboard design system

Direction: **warm pantry ledger** (Design t_0abdce8f, confirmed by Liam). Paper,
ink, one copper action, hairline rules, system serif display. No fetched font,
image, icon, script or stylesheet: the document is self-contained and works
offline.

## Reading order is the contract

1. **Masthead** — surface, order, order total, as-of date, observed days, and a
   persistent dietary status line that cannot be scrolled past.
2. **Needs attention today** — the dietary verdict.
3. **Today · one thing** — the cart review, as an action list.
4. **What will run out** — runway ruler, caption, at-risk table, arithmetic.
5. **The ledger** — every item with price, dietary and product evidence.
6. **Evidence** — every original panel in a native `<details>` disclosure, in
   registry order. Collapsed by default; nothing is removed.

`render_dashboard` owns this order. `PANELS` stays the single registry; it is not
the reading order.

## Type scale and hierarchy

| token | use |
|---|---|
| `--step-4` | dietary attention figure — the largest number on the page |
| `--step-3` | page title and the one action headline |
| `--step-2` | section headlines and runway arithmetic |
| `--step-1` | lede, action item names |
| `--step-0` | body |
| `--step--1` | labels, captions, table headers |

The attention figure (`--step-4`) must outrank every other number. Order total
is not the hero: it sits inside the runway arithmetic at `--step-2`.

## Attention contract (fail closed)

The engine returns `dietary_status` per item and `evidence_status` per
evaluation. The dashboard must render:

- `{open}/{total} items unverified`, where *open* counts items whose status is
  `blocked`, `needs_review` or `warn`;
- **"No item has been cleared as safe"** whenever any item is open — a warning
  is never presented as a clearance;
- the evidence gap: how many items have no `current` evidence;
- the engine rule that would clear an item, and — when every evaluation is
  `warn` — that this profile warns on every item and clears none;
- profile label and restriction (`value`, `safety_tier`, `behaviour`) in a caveat
  that says missing evidence is a data gap, not proof of safety;
- a `<details class="evidence">` table of **every** evaluation with item, result,
  evidence and the engine's own reason. Raw result/evidence keys stay in
  `data-raw-*` attributes for machines; visible text uses the label maps.

Status colours: `blocked` and `needs_review` use `--brick`; `warn` uses
`--ochre`; `safe` uses `--sage`. **`warn` must never use the success token.**

## Action contract (one thing)

The cart review is an ordered list, one row per item: number, item, the engine's
own `reason`, the humanized `action`, and `source`. No raw `action` or
`approval_state` slug appears in visible prose. Approval is stated once in words
("every item needs your approval"), together with `approval_required=true`,
`checkout_available=false`, the price-freshness caveat and the honest export
note: the button downloads browser-local JSON; it does not save.

## Runway contract

- SVG ruler: one tick per day, ink for elapsed days, outline for remaining,
  copper marker for today, `role="img"` with a sentence `aria-label`.
- Legend, then a caption with elapsed days, remaining days, and consumed versus
  order value.
- At-risk table: items at or past half life, with role, percent, a copper
  drawdown bar (`--brick` at 80%+), spend and note.
- Arithmetic strip: observed depletion, estimated runway, order total.
- Depletion never uses the success token; drawdown is copper/brick.

## Ledger contract

Columns: Item, Role, Category, Spend, Consumed, Price, Dietary, Product evidence.
Roles and categories are humanized; the raw key stays in `data-role`.
`Product evidence` is labelled, opens a disclosure per evidence row, and reads
"No label evidence" when absent. Below the table, the reconciliation states the
order total, the tracked total, and the **unattributed remainder** in words.

## Data and safety contracts

Unchanged from the engine: calculations, fail-closed dietary evidence,
`approval_required=true`, `checkout_available=false`, profile containment and
private output, no telemetry, no network, no listener, no retailer integration.
Correction capture renders only for `local_only`/`hosted_opt_in` consent. All
emitted scripts are fixed renderer literals; household data never reaches a
script, and the native wrapper hashes every script and handler into the CSP.

## Verification contract

- `pytest` (presentation, escaping, consent, CSP, manifest coverage), `ruff`,
  docs link check.
- Fresh bundle build, then the native verifier: manifest coverage, no caches,
  plugin validate/doctor, dispatch through the installed manager, malformed
  state → `INVALID_INPUT`.
- Chrome at 1440/768/390/320 and native 400% zoom: zero external requests, zero
  JS errors, no overflow, labelled cells, visible focus, measured contrast,
  real downloads.
- `capture` mode in the browser verifier is evidence only and reports
  `acceptance:false`; `baseline` is rejected. Only `normal` and `zoom` count.
- Golden dashboards are regenerated intentionally; a golden diff is a design
  change, never a test fix.
