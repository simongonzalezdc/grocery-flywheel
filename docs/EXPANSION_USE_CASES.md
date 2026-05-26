# Expansion Use Cases

Grocery Flywheel starts with personal groceries, but the mechanics point to a larger replenishment product.

## Personal Grocery

Core use case. Optimizes grocery-store replenishment around decision fatigue, real eating and household usage patterns, budget, pantry/cabinet runway, and preference corrections.

This includes food and non-food household consumables: cleaning supplies, paper goods, toiletries, pet supplies, basic pharmacy, batteries, and other recurring items sold through grocery-style channels.

## Restaurant Or Cafe Restocking

Inventory surface: walk-in, dry storage, prep station, disposables, beverages, cleaning supplies.

Useful mechanics:

- shift or service-period runway
- prep depletion pulses
- supplier substitution
- par levels
- emergency bridge inventory
- approval-first orders

Risks:

- multi-person updates need auditability
- food safety and compliance are out of MVP scope
- unit economics may need yield, waste, and menu mapping

## Office Kitchen Or Team Pantry

Inventory surface: coffee, snacks, drinks, paper goods, cleaning supplies.

Useful mechanics:

- low-friction reorder thresholds
- preference signals from repeated depletion
- multi-store price comparison
- budget-aware replenishment

## Studio, Lab, Or Maker Space

Inventory surface: consumables, materials, batteries, cables, filament, packaging, tools.

Useful mechanics:

- project-based runway
- substitutions by compatibility
- minimum viable stock
- reorder lead time

## Household Essentials

Inventory surface: toiletries, cleaning supplies, pet supplies, medicine-cabinet basics, laundry.

Useful mechanics:

- recurring depletion pulses
- emergency buffer
- household member preferences
- bulk versus storage tradeoff

## Event Or Production Inventory

Inventory surface: food, drinks, supplies, merch, equipment, transport materials.

Useful mechanics:

- event-date runway
- role-based checklists
- substitution planning
- post-event depletion review

## Product Implication

The product should not hardcode grocery assumptions into the core model. The core should speak in inventory surfaces, roles, runway, depletion pulses, substitutions, acquisition channels, and approvals. Grocery-specific labels should be a module layer.
