# Design Direction

The design source of truth, its evidence base, and how the shipped dashboard maps to both. (Merges the former root DESIGN.md and PRODUCT_DESIGN_RESEARCH_2026.md — 2026-08-14.)

## Product feel

A calm, competent household operator: practical, warm, legible, quietly beautiful. Not a spreadsheet, not a coupon site, not a chatbot bolted onto a table.

## Surfaces

1. **Guided setup** — starts with stores, not forms ("which retailers do you use?"), then builds adapter profiles and imports history where possible.
2. **Command-center dashboard** — the scanable status and decision surface. Shipped: the dark command-center chosen in decision D1 (first-wow cards, runway, dietary chips, evidence drawers, corrections capture, cart plan).
3. **Assistant loop** — depletion pulses, corrections, restock drafting. Shipped: the MCP server and the correction-capture panel.

## Visual direction

Editorial operations: human-readable; warm but not cute; dense enough for repeated use; generous enough for tired users. Tables for price/substitution comparisons; cards for decision blocks; progressive disclosure for evidence; the "why" sits beside the recommendation; correction actions stay visible ("never again", "too expensive", "wrong format"). System sans-serif; large high-contrast numerals; sentence case; no untaught jargon.

Color carries meaning — green: good runway/savings; amber: watch items, low confidence; red: critical risk; blue: research; neutral: stable stock. The shipped dark theme keeps this mapping (see `rendering/layout.py`).

Visual companion for the future guided-setup surface: [design-preview.html](design-preview.html) — a dependency-free static mock kept as the north star for surfaces not yet built (D2 decision, 2026-08-14).

## Research findings (May 2026 synthesis)

Ten findings from a survey of grocery/household apps and operator tools, still load-bearing:

1. **First use must produce a result immediately** — hence the 30-second sample-dashboard quick start.
2. **Don't make people enter data the system can infer** — hence import-first onboarding.
3. **Human-readable beats technically complete** — runway in days, fuzzy pulses.
4. **Beauty is a usability feature here** — the dashboard is looked at tired, at a glance, repeatedly.
5. **Accessibility is a product requirement, not polish** — contrast, sizing, and meaning-plus-color (never color alone).
6. **AI must stay explainable and undoable** — every recommendation shows its objective, evidence, and confidence; corrections are permanent undo.
7. **Unit economics must be first-class** — normalized unit prices and size parsing in the contract itself.
8. **Substitutions need global defaults and per-item overrides** — objectives are global; corrections are per-item and win.
9. **Sourcing research is its own stage** — separate panel, check dates, freshness aging.
10. **Trust requires price provenance** — every price carries where-it-came-from and when-it-was-checked.

UX metrics that matter: time-to-first-dashboard; correction-add friction; decisions the dashboard resolves without re-derivation; percentage of recommendations carrying visible reasoning.
