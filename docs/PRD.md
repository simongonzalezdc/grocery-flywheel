# Product Requirements

## Product

Grocery Flywheel is a local-first assistant workflow for neurodivergent-friendly grocery-store and household replenishment. It learns from real orders, in-person store inputs, small depletion check-ins, and explicit user corrections to produce high-ROI next-cart recommendations.

Grocery is the first module. The reusable product pattern is a replenishment flywheel for any inventory surface where the user needs restocking decisions with low cognitive overhead.

## Problem

The user does not need another static shopping list. The user needs a system that:

- Knows what was actually bought.
- Understands what gets eaten, opened, used first, or left untouched.
- Preserves no-thought food as a real requirement, not a moral failure.
- Treats cleaning supplies, paper goods, toiletries, pet supplies, and other household consumables as first-class inventory.
- Distinguishes price wins from items that will not get used.
- Researches whether recurring items should be bought somewhere else.
- Reduces repeated decision work at the next grocery run.

## Target User

Primary: one person managing groceries and household consumables under variable executive function, variable cooking/cleaning/shopping energy, and price pressure.

Secondary: households that want a private, explainable grocery planning loop without handing purchase history to another SaaS vendor.

Expansion: small operators with recurring restocking needs, such as restaurants, cafes, office kitchens, studios, labs, and event teams.

## MVP Goals

1. Maintain a structured grocery state file.
2. Track grocery-store runs, household items, roles, prices, and remaining inventory.
3. Capture depletion pulses quickly.
4. Compute known consumption value and rough runway.
5. Compare substitutions by unit economics and preference fit.
6. Render a readable static dashboard.
7. Produce next-cart recommendations without submitting purchases.
8. Make retailer purchase-history import the default first-run path.
9. Support first-run onboarding when the user has no retailer order history.
10. Support in-person shopping through receipt/manual/photo-friendly state entry as fallback paths.
11. Support a sourcing research stage for selected recurring or overpriced items.

## Non-Goals

- Do not submit grocery orders.
- Do not mutate live carts without explicit user approval.
- Do not give medical or dietary prescriptions.
- Do not scrape authenticated grocery data without an explicit connector/session.
- Do not shame bridge-food behavior.
- Do not limit the product to edible items.
- Do not become a full restaurant POS, accounting, or compliance system in the MVP.

## Core Jobs

### Job 1: Know What Is Left

As a user, I can report tiny inventory signals so the system estimates what remains without requiring a full pantry, fridge, freezer, cabinet, or cleaning-supply audit.

### Job 2: Build a Better Next Cart

As a user, I can see what should be bought next based on actual depletion, missing unlocks, critical household stockouts, price per useful unit, and items I will actually use.

### Job 3: Preserve Preference Corrections

As a user, when I say "do not buy diced chicken again", the system remembers that form factor matters and changes future recommendations.

### Job 4: Explain the Math

As a user, I can see why an item is recommended or rejected, including when a cheaper item loses because it adds friction or fails a preference signal.

### Job 5: Start From Zero

As a user with no prior order history, I can onboard from an in-person store trip, receipt, or manual shelf scan without needing perfect data.

### Job 6: Import Real History Fast

As a user with retailer accounts, I can connect or export my purchase history so the product can build a useful baseline from my actual repeated purchases.

### Job 7: Generalize The Pattern

As a product builder, I can identify which grocery mechanics also apply to restaurant restocking, office supplies, and other inventory surfaces.

### Job 8: Buy The Right Thing In The Right Place

As a user, I can see when an item is worth buying online, at a warehouse store, at a specialty store, or from a restaurant/office supplier instead of my default grocery store.

## Acceptance Criteria

- A sample state file can be rendered into a static dashboard.
- Runway is calculated from observed depletion and total order cost.
- Preference signals appear in the dashboard.
- Same-brand substitution comparisons show unit price and fit.
- The docs state that checkout is approval-only.
- Tests cover consumption math and substitution ranking.
- The docs make retailer history import the preferred first-run path.
- The docs cover in-person onboarding and store-agnostic fallback acquisition channels.
- Meta-patterns are documented separately from grocery-specific behavior.
- Non-food household consumables are represented in the docs and sample state.
- Sourcing alternatives appear in the data model and dashboard.
