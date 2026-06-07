# Data Model

The prototype uses a JSON state file. It is intentionally plain so imports can be written later for Vons, Instacart, CSV, email receipts, or manual notes.

## Top-Level Shape

```json
{
  "as_of": "2026-05-24",
  "inventory_surface": {
    "type": "personal_grocery",
    "label": "Home groceries"
  },
  "acquisition_channel": "retailer_history_import",
  "order": {
    "store": "Example Grocery",
    "date": "2026-05-20",
    "total": 112.19
  },
  "items": [],
  "pulses": [],
  "preferences": [],
  "dietary_profiles": [],
  "substitutions": [],
  "sourcing_research": [],
  "retailer_profiles": []
}
```

## Item

```json
{
  "name": "Example burritos",
  "role": "bridge_food",
  "category": "frozen_meal",
  "storage": "frozen",
  "spend": 6.42,
  "units_total": 8,
  "units_remaining": 0,
  "remaining_fraction": null,
  "notes": "Immediate food."
}
```

Use `units_total` and `units_remaining` when countable. Use `remaining_fraction` when the user reports a rough fullness signal such as `2/3 full`.

Use `category` to distinguish food and non-food inventory inside the same run. Examples: `frozen_meal`, `dry_good`, `coffee`, `cleaning_supply`, `paper_good`, `toiletry`, `pet_supply`, `pharmacy_basic`, `operator_supply`.

### Optional Pricing Fields

The pricing-status field is additive and lets the dashboard surface how confident we are in a row's price. The dashboard does not require these fields; items without them are treated as `priced` with no captured check date, which the freshness panel flags as stale so the user can refresh.

| Field | Type | Meaning |
|-------|------|---------|
| `pricing_status` | string | One of `priced`, `unpriced`, `estimated`, `gift`. The dashboard shows a freshness badge for each. |
| `last_price_check` | ISO date (`YYYY-MM-DD`) | When the price was last confirmed. Items missing this field show as `no check date` in the Data Freshness panel. |
| `added_on` | ISO date | When the item entered the run. The freshness panel uses this as a fallback if `last_price_check` is missing. |

`estimated` is intentionally rendered as stale even when the check date is today: the freshness panel's job is to make low-confidence data visible until a real receipt or store page replaces it.

## Inventory Surface

```json
{
  "type": "restaurant_pantry",
  "label": "Cafe dry storage",
  "operators": 3
}
```

Known surface types:

- `personal_grocery`
- `household_essentials`
- `restaurant_pantry`
- `office_kitchen`
- `studio_supplies`
- `event_inventory`
- `custom`

## Acquisition Channel

Known channels:

- `retailer_history_import`
- `digital_history`
- `receipt_import`
- `in_person_onboarding`
- `manual_inventory`
- `photo_assisted`
- `operator_log`

## Preference

```json
{
  "key": "avoid_diced_chicken",
  "signal": "Diced microwave chicken was rejected.",
  "rule": "Prefer strips, fillets, or whole pieces."
}
```

## Dietary Profile

```json
{
  "profile_id": "household-default",
  "label": "Household default",
  "restrictions": [
    {
      "type": "food_allergy",
      "value": "peanuts",
      "safety_tier": "safety_critical",
      "behavior": "block_until_review"
    },
    {
      "type": "lifestyle",
      "value": "vegetarian",
      "safety_tier": "strong_preference",
      "behavior": "warn"
    }
  ]
}
```

Dietary profiles are optional and explicit. Allergies are one type of dietary restriction, not the top-level module. Safety-critical restrictions default to `needs review` when product data is missing or ambiguous.

## Substitution

```json
{
  "current": "Tyson diced chicken",
  "candidate": "Tyson grilled strips",
  "current_unit_price": 0.45,
  "candidate_unit_price": 0.454,
  "fit": "better",
  "read": "Same price tier, better form factor."
}
```

## Sourcing Research

```json
{
  "item": "Dish soap",
  "current_source": "Default grocery store",
  "current_unit_price": 0.19,
  "recommendation": "Research warehouse or online refill options.",
  "alternatives": [
    {
      "source": "Warehouse store",
      "unit_price": 0.12,
      "constraints": ["membership", "storage"],
      "confidence": "low",
      "checked_date": "2026-05-25"
    }
  ]
}
```

Use sourcing research only when it is likely to change behavior. The product should not make the user compare ten stores for every item.

`retailer_history_import` is the preferred setup path. Receipt import, photo-assisted entry, and manual inventory exist because real users sometimes lack account history, shop in person, or need a rescue path.

## Retailer Profile

Retailer profiles describe what a store adapter can do. See `docs/RETAILER_ADAPTERS.md` for the full contract.

```json
{
  "id": "generic.browser_retailer",
  "name": "Generic Browser Retailer",
  "type": "grocery",
  "channels": ["pickup", "delivery", "in_person"],
  "acquisition_methods": ["retailer_history_import", "browser_assisted"],
  "capabilities": {
    "purchase_history": true,
    "product_search": true,
    "price_lookup": true,
    "unit_price": true,
    "availability": true,
    "substitutions": true,
    "cart_draft": true,
    "order_submit": false
  }
}
```
