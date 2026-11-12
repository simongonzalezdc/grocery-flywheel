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

**One verdict authority.** `_item_verdict(name, evaluation)` computes every
field a dietary surface may render: `state`, `token`, `label`, `detail`,
`cleared`, `result`, `evidence`, `tier` and `reason`. `_dietary_mark(verdict)`
accepts nothing else — it cannot see an item's `dietary_status`, a price field
or a missing value, so no surface can infer a clearance of its own choosing.
The ledger, action list, substitutions, sourcing rows, easy-food rotation,
evidence drawer, headline counts and the downloadable draft all render that
same object. The invariant, asserted over every fixture and every viewport, is
`mark_token == cleared` iff `evaluation.result == safe` AND
`evidence_status == current`; one item must show one verdict everywhere it
appears. An evaluation whose item name matches no item on the page is never
silently dropped: it is surfaced as **not evaluated — evidence did not match**
and never clears a row.

- `{open}/{total}` with the caption **"items blocked or not cleared"** when any
  item is blocked, otherwise "items unverified". *open* counts every item that is
  not cleared: `blocked`, `needs_review`, `warn`, unknown, or **no evaluation at
  all**.
- An **exact counts line** directly under the headline: `X of N cleared · Y
  blocked · Z need review · W warnings · V not evaluated`, omitting zero rows.
  Mixed pages never make an absolute claim: the headline is
  `X of N items are cleared; Y items are not cleared` (or the blocked sentence
  when something is blocked), and **"No item has been cleared as safe"** appears
  only when nothing is cleared.
- **`Cleared` requires an explicit `safe` evaluation result with
  `evidence_status` = `current`.** The item's own `dietary_status` is never a
  clearance: `core` defaults a missing item field to `safe`, so a mark derived
  from it fails open. A contradictory pair (item says `safe`, evaluation says
  `blocked`/`needs_review`/`warn`) renders the evaluation's mark. The same rule
  applies in the ledger, action list, substitutions and sourcing row.
- the evidence gap: how many items have no `current` evidence;
- the engine rule that would clear an item, and — when every evaluation is
  `warn` — that this profile warns on every item and clears none;
- profile label and restriction (`value`, `safety_tier`, `behaviour`) in a
  `.attention-context` disclosure, so the mobile first screen is the verdict and
  the action, not two explanatory paragraphs; the qualifier stays visible at
  body size directly under the verdict headline and is selected from the
  configured behaviour: under **warn**, "Missing evidence is a data gap, not
  proof of a safety failure."; under **block** (or a critical/allergy tier),
  "Missing evidence is treated as not cleared: the engine never clears an item
  it cannot verify." The engine-rule paragraph and the restriction note are
  selected the same way — a blocking profile never reuses the warn wording.
