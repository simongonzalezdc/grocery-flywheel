# Workflow Spec

## Loop

1. Start from a grocery run.
2. Classify items by role: bridge food, pantry base, protein, flavor unlock, drink, coffee, or household support.
3. Record price, size, quantity, storage, and friction.
4. Collect depletion pulses.
5. Compute runway and risk.
6. Record preference signals.
7. Recommend the next stop.
8. Render dashboard.
9. Wait for user approval before any cart mutation or purchase.

## Acquisition Channels

- `digital_history`: prior grocery orders or store account history.
- `receipt_import`: paper or email receipts entered manually or parsed later.
- `in_person_onboarding`: first store trip with no prior structured history.
- `manual_inventory`: shelf, pantry, fridge, freezer, or stockroom scan.
- `photo_assisted`: images used to identify items and rough quantities.
- `operator_log`: multi-person restocking notes for restaurant, office, or studio use.

## Item Roles

- `bridge_food`: immediate eating with very low decision load.
- `pantry_base`: staple food with long runway but higher preparation need.
- `protein`: protein anchor, including tofu, meat, dairy, and legumes.
- `flavor_unlock`: spice, sauce, acid, salsa, condiment, or ingredient that makes staples edible.
- `drink`: non-water drink or ready protein drink.
- `coffee`: dedicated caffeine/ritual supply.
- `support`: household or baking/pantry support.

## Depletion Pulse Shape

A pulse should be short and forgiving:

```text
burritos finished, tofu half eaten, cereal 2/3 full
```

The system can map this into structured state later. The user should not have to speak in schema.

## Recommendation Rules

1. Prefer foods that will actually be eaten over foods that only win on spreadsheet math.
2. Preserve bridge foods, but track their cost and depletion speed.
3. Treat dry legumes and bulk staples as runway extenders when the user can actually prepare them.
4. Treat spices and sauces as high-leverage because they unlock multiple pantry-base meals.
5. Never confuse same-SKU inflation with package-size or brand substitutions.
6. Keep checkout and live-cart changes approval-first.

## Current Known Preference Rules

- Bustelo is the moka-pot default unless a better price-quality source is confirmed.
- Dried beans, garbanzos, and lentils are welcome.
- Diced microwave chicken is rejected; prefer strips, fillets, or whole pieces.
- Bridge foods get eaten first, then cooking starts. This is expected behavior.

## Generalization Rule

When adding a feature, ask whether it is grocery-specific or a replenishment flywheel primitive. Keep grocery-specific language in module docs and promote reusable mechanics into `META_PATTERNS.md`.
