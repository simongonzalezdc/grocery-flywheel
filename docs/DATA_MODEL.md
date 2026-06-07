# Data Model

The prototype uses a JSON state file. It is intentionally plain so imports can be written later for Vons, Instacart, CSV, email receipts, or manual notes.

## Top-Level Shape

```json
{
  "schema_version": "2026-05-26.mvp1",
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

Every imported/canonical object carries `schema_version`. Sensitive fields also
carry or inherit privacy metadata so local mode, hosted beta, export, and delete
behavior can be verified instead of inferred.

## Item

```json
{
  "schema_version": "2026-05-26.mvp1",
  "name": "Example burritos",
  "role": "bridge_food",
  "category": "frozen_meal",
  "storage": "frozen",
  "spend": 6.42,
  "units_total": 8,
  "units_remaining": 0,
  "remaining_fraction": null,
  "notes": "Immediate food.",
  "privacy_class": "sensitive_purchase_history",
  "confidence": "medium",
  "source_provenance": {
    "source": "retailer_history_import",
    "source_row_id": "line-1"
  },
  "product_evidence": []
}
```

Use `units_total` and `units_remaining` when countable. Use `remaining_fraction` when the user reports a rough fullness signal such as `2/3 full`.

Use `category` to distinguish food and non-food inventory inside the same run. Examples: `frozen_meal`, `dry_good`, `coffee`, `cleaning_supply`, `paper_good`, `toiletry`, `pet_supply`, `pharmacy_basic`, `operator_supply`.

Product evidence used for dietary decisions must include `evidence_type`,
`source`, `checked_date`, and `schema_version`. A source/date shell without
ingredient, allergen, or certification label content is not enough to mark a
safety-critical item safe.

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

## Correction Event

```json
{
  "schema_version": "2026-05-26.mvp1",
  "privacy_class": "sensitive_correction_telemetry",
  "item": "Diced microwave chicken",
  "signal": "wrong_format",
  "note": "Prefer strips, fillets, or whole pieces.",
  "source": "user_explicit",
  "created_at": "2026-05-26"
}
```

Correction and draft-edit telemetry is local-only by default and must be
consent-gated before persistence.

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
  "read": "Same price tier, better form factor.",
  "product_identity": {
    "schema_version": "2026-05-26.mvp1",
    "name": "Tyson grilled strips",
    "canonical_name": "tyson grilled strips",
    "category": "protein",
    "confidence": "medium"
  },
  "product_evidence": [],
  "source_provenance": {
    "source": "substitution_candidate",
    "confidence": "medium"
  },
  "evidence_status": "missing_candidate_evidence",
  "dietary_status": "needs_review"
}
```

Substitution candidates are treated as separate products. When any active
dietary profile is safety-critical, a candidate without its own current product
evidence defaults to `needs_review`; it cannot inherit `safe` from the current
item.

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
    "cart_plan": true,
    "order_submit": false
  }
}
```

`cart_plan` means internal guidance only. `external_cart_draft`, retailer cart
mutation, and `order_submit: true` are outside MVP and require a later ADR.