- the action area carries **every blocked item**, including one the engine's
  cart plan does not name: it renders a held row, `Do not buy — blocked:
  <engine reason>`. No non-cleared row may present an unqualified action; each
  next to it carries its dietary qualifier (for example "Restock — not
  dietarily cleared: resolve evidence first").
- a **text severity token** in the section note (`Dietary evidence · warning
  tier` / `· blocked`), so state does not rest on hue alone;
- a **jump link** to `#today` on every page with cart items, so the action is
  reachable within an 844 px mobile first screen even when the attention panel
  is tall;
- the five-state legend sits inside the evidence disclosure with the full
  evaluation table, so reference material does not push the action below the
  fold;
- a `<details class="evidence">` table of **every** evaluation with item, result,
  evidence and the engine's own reason. Raw result/evidence keys stay in
  `data-raw-*` attributes for machines; visible text uses the label maps. The
  evidence drawer shows **every** entry in a label list — it does not truncate.

Status colours: `blocked` and `needs_review` use `--brick`; `warn` uses
`--ochre`; `safe` uses `--sage`; unknown/missing uses `--muted`. **`warn` must
never use the success token.** A preference-tier warning is not a blocker: the
whole attention panel wears `.attention.warn-tier` (ochre edge and figure) and
the qualifier is body-size, not the smallest tier. Brick is reserved for
blocking evidence (`blocked`/`needs_review`).

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
| priced, fresh | Priced | ink (`plain`) |
| priced, stale with a check date | Stale price on file | ochre |
| priced, stale with no check date | Price on file · date unknown | ochre |
| `unpriced` | No price captured | muted |
| `estimated` | Estimated price | ochre |
| `gift` | Gift — price optional | muted |

An unpriced placeholder with no recorded amount renders its spend cell as
**not recorded**, never `$0.00`; a recorded zero (priced, estimated or gift)
still renders `$0.00`. The sourcing card states the real number of modelled
saving rows in the engine's research (never an absolute "one candidate"), and
recent pulses are labelled **unverified note** with a caption saying they are
not reconciled against the ledger or the depletion model.

Sage is reserved for a dietary clearance. A price state never wears the sage
token, so green cannot mean both "Cleared" and "Priced". Aggregates use four
buckets from the freshness record — `priced · stale · no price · estimated` —
so an item whose own cell says "Estimated price" is never counted as stale.

The ledger, freshness panel and action list all read the freshness record, so a
missing `items[*].pricing_status` no longer renders as "No price record" while
the freshness panel calls the same item priced. `normal store` (engine draft
source) displays as "your usual store".

## Action contract (one thing)

The cart review is an ordered list, one row per item: number, item, the engine's
own `reason`, the humanized `action`, `source`, and a **Dietary** line with the
evaluation-derived mark and evidence label. Action and source carry visible
`Action` / `Source` labels, and no raw `action` or `approval_state` slug appears
in visible prose. Approval is stated once in words ("every item needs your
approval before anything is bought."), together with `approval_required=true`,
`checkout_available=false`, the four-bucket price caveat (`priced · stale · no
price · estimated`) and the honest export note. On mobile the source line moves
under the item instead of squeezing the reason into a narrow column.

The sourcing panel labels its mark **"Dietary · this item, not the
alternatives"** and its basis note says alternatives are not evaluated there.
A missing amount renders **"not recorded"**; `_money` never fabricates `$0.00`.

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

The headline attributes the money instead of repeating the order total:
**`{n} items · {tracked} tracked · {unattributed} unattributed · {order} order`**.
The reconciliation below repeats the arithmetic in words.

## Layout and contrast

- Every table declares `table-layout:fixed` and an explicit `<colgroup>`; widths
  are percentages that sum to 100. A 2,000-character unbroken token therefore
  wraps inside its column instead of growing the table's min-content width. Long
  notes open a `<details class="note-disclosure">`; captions live outside the
  table.
- Below 700px each row stacks into labelled blocks. A ledger record is a
  two-column grid; every value cell carries a `.cell-value` wrapper and every
  sub-line (`.cell-sub`, `.mark-detail`) is pinned to column 2, so the note sits
  under the value and never under the label.
- Meaningful graphics meet **≥3:1** against paper: ruler outlines, legend
  outlines and bar boundaries use `--edge-strong` (#8A7F6E → 3.49:1 on `--bg`,
  3.87:1 on `--panel`). Hairline rules stay decorative.
- The `.muted` class is defined; `.wow` and other dead tokens are gone.
- Disclosure titles are the panel's own `<h2>` promoted to the `<summary>`; the
  body keeps a `.visually-hidden` copy of the heading for heading navigation, so
  one title is visible and no second heading is drawn.
- A jump link (`#today`) is present whenever cart items exist; at 390 px the
  first action or its jump link must sit within an 844 px first screen.
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
- Chrome at 1440/885/820/768/753/390/320 and native 400% zoom on **normal,
  consent, empty, long, mixed and hostile fixtures**: zero external requests,
  zero JS errors, no page or table overflow, labelled cells, visible focus,
  measured text contrast, **measured non-text contrast ≥3:1** for
  ruler/legend/bar, word-intact cells, a five-column ledger *when a ledger table
  exists*, the empty ledger's own copy when it does not, the one action
  starting above the 900px fold at desktop width, a visible `#today` jump link
  on mobile, **one dietary verdict per item across every surface**, a
  `.mark.ok` only where the authority says `cleared` with `safe`+`current`,
  **every blocked item present in the action area** (including a cart-absent
  hold), **no non-cleared action without its qualifier**, and no `$0.00` on a
  row whose price state is `No price captured`. Zoom mode runs on **all six**
  fixtures, not only the sample.
- Long content is a standard fixture: a 2,000-character item name and a
  2,500-character note must not widen any table past its panel; a long note is
  disclosed, and the page gains no horizontal overflow.
- `capture` mode in the browser verifier is evidence only and reports
  `acceptance:false`. It writes **full-page** captures at 1440 and 390 plus
  section captures (attention, today/action, runway, ledger, and the long
  fixture's long row), and a `capture-manifest.json` binding the artifact's
  sha256 and every PNG's sha256, so a capture cannot be separated from the bytes
  it depicts. `baseline` is rejected. Only `normal` and `zoom` count as checks.
- Golden dashboards are regenerated intentionally; a golden diff is a design
  change, never a test fix.
