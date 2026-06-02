# Product Design Research - May 2026

This research memo translates current product, ecommerce, accessibility, AI UX, and service-design guidance into requirements for Grocery Flywheel.

## Sources Checked

- Apple Human Interface Guidelines: Onboarding, Entering Data, Loading, Generative AI, and Human Interface Guidelines. https://developer.apple.com/design/human-interface-guidelines/
- Google Material 3 Expressive research, published May 2025. https://design.google/library/expressive-material-design-google-research
- Microsoft HAX Toolkit guidelines for human-AI interaction. https://www.microsoft.com/en-us/haxtoolkit/ai-guidelines/
- Baymard ecommerce and online grocery UX research on unit pricing and substitutions. https://baymard.com/blog/price-per-unit and https://baymard.com/blog/grocery-substitutions
- W3C WCAG 2.2. https://www.w3.org/TR/WCAG22/
- GOV.UK Service Manual guidance on simple services and user needs. https://www.gov.uk/service-manual/service-standard/point-4-make-the-service-simple-to-use
- AP reporting on grocery price variability and Instacart price-testing scrutiny. https://apnews.com/article/instacart-pricing-customers-retailers-c9a0a52e959ce46d2152aa664308d228

## Product Surface Recommendation

The product should not be "a dashboard" or "a chatbot" alone.

Recommended surface:

1. **Start Page**: one human-readable page that says what this does, what it needs, and what the user gets in 2 minutes.
2. **Guided Setup**: retailer history import first, fallback paths second. No perfect data required.
3. **First Wow**: estimated savings and sourcing alternatives.
4. **Command Center**: the beautiful dashboard, optimized for scanability and action.
5. **Assistant Loop**: recurring depletion pulses and correction capture.
6. **Restock Draft**: an explainable next-cart or next-run plan.
7. **Sourcing Research Stage**: optional cross-store/online alternatives for selected items.

This gives the user immediate value while preserving automation. The dashboard is the proof surface; the assistant loop is the habit; the restock draft is the action.

## Design Implications

### 1. First Use Must Produce A Result Immediately

Apple's onboarding guidance says onboarding should be fast, optional, and interactive. For this product, the first-run experience should strongly prefer retailer purchase history because it produces the best immediate baseline.

Ranked setup paths:

1. Import retailer order history.
2. Browser-assisted retailer import.
3. Email receipt/order confirmation import.
4. Paper receipt scan.
5. 10-item shelf/pantry/cabinet walkthrough.

The user should see a first dashboard even with rough data. Confidence labels can be low, but the product should not wait for perfect input.

### 2. Do Not Make People Enter Data The System Can Infer

Apple's data-entry guidance says to minimize manual input and use available system information when possible. Grocery Flywheel should infer categories, item roles, likely units, and storage from item names, then ask only for corrections.

Bad: "Fill out this schema."

Good: "I found 18 items. These 4 look like household essentials. Is that right?"

Better: "I found 8 months of your purchases. These are your recurring household essentials, pantry staples, and bridge foods. What is still in the house?"

### 3. Human-Readable Beats Technically Complete

GOV.UK service design guidance says services should help users succeed first time with minimal help. For this product, every recommendation needs:

- plain-English reason
- unit price if relevant
- what changed from last time
- action to take
- confidence level
- why it is safe to ignore

### 4. Beauty Is A Usability Feature Here

Google's Material 3 Expressive research found that expressive design can improve both preference and usability when it highlights key actions, groups related elements, and preserves familiar patterns.

For Grocery Flywheel, beauty should mean:

- warm, legible, high-trust visual language
- key action cards that are easy to spot
- readable tables for comparison
- restrained color used for meaning
- motion only where it clarifies state changes
- no decorative clutter that makes the user work harder

### 5. Accessibility Is A Product Requirement, Not Polish

Use WCAG 2.2 as the floor. The product must support:

- keyboard navigation
- visible focus states
- sufficient contrast
- readable text alternatives
- no action hidden behind drag-only gestures
- mobile touch targets that are easy to hit

### 6. AI Must Stay Explainable And Undoable

Apple's generative AI guidance and Microsoft HAX both emphasize user control, feedback, and failure handling. Grocery Flywheel should:

- label AI-generated analysis
- show evidence for recommendations
- let users reject, correct, retry, or ignore suggestions
- preserve corrections as durable preference signals
- never mutate carts or submit purchases without explicit approval

### 7. Unit Economics Must Be First-Class

Baymard research shows unit price matters for grocery and bulk purchase comparison. The product must normalize:

- price per ounce
- price per pound
- price per count
- price per serving
- price per use
- price per usable protein/meal when available

It should also explain when unit price loses to friction, preference, storage, or quality.

### 8. Substitutions Need Global Defaults And Per-Item Overrides

Baymard's grocery-substitution research shows users get frustrated when global substitution choices are hidden or appear too late. Grocery Flywheel should expose substitution policy early:

- "No substitutions unless approved."
- "Only same brand and format."
- "Cheapest equivalent quality."
- "Prefer larger package if storage is OK."
- "Never repeat disliked formats."

### 9. Sourcing Research Is Its Own Stage

Some items should leave the grocery-store default:

- coffee may be cheaper in bulk online or at Target/Walmart/warehouse stores
- cleaning supplies may be cheaper at warehouse stores or online
- spices may be cheaper at ethnic markets
- pet supplies may be better online
- restaurant/operator inventory may belong at restaurant supply stores

This stage should not overwhelm every cart. It should trigger only for high-spend, recurring, bulk-friendly, or suspiciously overpriced items.

### 10. Trust Requires Price Provenance

Reporting on Instacart price testing and grocery price variability makes price provenance part of product trust. Every sourced alternative should show:

- source
- date checked
- pickup, delivery, shipping, membership, or minimum-order constraints
- whether the price is personalized, scraped, user-entered, or from a receipt
- confidence level

## UX Metrics

Track whether the product is working:

- time to first useful dashboard
- number of questions required before first result
- percent of recommendations accepted
- percent of corrections remembered correctly
- restock plan creation time
- stockout count for critical essentials
- user-reported decision fatigue before and after
- repeat use after second grocery/restock run

## Product Principle

The product should feel like a calm, competent household operator:

It notices the boring things, explains the money, remembers what failed, and turns the next restock into a short approval step.
