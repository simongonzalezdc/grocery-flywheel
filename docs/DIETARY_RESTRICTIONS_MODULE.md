# Dietary Restrictions Module

The dietary restrictions module is a high-value optimization path. Allergies are the safety-critical subset, not the whole category.

## Product Goal

Help users avoid adding products that conflict with household dietary profiles by scanning product labels, ingredient lists, allergen statements, nutrition facts, certifications, and cart items.

## Restriction Types

Preset paths can include:

- food allergy
- intolerance or sensitivity
- gluten-free / celiac
- lactose-free / dairy-free
- vegetarian
- vegan
- kosher
- halal
- low sodium
- low sugar
- low FODMAP
- diabetic-friendly
- renal-friendly
- heart-healthy
- pregnancy restrictions
- medication interaction watchlist
- user-defined avoid list

## Safety Tiers

### Tier 1: Safety-Critical

Examples: food allergies, celiac/gluten cross-contact, severe medical restrictions, medication interactions.

Rules:

- Missing or ambiguous data means `needs review`, not safe.
- Require explicit user review before accepting a risky substitution.
- Show evidence and source date.
- Do not make medical guarantees.

### Tier 2: Strong Preference Or Lifestyle Rule

Examples: vegan, vegetarian, kosher, halal, dairy-free by preference.

Rules:

- Flag conflicts and uncertain products.
- Let users override.
- Preserve corrections.

### Tier 3: Optimization Goal

Examples: lower sugar, lower sodium, higher protein, fewer ultra-processed foods.

Rules:

- Rank and explain; do not block by default.
- Keep health language careful and non-prescriptive.

## MVP Scope

- Household dietary profile.
- Preset restriction paths.
- User-defined avoid list.
- Product/cart warnings.
- Evidence display: label, ingredient, allergen statement, nutrition fact, certification, source, date checked.
- Correction chips: safe for me, unsafe for me, needs review, false positive, never substitute.

Out of scope:

- Medical diagnosis.
- Guaranteeing a product is safe.
- Replacing label reading.
- Replacing clinician advice.

## U.S. Major Allergen Baseline

FDA-recognized major food allergens:

- milk
- eggs
- fish
- Crustacean shellfish
- tree nuts
- peanuts
- wheat
- soybeans
- sesame

The FDA notes that allergen labeling requirements apply to FDA-regulated foods and that sesame became the ninth major allergen effective January 1, 2023.

## UX Requirements

- Use clear warnings, not scary vague alerts.
- Separate `contains`, `may contain`, `processed in facility`, `conflicts with preference`, and `unknown`.
- If safety-critical data is missing, say unknown. Do not infer safety.
- Let users set profiles for multiple household members.
- Make dietary conflict and allergy risk correction chips.
- Require explicit user review before accepting a risky substitution.

## Safety Rule

When safety-critical dietary data is missing or ambiguous, the product must default to `needs review`, not `safe`.

## Sources

- FDA Food Allergies: https://www.fda.gov/food/food-labeling-nutrition/food-allergies
- FDA Food Allergies: What You Need to Know: https://www.fda.gov/food/buy-store-serve-safe-food/food-allergies-what-you-need-know

