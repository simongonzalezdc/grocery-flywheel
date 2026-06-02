# Design Source Of Truth

## Product Feel

Grocery Flywheel should feel like a calm, competent household operator. It is practical, warm, legible, and quietly beautiful.

It should not feel like a spreadsheet, a coupon site, or a chatbot bolted onto a table.

## Primary Surface

Use a three-part product surface:

1. **Guided setup** for fast first value.
2. **Command center dashboard** for scanable status and decisions.
3. **Assistant loop** for depletion pulses, corrections, and restock drafting.

The dashboard is the proof surface. The assistant loop is the habit. The restock draft is the action.

Guided setup starts with stores, not forms: "Which retailers do you use?" The product should then detect or build retailer adapter profiles and pull history where possible.

## Visual Direction

Style: editorial operations dashboard.

Qualities:

- human-readable
- warm but not cute
- beautiful but not decorative
- dense enough for repeated use
- generous enough for tired users
- clear enough for groceries, cleaning supplies, and operator inventory

## Layout

- Start with one clear status row: runway, urgent stockouts, next action.
- Use cards only for individual decision blocks, not for every section.
- Use tables for price and substitution comparisons.
- Use progressive disclosure for evidence.
- Put the "why" beside the recommendation, not hidden in a tooltip.
- Make correction actions visible: "never again", "good substitute", "too expensive", "wrong format".

## Typography

- Use system sans-serif for UI.
- Use large, high-contrast numerals for runway and spend.
- Keep body copy short.
- Prefer sentence case.
- Avoid jargon in the UI unless the term is taught in context.

## Color

Use color for meaning:

- green: good runway, savings, accepted recommendation
- amber: watch item, low confidence, upcoming need
- red: critical stockout or purchase risk
- blue: research/source info
- neutral: stable inventory

Avoid one-note palettes and decorative gradients.

## Interaction Rules

- First result before full setup.
- No required perfect inventory audit.
- Let users answer with fuzzy language.
- Every recommendation can be ignored.
- Every AI action can be corrected.
- Checkout and external account mutation require explicit approval.

## Accessibility

- WCAG 2.2 is the floor.
- Keyboard navigation must work.
- Focus states must be visible.
- Touch targets must be comfortable.
- Text must reflow on mobile.
- Color must never be the only signal.

## Signature Components

### Runway Card

Shows how long the current setup should last and what could break first.

### Next Action Strip

One row of the highest-leverage actions: buy, wait, research, cook, check stock, or correct.

### Sourcing Card

Shows whether an item is worth buying elsewhere. It includes current source, best alternative, unit price, savings, constraints, and confidence.

### Retailer Adapter Card

Shows which stores are connected or configured, what each adapter can do, and where the data came from:

- history import
- price lookup
- unit price
- availability
- substitutions
- cart draft

The UI should make incomplete adapters feel useful, not broken. A local market with receipt-only support can still be a valid source.

### Correction Chips

One-tap ways to teach the system:

- never again
- good default
- wrong format
- too expensive
- buy elsewhere
- emergency only

### Evidence Drawer

Expandable details for users who want the math.

## Design Standard

The interface should make the user think:

"I can trust this, I can understand this, and I do not have to solve the whole grocery problem again."
