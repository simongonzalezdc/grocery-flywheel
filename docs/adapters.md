# Retailer Adapters, Onboarding, and Sourcing Research

One doc for everything between "a store exists" and "sourcing research is running": the adapter contract, the onboarding paths, and how sourcing alternatives get generated. (Merges the former RETAILER_ADAPTERS, ONBOARDING, and SOURCING_RESEARCH_STAGE docs — 2026-08-14.)

## Status, honestly

Shipped today: capability-profile validation and scoring (`retailer_adapter.py`), normalized-JSON and CSV history import (`grocery-flywheel import`), and sourcing-alternative generation from a built-in research library (`sourcing.py`). Designed but not automatic: browser-assisted account import, receipt OCR, product-search adapters, cart drafting. Nothing in this product logs into a retailer account.

## Adapter core idea

The product is not built one retailer at a time. Every retailer maps store-specific data into the same canonical objects — profile, acquisition method, order item, normalized unit price, product identity, substitution candidate, sourcing candidate, cart-plan action, evidence/provenance. The question is always "what capabilities does this retailer expose?", never "which hardcoded retailer is this?".

## Capability levels

- **Level 0 — Profile only.** The user describes a retailer manually (name, type, region, categories, channels). Useful for small local stores.
- **Level 1 — File or receipt import.** CSV, PDF, email receipts, OCR, copied order text. A fallback path. *(CSV shipped; the rest designed.)*
- **Level 2 — Retailer history import.** Past purchases from an account, ideally browser-assisted or API-backed. The default happy path: repeated purchase history produces the useful baseline. *(File-based import shipped.)*
- **Level 3 — Product search and price lookup.** Current prices, sizes, unit prices, constraints, availability. Powers sourcing research. *(A built-in research library stands in for this today.)*
- **Level 4 — Cart draft.** Prepare a draft cart for review. Checkout stays explicit-approval-only. *(Internal cart plans shipped; retailer cart drafting designed.)*
- **Level 5 — Purchase submission.** Out of scope. If ever supported: explicit final approval plus a full audit trail.

## Retailer profile schema

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
  "provenance": { "price_source": "browser", "history_source": "account" }
}
```

Profiles are validated and scored by capability coverage (`validate_retailer_profile`, `adapter_score`, `best_import_profiles` in `retailer_adapter.py`). One rule is non-negotiable: `order_submit` stays false — the adapter contract never grows a checkout surface.

## Onboarding paths, ranked honestly

Default first: **retailer history import** (repeated behavior beats one receipt). Then:

1. Retailer history import (shipped for file exports)
2. Browser-assisted account import (designed)
3. Email receipt / order-confirmation import (designed)
4. Paper receipt scan (designed)
5. In-person store walkthrough (manual flows below)
6. Manual shelf scan

The walkthrough and shelf-scan flows exist for zero-history starts: they ask what surface you're managing, the time horizon, storage, friction budget, and which items must never run out — then build a low-confidence starter baseline from fuzzy counts ("full, half, almost gone, sealed, opened").

**First-run questions** (any path): which inventory surface? which order histories exist? how many people/periods to cover? budget pressure? what can be cooked/stored/delegated? what must never run out? what should never repeat? which store types are allowed?

## Sourcing research

Sourcing asks, per recurring or high-leverage item: is the current store actually the best place to buy this?

- **Trigger:** item is recurring, matches a known research category (coffee, household essentials, pantry staples), or spend crosses the leverage threshold.
- **Method:** the built-in research library proposes alternatives (online bulk, warehouse club, bulk pantry) with unit-price multipliers, savings estimates, constraints (membership, storage, subscription), and confidence — each stamped with a check date so freshness badges can age it out.
- **Objective-aware:** alternatives are ranked by the active objective (e.g. `fewer_trips` penalizes trip friction hard; `allergy_safe` gates on dietary status).
- **Dietary gate:** an item with an unresolved dietary conflict reads "Do not buy until dietary conflict is resolved" — savings never outrank safety.
- **Honest default:** when nothing beats the current source by ≥10% with acceptable friction, the recommendation is "keep with the normal store."

Hand-authored sourcing rows in the state (`item`, `current_source`, `alternatives[]` with `checked_date`, …) are honored as-is; auto-generation only fills an empty list, and only under an explicit objective.
