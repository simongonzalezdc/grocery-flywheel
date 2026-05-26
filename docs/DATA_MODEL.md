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
  "acquisition_channel": "digital_history",
  "order": {
    "store": "Example Grocery",
    "date": "2026-05-20",
    "total": 112.19
  },
  "items": [],
  "pulses": [],
  "preferences": [],
  "substitutions": [],
  "sourcing_research": []
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
