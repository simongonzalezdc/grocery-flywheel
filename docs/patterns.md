# Flywheel Patterns and Expansion Markets

The reusable mechanics of a replenishment flywheel, and the markets they generalize to. Grocery is pattern 1; the rest is why the engine is deliberately vertical-agnostic. (Merges the former META_PATTERNS and EXPANSION_USE_CASES docs, numbering fixed — 2026-08-14.)

## 1. Replenishment Flywheel

Observe inventory → capture tiny usage signals → preserve preference corrections → recommend the next restock inside an approval boundary. The loop, not the list, is the product.

## 2. Runway Over Stock Count

Users don't think in units; they think in days. "About nine days of coffee left" beats "2 bags." Runway estimates come from observed depletion, not audits, and are labeled with confidence.

## 3. Depletion Pulses

Tiny signals after the fact: "burritos finished," "one tofu opened," "prep tomatoes half gone." Fuzzy is fine — pulses refine runway estimates over time instead of demanding precise counts.

## 4. Friction Budget

A cheaper item can lose if it costs too much cooking, prep, storage, cleanup, or coordination. Time cost is real cost — trip logging with an hourly value makes it visible.

## 5. Preference Signals Beat Naive Price Math

Rejected once → not the default again, even if cheaper. Corrections ("never again", "wrong format", "buy elsewhere") become durable derived preferences that override price-only logic. This generalizes to brand, texture, scent, package size, prep format, and workflow fit.

## 6. Bridge Inventory

Some inventory exists to prevent failure states: easy food in a household, toilet paper and dish soap, backup disposables in a restaurant, reliable coffee in an office. Bridge inventory is not waste by default — it needs its own ROI model, and unopened top-ups should rotate before they duplicate.

## 7. Substitution Graph

Know *why* item A can replace item B: same role, better unit economics, lower friction, better preference fit, equivalent quality, or a storage tradeoff. Ranking by the active objective makes the "why" explicit.

## 8. Acquisition Channel Independence

The flywheel works whether data arrives as retailer history, an export file, a paper receipt, a photo, or a manual shelf scan. History import is the default when available; everything else is a fallback, ranked honestly.

## 9. Approval-First Action Boundary

The system may draft, rank, and explain — a human approves. The boundary is structural (`checkout_available: false` is asserted, not promised), and telemetry only persists under explicit consent.

## 10. Explainable Recommendations

Every recommendation carries its reasoning: the objective used, the evidence seen, the confidence, and the tradeoff. Users should never have to re-derive the decision the tool just made.

## 11. Adapter Contract Over Hardcoded Connectors

No retailer-specific product decisions. The adapter contract (history, normalization, unit price, search, availability, substitutions, cart draft, provenance, freshness) comes first; retailers are instances. See [adapters.md](adapters.md).

## Expansion markets

The same eleven patterns, different vocabulary:

- **Restaurant / café restocking** — shift-runway instead of days, prep pulses, supplier substitution, par levels, emergency bridge stock; multi-person updates need auditability; food-safety compliance and yield/waste mapping are explicit non-goals for now.
- **Office kitchen / team pantry** — low-friction reorder thresholds, preference signals from shared depletion, multi-store comparison, budget-aware replenishment.
- **Studio / lab / maker space** — project-based runway, compatibility-constrained substitutions, minimum viable stock, reorder lead time.
- **Household essentials** — the personal case generalized: recurring consumables of every kind (cleaning, paper, toiletries, pet, basic pharmacy) through grocery-style channels.
