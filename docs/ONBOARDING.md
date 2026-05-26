# Onboarding

The product must work even when the user has no grocery history, shops in person, or needs non-food household replenishment.

## Onboarding Principle

Use retailer history import as the default path. It is the fastest way to get a meaningful baseline because it captures repeated behavior, not one random receipt.

Retailer import must be adapter-based, not hardcoded to one store. The setup asks which stores the user uses, then creates retailer profiles and detects which capabilities each store supports.

Support every path, but rank them honestly:

1. Retailer history import.
2. Browser-assisted retailer account import.
3. Email receipt or order confirmation import.
4. Paper receipt scan.
5. In-person store walkthrough.
6. Manual shelf scan.

Manual and receipt flows are fallback/rescue paths, not the desired happy path.

## Onboarding Modes

### 1. Retailer History Import

Best when the user has retailer account access or exportable order history.

Flow:

1. Connect, export, or browser-import recent purchases.
2. Detect retailer adapter capabilities.
3. Normalize purchases into canonical order items.
4. Classify item roles.
5. Estimate savings and sourcing alternatives.
6. Ask for current remaining-stock signal.
7. Generate runway and next-cart risks.

### 2. Add A Retailer

Best when the retailer is not prebuilt.

Flow:

1. Name the retailer.
2. Choose type: grocery, warehouse, online, local market, restaurant supply, office supplier, specialty.
3. Choose available acquisition methods.
4. Test with one sample order, export, or receipt.
5. Save a retailer adapter profile.

### 3. Email Or Digital Receipt Import

Best when full retailer history is unavailable but order confirmations or emailed receipts exist.

Flow:

1. Import receipts or order confirmations.
2. Cluster repeated items.
3. Ask whether this represents normal behavior or a one-off run.
4. Generate a lower-confidence baseline.

### 4. Paper Receipt Fallback

Best when the user just went to a physical store.

Flow:

1. Enter or scan receipt.
2. Confirm item names and rough categories.
3. Mark which items are immediate food, pantry base, flavor unlocks, cleaning supplies, paper goods, toiletries, pet supplies, or recurring essentials.
4. Schedule depletion pulse.

### 5. Store Walkthrough

Best when the user is starting from zero.

Flow:

1. Ask what the user is trying to support: one person, household, restaurant, office, event, or project.
2. Ask time horizon: days, week, month, service period, or event date.
3. Ask available storage: shelf, fridge, freezer, stockroom, vehicle, or none.
4. Ask friction budget: no-cook, microwave, batch cook, prep team, or normal operations.
5. Build a starter inventory map.
6. Capture the first purchase or planned purchase.

### 6. Manual Shelf Scan

Best when the user has inventory but no records.

Flow:

1. Capture broad categories first.
2. Accept fuzzy counts: full, half, almost gone, sealed, opened.
3. Identify missing unlocks.
4. Create first runway estimate with low confidence.

## First-Run Questions

- What inventory surface are we managing?
- Which retailer accounts or order histories can we use?
- How many people or service periods does it need to cover?
- What is the budget pressure?
- What can be cooked, cleaned, prepped, stored, or delegated?
- What items must never run out?
- What items are disliked, avoided, or not worth repeating?
- What store types are allowed: grocery, warehouse, restaurant supply, farmers market, convenience, online?

## Compatibility Requirement

The onboarding flow must support:

- grocery pickup history
- retailer account history
- in-person grocery stores
- cleaning, paper goods, toiletries, pet supplies, basic pharmacy, and other grocery-store categories
- warehouse stores
- small ethnic markets
- farmers markets
- restaurant supply stores
- office or operator restocking
- manual entry when no receipt exists
