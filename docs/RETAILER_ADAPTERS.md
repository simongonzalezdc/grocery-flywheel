# Retailer Adapter Architecture

The product should not be built one retailer at a time. Retailers share enough structure that Grocery Flywheel needs a reusable adapter system.

## Core Idea

Every retailer adapter maps store-specific data into the same canonical objects:

- retailer profile
- acquisition method
- order history
- order item
- normalized unit price
- product identity
- substitution candidate
- sourcing candidate
- cart draft action
- evidence/provenance

The product should ask: "What capabilities does this retailer expose?" not "Which hardcoded retailer is this?"

## Adapter Capability Levels

### Level 0: Profile Only

The user can describe a retailer manually:

- name
- type
- region
- common categories
- whether it is online, in-person, warehouse, specialty, restaurant supply, or local

Useful for small local stores and early onboarding.

### Level 1: File Or Receipt Import

The adapter can ingest exported data:

- CSV
- PDF
- email receipt
- paper receipt OCR
- copied order text

This is a fallback path, not the ideal setup.

### Level 2: Retailer History Import

The adapter can import past purchases from a retailer account, preferably browser-assisted or API-backed.

This is the default happy path because repeated purchase history produces the useful baseline.

### Level 3: Product Search And Price Lookup

The adapter can search current products and prices:

- current price
- size
- unit price
- pickup/delivery/shipping constraints
- membership requirements
- availability

This powers sourcing research.

### Level 4: Cart Draft

The adapter can prepare a cart draft:

- add item
- remove item
- set quantity
- record unavailable items
- show substitutions

Checkout remains explicit-approval only.

### Level 5: Purchase Submission

Out of MVP scope. If ever supported, it requires explicit final user approval and a very clear audit trail.

## Retailer Profile Schema

```json
{
  "id": "retailer.example",
  "name": "Example Grocery",
  "type": "grocery",
  "region": "US",
  "channels": ["pickup", "delivery", "in_person"],
  "acquisition_methods": ["retailer_history_import", "browser_assisted"],
  "capabilities": {
    "purchase_history": true,
    "product_search": true,
    "price_lookup": true,
    "unit_price": true,
    "availability": true,
    "substitutions": true,
    "cart_draft": false,
    "order_submit": false
  },
  "constraints": ["login_required", "location_specific_prices"],
  "provenance": {
    "price_source": "browser",
    "history_source": "account"
  }
}
```

## Canonical Order Item

```json
{
  "retailer_id": "retailer.example",
  "order_id": "123",
  "purchased_at": "2026-05-20",
  "name": "Dish soap",
  "brand": "Example Brand",
  "quantity": 1,
  "package_size": "24 fl oz",
  "price_paid": 4.99,
  "unit_price": 0.208,
  "unit": "fl oz",
  "category": "cleaning_supply",
  "retailer_sku": "optional",
  "upc": "optional",
  "provenance": "retailer_history_import"
}
```

## Setup UX

The setup flow should not ask the user to pick a hardcoded connector from a tiny list. It should ask:

1. Which stores do you use?
2. Do you have a login/order history for any of them?
3. Can we import history, export files, or use browser-assisted capture?
4. Which stores should be used only for sourcing research?
5. Which stores should never be used?

Then the product builds adapter profiles.

## Adapter Builder

Users and future agents should be able to add a new retailer by creating a profile and selecting capability level:

1. Name the retailer.
2. Pick retailer type.
3. Pick acquisition methods.
4. Confirm sample order fields.
5. Map item name, price, quantity, size, and date.
6. Test import on a small sample.
7. Save the profile.

## Why This Is Better

This avoids hardcoding Vons, Walmart, Target, Costco, Amazon, and every local market as separate product decisions. Those are adapter instances. The product decision is the adapter contract.

Vons can be the first real test fixture because we have evidence. It is not the architecture.

