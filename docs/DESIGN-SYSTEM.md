# Grocery Flywheel dashboard design system

Direction: **warm pantry ledger** (Design t_0abdce8f, confirmed by Liam). Paper,
ink, one copper action, hairline rules, system serif display. No fetched font,
image, icon, script or stylesheet: the document is self-contained and works
offline.

## Reading order is the contract

1. **Masthead** — surface, order, order total, as-of date, observed days, and a
   persistent dietary status line that cannot be scrolled past. The status line
   states the count only; the verdict is not repeated three times in one view.
2. **Needs attention today** — the dietary verdict, the qualifier, the state
   legend and every evaluation.
3. **Today · one thing** — the cart review, as an action list with dietary state.
4. **What will run out** — basis note, runway ruler, caption, at-risk table,
   arithmetic.
5. **The ledger** — every item with price, dietary and product evidence.
6. **Evidence** — every original panel in a native `<details>` disclosure, in
   registry order. Collapsed by default; nothing is removed.

`render_dashboard` owns this order. `PANELS` stays the single registry; it is not
the reading order. Each disclosure body is a responsive `.disclosure-grid`; the
legacy `span-*` classes are not inert inside it.

## Type scale and hierarchy

| token | use |
|---|---|
| `--step-4` | dietary attention figure — the largest number on the page |
| `--step-3` | page title |
| `--step-2` | the one action headline, section headlines and runway arithmetic |
| `--step-1` | lede, action item names, disclosure summaries |
| `--step-0` | body |
| `--step--1` | labels, captions, table headers, disclosure `h2`s |

The attention figure (`--step-4`) must outrank every other number. The page title
and the action headline are deliberately one step apart. Headlines and the lede
use `text-wrap:balance` so a narrow viewport does not leave orphan words.

## Attention contract (fail closed)

The engine returns `dietary_status` per item and `evidence_status` per
evaluation. The dashboard derives its own per-item result map from
`dietary_evaluations`; it never trusts an item's `dietary_status` on its own.

- `{open}/{total} items unverified`, where *open* counts every item that is not
  cleared: `blocked`, `needs_review`, `warn`, unknown, or **no evaluation at
  all**. When any item is blocked the figure caption reads "items blocked or
  unverified".
- **"No item has been cleared as safe"** whenever any item is open — a warning
  is never presented as a clearance.
- **`Cleared` requires an explicit `safe` result with `evidence_status` =
  `current`.** A missing status, an unknown status, or `safe` without current
  evidence renders the neutral **"Not evaluated"** mark, never the sage success
  token. The same rule applies in the ledger, action list and substitutions.
- the evidence gap: how many items have no `current` evidence;
- the engine rule that would clear an item, and — when every evaluation is
  `warn` — that this profile warns on every item and clears none;
- profile label and restriction (`value`, `safety_tier`, `behaviour`) in a
  caveat whose first sentence is weighted: **"Missing evidence is a data gap,
  not proof of a safety failure."**
- a state legend defining Blocked, Needs review, Warning, Cleared and Not
  evaluated in one place;
- a `<details class="evidence">` table of **every** evaluation with item, result,
  evidence and the engine's own reason. Raw result/evidence keys stay in
  `data-raw-*` attributes for machines; visible text uses the label maps.

Status colours: `blocked` and `needs_review` use `--brick`; `warn` uses
`--ochre`; `safe` uses `--sage`; unknown/missing uses `--muted`. **`warn` must
never use the success token.**

## Vocabulary: dietary and price

One vocabulary per concept across every panel:

| dietary result | label | token |
|---|---|---|
| `blocked` | Blocked | brick |
| `needs_review` | Needs review | brick |
| `warn` | Warning | ochre |
| `safe` + current evidence | Cleared | sage |
| absent/unknown/safe without current evidence | Not evaluated | muted |

| price state (resolved by `freshness.item_freshness`) | label | token |
|---|---|---|
| priced, fresh | Priced | sage |
| priced, stale | Stale price on file | ochre |
| `unpriced` | No price captured | muted |
| `estimated` | Estimated price | ochre |
| `gift` | Gift — price optional | muted |

The ledger, freshness panel and action list all read the freshness record, so a
missing `items[*].pricing_status` no longer renders as "No price record" while
the freshness panel calls the same item priced. `normal store` (engine draft
source) displays as "your usual store".

## Action contract (one thing)

