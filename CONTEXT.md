# Context

Grocery Flywheel is a local-first grocery-store and household replenishment system and the first module of a broader replenishment flywheel. It turns purchase history, small usage check-ins, and user preference corrections into lower-friction future carts.

## Domain Terms

### Grocery Run

A completed grocery-store, household, or restocking shopping event. A run has a date, store, total cost, and item list.

### Cart Draft

A proposed next order that is still waiting for user approval. A cart draft can be optimized, but it must not be submitted automatically.

### Pantry Base

Longer-lived staples that make many meals possible: rice, dry beans, lentils, pasta, tofu, frozen vegetables, sauces, spices, and coffee.

### Bridge Food

Immediate or near-immediate food that prevents executive-function collapse: burritos, waffles, pizza, microwave chicken, cereal, ready drinks. Bridge foods can be rational even when unit economics are weaker.

### Household Consumable

A recurring non-food household item sold through grocery-style restocking channels: cleaning supplies, detergent, trash bags, toilet paper, paper towels, toiletries, pet supplies, basic pharmacy, batteries, and similar essentials.

### Critical Household Essential

A household consumable whose stockout creates disproportionate disruption, such as toilet paper, dish soap, laundry detergent, trash bags, medication basics, or pet food.

### Runway

The estimated number of days before the current grocery or household setup stops covering the user's real usage pattern.

### Depletion Pulse

A small user report about what has been eaten, opened, used, or depleted. A pulse should be cheap to give: "2 burritos left", "opened tofu", "coffee brick sealed", "dish soap half full".

### Preference Signal

Evidence that an item is or is not actually usable for the user. Preference signals override naive price math when they change the probability of consumption or use.

### Friction Budget

The available cooking, cleanup, planning, storage, shopping, and decision energy required to transform inventory into useful outcomes.

### Unit Economics

Price per useful unit: per ounce, per pound, per serving, or per gram of protein. Unit economics must be interpreted with friction and preference, not alone.

### Same-SKU Inflation

Price change for the same product over time. This is different from switching package size, brand, or format.

### Format Swap

A change in package size, form factor, or preparation level, such as 5 lb rice to 20 lb rice or diced chicken to grilled strips.

### Approval-First Automation

The system can analyze, recommend, and prepare drafts, but purchase submission and external account mutation require explicit user approval.

### Replenishment Flywheel

The reusable pattern behind groceries: track what exists, observe what gets used, identify what unlocks future use, recommend the next restock, and preserve corrections.

### Inventory Surface

Any context where stocked items are consumed or used and need replenishment: home groceries, household essentials, restaurant pantry, office kitchen, maker lab, event supplies, or operator consumables.

### Acquisition Channel

How inventory enters the system: retailer purchase history, receipt import, manual entry, barcode scan, photo capture, or in-person onboarding.

### Retailer History Import

The preferred first-run acquisition channel. The user connects or exports purchase history from a retailer account so the product can build a useful baseline from repeated real purchases instead of relying on one receipt or manual entry.

### Retailer Adapter

A reusable connector profile that maps a retailer's store-specific account, history, search, price, substitution, and cart behavior into Grocery Flywheel's canonical model.

### Adapter Capability

A specific ability exposed by a retailer adapter, such as purchase history import, product search, price lookup, unit-price normalization, availability, substitutions, or cart draft.

### Onboarding Run

The first setup flow for a user with little or no structured history. It creates a starter inventory, captures constraints, and schedules early depletion pulses.

### Operator Use Case

A multi-person or business restocking workflow, such as restaurant mise en place, cafe supplies, office snacks, cleaning supplies, or studio consumables. Operator use cases need stronger auditability and role boundaries than personal groceries.

### Meta Pattern

A reusable product mechanic extracted from the grocery module, such as runway, depletion pulses, preference signals, substitution graphs, friction budgets, and approval-first actions.

### Sourcing Research

A stage that evaluates whether selected items should be bought from a different source than the default grocery run, such as online, warehouse, specialty, restaurant supply, ethnic market, or office supplier.

## Current Product Language

Use "runway", "depletion pulse", "bridge food", "pantry base", "household consumable", "critical household essential", "preference signal", "friction budget", "acquisition channel", "retailer history import", "retailer adapter", "adapter capability", "sourcing research", and "replenishment flywheel" consistently. Avoid reducing the product to a generic grocery list app or a food-only planner.
