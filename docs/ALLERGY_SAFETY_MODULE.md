# Allergy Safety Module

The allergy module is a high-value adjacent product module. It should be treated as safety-sensitive.

## Product Goal

Help users avoid adding products that conflict with their allergy profile by scanning product labels, ingredient lists, allergen statements, and cart items.

## Default Scope

MVP scope:

- User-defined allergy profile.
- Flag products containing known allergens.
- Flag missing or uncertain allergen data.
- Explain the evidence: label, ingredient, allergen statement, source, date checked.
- Let the user mark an item as safe/unsafe for their own household.

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
- Show "contains", "may contain", "processed in facility", and "unknown" separately.
- If label data is missing, say unknown. Do not infer safety.
- Let users set household profiles for multiple people.
- Make allergy risk a correction chip.
- Require explicit user review before accepting a risky substitution.

## Safety Rule

When allergy data is missing or ambiguous, the product must default to "needs review", not "safe."

## Sources

- FDA Food Allergies: https://www.fda.gov/food/food-labeling-nutrition/food-allergies
- FDA Food Allergies: What You Need to Know: https://www.fda.gov/food/buy-store-serve-safe-food/food-allergies-what-you-need-know