The cart review is an ordered list, one row per item: number, item, the engine's
own `reason`, the humanized `action`, `source`, and a **Dietary** line with the
item's mark and evidence label. No raw `action` or `approval_state` slug appears
in visible prose. Approval is stated once in words ("every item needs your
approval"), together with `approval_required=true`, `checkout_available=false`,
the price-freshness caveat and the honest export note.

The downloaded draft is the real engine plan plus a `presentation` envelope:
`schema`, `note`, and `dietary_context` (per-item result, `cleared`, evidence
status, reason, restriction tiers). Every engine field of the plan is retained
verbatim at the top level. The page says the JSON includes the dietary state and
that nothing is bought or written back.

## Runway contract

- A **basis note beside the figure** states the full order total, the
  unattributed remainder, the observed-day window, and that the estimate is
  dollar-weighted and not a pantry audit.
- SVG ruler: one tick per day, ink for elapsed days, `--edge-strong` outline for
  remaining days, copper marker for today, `role="img"` with a sentence
  `aria-label`.
- Legend, then a caption with elapsed days, remaining days, and consumed versus
  order value.
- At-risk table: items at or past half life, with role, percent, a copper
  drawdown bar (`--brick` at 80%+), spend and note. Captions are a
  `.table-caption` paragraph above the table, never a `<caption>` squeezed by
  the table grid.
- Arithmetic strip: observed depletion, estimated runway, order total.
- Depletion never uses the success token; drawdown is copper/brick.

## Ledger contract

Five content-driven columns: **Item** (with role · category sub-line), **Spend**
(with consumed %), **Price**, **Dietary**, **Product evidence**. Roles and
categories are humanized; the raw key stays in `data-role`. Product evidence is
labelled, opens a disclosure per evidence row, and reads "No label evidence"
when absent. When every item shares one dietary result the caption says so once
instead of repeating the same token thirteen times.

Below the table, the reconciliation states the order total, the tracked total,
and the **unattributed remainder** in words.

## Layout and contrast

- Tables use content-driven columns (`table-layout:auto`), `overflow-wrap:
  break-word`, `word-break:normal`, `hyphens:none`. Captions live outside the
  table. Below 700px each row stacks into labelled blocks; a ledger row is five
  labelled pairs at 390px and every datum stays reachable. 753–885px keeps the
  real table (rows 72–92px).
- Meaningful graphics meet **≥3:1** against paper: ruler outlines, legend
  outlines and bar boundaries use `--edge-strong` (#8A7F6E → 3.49:1 on `--bg`,
  3.87:1 on `--panel`). Hairline rules stay decorative.
- The `.muted` class is defined; `.wow` and other dead tokens are gone.
- A skip link targets the review section (not a `<main>` that still contains the
  masthead). A print stylesheet removes the paper background; collapsed
  sections are documented as printing their titles only.

## Data and safety contracts

Unchanged from the engine: calculations, fail-closed dietary evidence,
`approval_required=true`, `checkout_available=false`, profile containment and
private output, no telemetry, no network, no listener, no retailer integration.
Correction capture renders only for `local_only`/`hosted_opt_in` consent. All
emitted scripts are fixed renderer literals; household data never reaches a
script, and the native wrapper hashes every script and handler into the CSP.
The native CSP is a **union policy** across all surfaces: a given artifact may
carry hashes for scripts or handlers that surface does not render. The hashes
are content-specific, so this is harmless; it is not a claim that every hash is
used by every artifact.

## Verification contract

- `pytest` (presentation, escaping, consent, CSP, manifest coverage, fail-closed
  dietary display, mixed/blocked fixtures), `ruff`, docs link check.
- Fresh bundle build, then the native verifier: manifest coverage, no caches,
  plugin validate/doctor, dispatch through the installed manager, empty/long/
  mixed fixtures, malformed state → `INVALID_INPUT`.
- Chrome at 1440/885/820/768/390/320 and native 400% zoom: zero external
  requests, zero JS errors, no overflow, labelled cells, visible focus, measured
  text contrast, **measured non-text contrast ≥3:1** for ruler/legend/bar,
  word-intact cells, five-column ledger, styled disclosure headings, real
  downloads.
- `capture` mode in the browser verifier is evidence only and reports
  `acceptance:false`; `baseline` is rejected. Only `normal` and `zoom` count.
- Golden dashboards are regenerated intentionally; a golden diff is a design
  change, never a test fix.
