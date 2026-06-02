# Sourcing Research Stage

The sourcing research stage finds alternative places to buy selected items. It exists because the best restock source is not always the same store as the current grocery run.

## Goal

Find better sources for specific recurring or expensive items while avoiding decision overload.

## Trigger Conditions

Run sourcing research when an item is:

- recurring
- high spend
- bulk-friendly
- shelf-stable
- unusually expensive
- used across many meals/tasks
- frequently bought at a grocery store despite likely cheaper specialty sources
- an operator supply with supplier alternatives

Examples:

- coffee
- spices
- rice and beans
- cleaning supplies
- paper goods
- toiletries
- pet supplies
- restaurant disposables
- office coffee and snacks

## Candidate Source Types

- current grocery store
- competing grocery store
- warehouse club
- Target/Walmart-style general retailer
- online retailer
- restaurant supply store
- ethnic market
- farmers market
- local specialty shop
- subscription/bulk source

## Output

Each sourcing result should be human-readable:

```json
{
  "item": "Cafe Bustelo 10 oz brick",
  "current_source": "Vons",
  "current_unit_price": 0.692,
  "alternatives": [
    {
      "source": "Walmart bulk pack",
      "unit_price": 0.596,
      "savings": "14%",
      "constraints": ["bulk storage", "online availability"],
      "confidence": "medium",
      "recommendation": "Buy outside grocery store if storing 12 bricks is acceptable."
    }
  ]
}
```

## Ranking Rules

1. Normalize unit price first.
2. Include shipping, fees, memberships, pickup minimums, and delivery costs.
3. Prefer equivalent quality and format.
4. Penalize storage burden.
5. Penalize extra trip burden unless savings or reliability justify it.
6. Show confidence and date checked.
7. Never hide the current-store option.

## UX Rules

- Do not research every item by default.
- Show only the top 1-3 alternatives unless the user asks for more.
- Use "worth a separate source" / "not worth a separate source" labels.
- Explain the reason in one sentence.
- Preserve user corrections, such as disliked brand, scent, format, texture, package size, or store.

## Safety And Trust

Prices can be personalized, dynamic, member-only, out of date, or location-specific. The product must show provenance:

- source name
- checked date
- price basis
- whether login was used
- confidence
- known constraints

