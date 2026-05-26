# Data Model

The prototype uses a JSON state file. It is intentionally plain so imports can be written later for Vons, Instacart, CSV, email receipts, or manual notes.

## Top-Level Shape

```json
{
  "as_of": "2026-05-24",
  "order": {
    "store": "Example Grocery",
    "date": "2026-05-20",
    "total": 112.19
  },
  "items": [],
  "pulses": [],
  "preferences": [],
  "substitutions": []
}
```

## Item

```json
{
  "name": "Example burritos",
  "role": "bridge_food",
  "storage": "frozen",
  "spend": 6.42,
  "units_total": 8,
  "units_remaining": 0,
  "remaining_fraction": null,
  "notes": "Immediate food."
}
```

Use `units_total` and `units_remaining` when countable. Use `remaining_fraction` when the user reports a rough fullness signal such as `2/3 full`.

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

