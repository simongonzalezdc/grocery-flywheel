# Meta Patterns

These are the reusable mechanics being extracted from the grocery module.

## 1. Replenishment Flywheel

Observe inventory, track usage, preserve corrections, recommend the next restock, and repeat.

This applies to groceries, cleaning supplies, toiletries, restaurant pantry, office kitchens, maker supplies, household essentials, and event inventory.

## 2. Runway Over Stock Count

The useful question is not only "what is left?" It is "how long does this setup keep working under real behavior?"

Runway can be measured in days, shifts, service periods, meals, events, or batches.

## 3. Depletion Pulses

The user should not need a full inventory audit. Tiny updates are enough:

- "Burritos finished."
- "One tofu opened."
- "Two cases of cups left."
- "Prep tomatoes are half gone."

The system should accept fuzzy signals and improve estimates over time.

## 4. Friction Budget

Restocking decisions must account for the effort needed to use the item. A cheaper item can lose if it requires too much cooking, prep, storage, cleanup, or coordination.

## 5. Preference Signals Beat Naive Price Math

If the user rejects diced chicken, diced chicken stops being the default even if it is cheaper. If a detergent scent is disliked, that detergent stops being the default even if the price is strong. This generalizes to brand, texture, scent, package size, prep format, storage, and workflow fit.

## 6. Bridge Inventory

Some inventory exists to prevent failure states. In groceries this is immediate food. In households it is toilet paper, dish soap, laundry detergent, trash bags, pet food, or medicine basics. In restaurants it might be emergency prep or backup disposables. In offices it might be reliable coffee or snacks.

Bridge inventory is not wasteful by default; it needs its own ROI model.

## 7. Substitution Graph

The system should know why item A can replace item B:

- same role
- better unit economics
- lower friction
- better preference fit
- equivalent quality
- different storage tradeoff

## 8. Acquisition Channel Independence

The flywheel should work whether data comes from retailer history, a store account, paper receipt, photo, manual shelf scan, or in-person onboarding.

Default to retailer history import when available. Use receipt and manual entry as fallback paths, not as the ideal setup experience.

## 11. Adapter Contract Over Hardcoded Connectors

Do not build the product around one retailer at a time. Define the shared adapter contract first, then map specific retailers into it.

Reusable adapter primitives:

- purchase history
- item normalization
- unit price
- product search
- availability
- substitutions
- cart draft
- provenance
- freshness

## 9. Approval-First Action Boundary

The system can recommend and prepare drafts, but purchasing and external mutations require explicit approval.

## 10. Explainable Recommendations

Every recommendation should show the reason: price, runway, preference, friction, quality, or missing unlock.
