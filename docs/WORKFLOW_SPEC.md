# Workflow Spec

## Loop

1. Start from a grocery-store or household restocking run.
2. Classify items by role: bridge food, pantry base, protein, flavor unlock, drink, coffee, household consumable, critical household essential, pet supply, operator consumable, or support.
3. Record price, size, quantity, storage, and friction.
4. Collect depletion pulses.
5. Compute runway and risk.
6. Record preference signals.
7. Run sourcing research for selected recurring, bulk-friendly, or suspiciously expensive items.
8. Recommend the next stop.
9. Render dashboard.
10. Wait for user approval before any cart mutation or purchase.

The first-run dashboard should emphasize estimated savings and sourcing alternatives before deeper restock automation.

## Retailer Adapter Loop

1. Create or select retailer profile.
2. Detect adapter capabilities.
3. Import purchase history when possible.
4. Normalize orders and items into the canonical data model.
5. Use search/price capabilities for sourcing research.
6. Use cart-draft capabilities only after explicit user approval.

Do not hardcode product decisions around specific retailers. Specific stores are adapter instances.

## Acquisition Channels

- `digital_history`: prior grocery orders or store account history.
- `retailer_history_import`: preferred first-run path using purchase history from retailer accounts.
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
- `household_consumable`: recurring non-food household item such as dish soap, paper towels, detergent, toiletries, or trash bags.
- `critical_household_essential`: non-food item whose stockout creates outsized disruption.
- `pet_supply`: pet food, litter, medicine basics, or recurring animal-care consumables.
- `operator_consumable`: restaurant, cafe, office, studio, lab, or event supply that is depleted through operations.
- `support`: baking, pantry, household, or miscellaneous support.

## Depletion Pulse Shape

A pulse should be short and forgiving:

```text
burritos finished, tofu half eaten, cereal 2/3 full
```

The system can map this into structured state later. The user should not have to speak in schema.

## Recommendation Rules

1. Prefer items that will actually be eaten or used over items that only win on spreadsheet math.
2. Preserve bridge foods, but track their cost and depletion speed.
3. Treat dry legumes and bulk staples as runway extenders when the user can actually prepare them.
4. Treat spices and sauces as high-leverage because they unlock multiple pantry-base meals.
5. Treat critical household essentials as stockout-sensitive even when they are not expensive.
6. Research alternative sources for high-leverage items, but do not split the cart unless savings, reliability, or quality justify the extra trip.
7. Never confuse same-SKU inflation with package-size or brand substitutions.
8. Keep checkout and live-cart changes approval-first.

## Sourcing Research Stage

See `docs/SOURCING_RESEARCH_STAGE.md`.

This stage asks: "Is this item worth buying somewhere else?"

Candidate sources can include the current grocery store, another grocery store, a warehouse club, Target/Walmart-style retailer, online retailer, ethnic market, restaurant supply store, office supplier, or specialty store.

## Current Known Preference Rules

- Bustelo is the moka-pot default unless a better price-quality source is confirmed.
- Dried beans, garbanzos, and lentils are welcome.
- Diced microwave chicken is rejected; prefer strips, fillets, or whole pieces.
- Bridge foods get eaten first, then cooking starts. This is expected behavior.

## Generalization Rule

When adding a feature, ask whether it is grocery-specific or a replenishment flywheel primitive. Keep grocery-specific language in module docs and promote reusable mechanics into `META_PATTERNS.md`.
