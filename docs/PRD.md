# Product Requirements

## Product

Grocery Flywheel is a local-first assistant workflow for neurodivergent-friendly grocery planning. It learns from real orders, in-person store inputs, small depletion check-ins, and explicit user corrections to produce high-ROI next-cart recommendations.

Grocery is the first module. The reusable product pattern is a replenishment flywheel for any inventory surface where the user needs restocking decisions with low cognitive overhead.

## Problem

The user does not need another static shopping list. The user needs a system that:

- Knows what was actually bought.
- Understands what gets eaten first versus what remains.
- Preserves no-thought food as a real requirement, not a moral failure.
- Distinguishes price wins from food that will not get used.
- Reduces repeated decision work at the next grocery run.

## Target User

Primary: one person managing groceries under variable executive function, variable cooking energy, and price pressure.

Secondary: households that want a private, explainable grocery planning loop without handing purchase history to another SaaS vendor.

Expansion: small operators with recurring restocking needs, such as restaurants, cafes, office kitchens, studios, labs, and event teams.

## MVP Goals

1. Maintain a structured grocery state file.
2. Track grocery runs, items, roles, prices, and remaining inventory.
3. Capture depletion pulses quickly.
4. Compute known consumption value and rough runway.
5. Compare substitutions by unit economics and preference fit.
6. Render a readable static dashboard.
7. Produce next-cart recommendations without submitting purchases.
8. Support first-run onboarding when the user has no digital order history.
9. Support in-person shopping through receipt/manual/photo-friendly state entry.

## Non-Goals

- Do not submit grocery orders.
- Do not mutate live carts without explicit user approval.
- Do not give medical or dietary prescriptions.
- Do not scrape authenticated grocery data without an explicit connector/session.
- Do not shame bridge-food behavior.
- Do not become a full restaurant POS, accounting, or compliance system in the MVP.

## Core Jobs

### Job 1: Know What Is Left

As a user, I can report tiny inventory signals so the system estimates what remains without requiring a full pantry audit.

### Job 2: Build a Better Next Cart

As a user, I can see what should be bought next based on actual depletion, missing flavor unlocks, price per useful unit, and foods I will actually eat.

### Job 3: Preserve Preference Corrections

As a user, when I say "do not buy diced chicken again", the system remembers that form factor matters and changes future recommendations.

### Job 4: Explain the Math

As a user, I can see why an item is recommended or rejected, including when a cheaper item loses because it adds friction or fails a preference signal.

### Job 5: Start From Zero

As a user with no prior order history, I can onboard from an in-person store trip, receipt, or manual shelf scan without needing perfect data.

### Job 6: Generalize The Pattern

As a product builder, I can identify which grocery mechanics also apply to restaurant restocking, office supplies, and other inventory surfaces.

## Acceptance Criteria

- A sample state file can be rendered into a static dashboard.
- Runway is calculated from observed depletion and total order cost.
- Preference signals appear in the dashboard.
- Same-brand substitution comparisons show unit price and fit.
- The docs state that checkout is approval-only.
- Tests cover consumption math and substitution ranking.
- The docs cover in-person onboarding and store-agnostic acquisition channels.
- Meta-patterns are documented separately from grocery-specific behavior.
