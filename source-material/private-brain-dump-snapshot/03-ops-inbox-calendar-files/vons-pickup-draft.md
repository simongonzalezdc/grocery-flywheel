# Vons Pickup Draft Cart

Updated: 2026-05-20
Store: Pickup at 600 E Broadway
Status: Order placed by user. Estimated total $112.19. Pickup Wednesday, May 20, 1 PM - 2 PM.
Earlier cart optimization snapshot: 18 items, estimated subtotal $89.03 after savings / $106.02 before savings.
Latest live Vons cart check after Bustelo correction: 16 items, estimated subtotal $82.54 after savings / $101.54 before savings.
Latest live Vons cart check after required additions: 23 items, estimated subtotal $113.08 after savings / $135.07 before savings.
Latest live Vons cart check after protein and dried-legume swaps: 23 items, estimated subtotal $114.88 after savings / $138.87 before savings.
Final placed order confirmation: 22 units across 19 unique SKUs, estimated subtotal $111.89 after savings / $135.88 before savings, estimated total $112.19 including $0.30 bag fee.

## Current Live-State Note

The live Vons cart later showed 14 items before the coffee add, not the earlier 18-item snapshot recorded in this note. After the coffee correction, the live cart showed 16 items: 14 food items plus 2 Cafe Bustelo vacuum-pack bricks. Treat the earlier 18-item table below as the prior optimization plan, and use the latest cart check plus `vons-moka-coffee-analysis.md` for the current coffee decision.

After the required-additions pass, the live cart showed 23 items and $113.08 after savings. Top verified additions/current requirements: Chocolate Fairlife was in cart at quantity 1, Florida's Natural Ruby Red Grapefruit Juice was in cart at quantity 1, and Just Bare Original Fully Cooked Chicken Breast Fillets was in cart at quantity 1.

The later protein and dried-legume pass executed the requested replacements. Just Bare was removed. The current meat-protein slot is Tyson Grilled & Ready Diced Oven Roasted Chicken Breast, quantity 1. Later correction: do not repeat diced chicken by default; the next microwave-chicken slot should use Tyson grilled strips, fillets, or another whole-piece fully cooked option. The canned pinto and canned kidney beans were removed. The dry-legume lane in the final placed order is Signature SELECT Garbanzo Beans 16 oz quantity 1, Signature SELECT Pinto Beans 32 oz quantity 1, and Signature SELECT Lentils 32 oz quantity 1.

Follow-up protein analysis found that Just Bare is not the best ROI meat-protein slot. Best low-friction replacement is Tyson frozen grilled chicken strips at $9.99 / 22 oz (~$7.27/lb), versus Just Bare at roughly $9.23-$9.33/lb. The Tyson diced option had the same saved shelf unit math as the strips but failed the user's form-factor preference. Cheapest microwave option is Foster Farms Classic Chicken Patties at $6.99 / 28 oz (~$3.99/lb), with the tradeoff that patties are more processed and less lean. See `vons-meat-protein-alternatives-2026-05-20.md`.

Follow-up bean correction: the user can soak dried beans overnight, so dried beans should replace canned beans as the main bean lane. Keep cans only as emergency/no-soak bridge food. One 1 lb dry bag is roughly four can-equivalents after cooking, so even a $2.99 dry bag beats $1.29 canned beans on cooked yield. User also explicitly said they love garbanzo beans, so garbanzos should be treated as a preferred staple, not a novelty. See `vons-dried-beans-analysis-2026-05-20.md`.

## Final Placed Order Snapshot

Verified live on Vons order confirmation: Order 172751073, pickup Wednesday, May 20, 1 PM - 2 PM. Items (22), $112.19 estimated total. User placed the order.

| Slot | Final Order Result |
| --- | --- |
| Meat protein | Tyson Grilled & Ready Diced Oven Roasted Chicken Breast - 22 oz, quantity 1, $9.89. |
| Dry legumes | Signature SELECT Beans Garbanzo - 16 oz, quantity 1; Signature SELECT Beans Pinto - 32 oz, quantity 1; Signature SELECT Lentils - 32 oz, quantity 1. |
| Required drink | Fairlife Chocolate 2% - 52 fl oz, quantity 1, $6.49. |
| Interesting drink | Florida's Natural Ruby Red Grapefruit Juice - 52 fl oz, quantity 1, $3.47. |
| Coffee | Cafe Bustelo Espresso Style Dark Roast Ground Coffee Vacuum-Packed - 10 oz, quantity 2, $13.84. |
| Final order difference from last draft cart | Lentils placed at quantity 1 rather than the earlier draft-cart quantity 2. |

## Latest Verified Draft Cart Snapshot

Verified live in Vons cart after edits: Cart (23), $114.88 after savings / $138.87 before savings. No checkout submitted.

| Slot | Verified Current Cart Result |
| --- | --- |
| Meat protein | Tyson Grilled & Ready Diced Oven Roasted Chicken Breast - 22 oz, quantity 1, $9.89 after savings. |
| Removed meat protein | Just Bare Original Fully Cooked Chicken Breast Fillets is no longer in cart. |
| Dry legumes | Signature SELECT Beans Garbanzo - 16 oz, quantity 1; Signature SELECT Beans Pinto - 32 oz, quantity 1; Signature SELECT Lentils - 32 oz, quantity 2. |
| Removed canned beans | Signature SELECT canned pinto and canned dark red kidney beans are no longer in cart. |
| Required drink | Fairlife Chocolate 2% - 52 fl oz, quantity 1. |
| Interesting drink | Florida's Natural Ruby Red Grapefruit Juice - 52 fl oz, quantity 1. |
| Coffee | Cafe Bustelo Espresso Style Dark Roast Ground Coffee Vacuum-Packed - 10 oz, quantity 2. |

## User Removal / Correction Signal

The user removed or rejected some earlier optimization choices. Inferred from the live cart compared with the prior 18-item snapshot, the items no longer present were:

- Lucerne Greek Yogurt Whole Milk Plain.
- Signature SELECT Peanut Butter Creamy 64 oz.
- SEEDS OF CHANGE ready-rice pouch.
- Kashi Go Chocolate Crunch.

Explicit correction from the user: remove the expensive Lavazza coffee idea and use 2 Bustelo bricks instead.

Lesson: the cart should not over-add "good idea" bridge foods. A bridge item only wins if the user actually wants that form factor and the price-per-function is good. For coffee specifically, Bustelo wins because it is familiar, moka-compatible, cheap, and provides almost twice the amount of coffee for roughly the same order cost as one Lavazza bag.

## Decision Rule

Prefer equivalent-quality items by unit price: price per pound, ounce, fluid ounce, or serving. Larger pantry sizes win when storage risk is low and the food is a stable staple.

For executive-function bridge foods, the decision rule has one extra factor: a slightly higher unit price can still win when the item prevents skipped meals, delivery, or standing in front of the kitchen unable to choose. Keep those items limited, visible, and repeatable.

## Added / Selected During Optimization

This table preserves the decision trail. The `Final Placed Order Snapshot` above is the source of truth for the order.

| Item | Price / Size | Unit Math | Why |
| --- | ---: | ---: | --- |
| Signature SELECT Beans Garbanzo Dry | $1.99 / 16 oz; $1.98 live after savings | Better cooked yield than canned | Added after user clarified garbanzo beans are a loved staple. |
| Signature SELECT Beans Pinto Dry | $2.99 / 32 oz; $2.97 live after savings | Better cooked yield than canned | Replaces canned pinto as the main bean lane. |
| Signature SELECT Lentils | 2 x $2.99 / 32 oz; $5.92 live after savings | Fast-cooking dry legume | Added at quantity 2 after user said to do a lot of lentils. |
| Signature SELECT Pasta Sauce Tomato Basil | $2.29 / 25 oz | ~$0.092/oz | Beats O Organics sauce even after coupon. |
| Signature SELECT Pesto Sauce | $4.79 / 8.3 oz | ~$0.58/oz | Better unit price than Barilla pesto. |
| Botan Calrose Rice | $19.99 / 20 lb | ~$1.00/lb | Better than 5 lb Calrose at $6.99 (~$1.40/lb); bulk pantry win. |
| Signature SELECT Pasta Rigatoni | $1.49 / 16 oz | ~$0.093/oz | Replaces Barilla rigatoni at $1.99. |
| Azumaya Extra Firm Tofu | $1.99 / 14 oz | ~$0.142/oz | Cheaper than O Organics tofu at $2.49; non-organic tradeoff. |
| Lucerne Sharp Cheddar | $7.90 cart price / 32 oz | ~$3.95/lb | Still better than small blocks, but the displayed $4.77 offer did not land in cart because it appears to require 5 total offer items. Review before approving pickup. |
| Signature SELECT Dark Brown Sugar | $2.99 / 32 oz | ~$1.50/lb | Better than 16 oz bag at $2.29 (~$2.29/lb). |
| Kashi Go Chocolate Crunch | $3.49 / 16 oz | ~$0.218/oz | Earlier exact buy-again item; not in the latest live cart after user removals. |
| Kashi Go Peanut Butter | $3.49 / 16.9 oz | ~$0.206/oz | Prior buy-again flavor; slightly better unit price than Chocolate Crunch. |
| Signature SELECT California Style Vegetables | $4.99 / 32 oz | ~$2.50/lb | Same family-pack frozen veg lane as O Organics at $5.49; non-organic tradeoff. |
| Signature SELECT Rising Crust Supreme Pizza | $4.99 / 33.5 oz | ~$0.15/oz | Real pizza pick: rated 4.7, biggest value among quality options, beats Screamin Sicilian, DiGiorno, Red Baron, and cauliflower pizzas by unit price. |
| El Monterey Bean & Cheese Frozen Burritos | $6.49 / 8 ct / 32 oz | ~$0.20/oz; ~$0.81 each | Direct taquito replacement: microwaveable, more filling per dollar, and less than half the unit price of $8.99 / 20 oz taquitos. |
| Signature SELECT Homestyle Waffles | $5.49 / 29.6 oz | ~$0.19/oz | Replaces premium/protein-waffle logic with a cheaper family-size no-thought breakfast base. |
| Lucerne Greek Yogurt Whole Milk Plain | $4.99 / 32 oz | ~$0.16/oz | Earlier protein/fat anchor idea; not in the latest live cart after user removals. |
| Signature SELECT Peanut Butter Creamy | $9.49 / 64 oz | ~$0.15/oz | Earlier shelf-stable anchor idea; not in the latest live cart after user removals. |
| SEEDS OF CHANGE Organic Rice Brown & Quinoa With Garlic | $2.50 / 8.5 oz | ~$0.29/oz | Earlier emergency ready-rice idea; not in the latest live cart after user removals. |
| Cafe Bustelo Espresso Style Dark Roast Ground Coffee Vacuum-Packed | 2 x $6.99 / 10 oz | ~$0.69-$0.70/oz | User-corrected moka-pot coffee choice: familiar, cheap, and about twice the coffee for roughly the cost of one Lavazza bag. |
| Fairlife Milk Ultra-Filtered Reduced Fat Chocolate 2% | $6.49 / 52 fl oz | ~$0.125/fl oz | User-required item. Verified already in cart at quantity 1. |
| Florida's Natural Ruby Red Grapefruit Juice 100% Chilled | $3.50 / 52 fl oz; $3.47 live after savings | ~$0.067/fl oz | Chosen as the one interesting non-water drink: real grapefruit juice, better value than Simply Grapefruit, Signature Select, Ocean Spray, or Squirt multipacks in this pass. |
| Tyson Grilled & Ready Diced Oven Roasted Chicken Breast | $9.99 / 22 oz; $9.89 live after savings | ~$7.27/lb shelf math | Replaced Just Bare as the single meat-protein slot while preserving fully cooked frozen convenience. Later correction: avoid diced next time; same-brand Tyson grilled strips had the same saved shelf unit price. |

## Just Bare / Frozen Chicken Alternatives

The remembered brand is `Just Bare`. The exact Buy Again match added was `Just Bare Original Fully Cooked Chicken Breast Fillets - 24 Oz`.

| Alternative | Price / Size | Unit Math | Use Case |
| --- | ---: | ---: | --- |
| Just Bare Fully Cooked Breaded Chicken Breast Bites | $13.99 / 24 oz | ~$0.58/oz | Best same-brand no-thought nugget/bowl option; rated 4.8 in live results. |
| Just Bare Fully Cooked Lightly Breaded Chicken Breast Strips | $13.99 / 24 oz | ~$0.58/oz | Same-brand strip option; easier for wraps, rice bowls, or pasta. |
| Just Bare Lightly Breaded Chicken Breast Bites, larger bag | $19.99 / 36 oz | ~$0.56/oz | Slightly better unit price, but only wins if the larger bag reliably gets eaten. |
| Tyson Frozen Grilled Chicken Breast Strips | $9.99 / 22 oz | ~$0.45/oz | Same saved unit price as Tyson diced, better form factor for the next lean microwave-chicken slot. |
| Tyson Frozen Crispy Chicken Breast Strips | $9.99 / 1.56 lb | ~$0.40/oz | Cheaper immediate-frozen strip alternative, lower perceived quality than Just Bare. |
| Signature Select/Farms Boneless Skinless Chicken Tenderloins | $9.99 / 40 oz | ~$0.25/oz | Best protein value, but requires cooking and does not solve the immediate-food problem. |
| Foster Farms Classic Crispy Chicken Strips | $8.99 / 24 oz | ~$0.37/oz | Cheap prepared option, but live rating was much weaker than Tyson/Just Bare. |

## Removed / Replaced

| Item | Cart Price | Why Removed |
| --- | ---: | --- |
| Open Nature Chicken Sausage & Pepper Cauliflower Crust Pizza | $6.47 after savings / 11.5 oz | The user clarified the need was real pizza and cost-effective immediate food. Signature SELECT Rising Crust Supreme is much larger, cheaper, and better aligned. |
| Lavazza Espresso Italiano Ground Coffee | $12.83 after savings / 10.5 oz | Removed after user correction: too expensive relative to Bustelo, with no clear enough quality/quantity ROI for this grocery run. |
| Just Bare Original Fully Cooked Chicken Breast Fillets | $13.99 / 24 oz; $13.85 previous live cart | Replaced by Tyson Grilled & Ready diced chicken for a lower-cost prepared chicken slot. Later preference signal says diced should be replaced by Tyson grilled strips or another whole-piece option next time. |
| Signature SELECT Beans Pinto canned | 2 x $1.29 / 15.5 oz | Replaced by dry pinto beans because soaking overnight is viable and dry beans win on cooked yield. |
| Signature SELECT Beans Kidney Dark Red canned | 2 x $1.29 / 15 oz | Removed during dry-bean correction; dry lentils and garbanzos are preferred current legumes. |

## No-Thought Food Stack

This cart should support three effort levels instead of pretending every meal happens with a functioning frontal lobe.

### Level 0: Eat Now

- Chocolate Fairlife as a required ready protein drink.
- Kashi cereal dry or with milk if available.
- Waffles when the toaster is available but cooking is not.

### Level 1: Microwave

- Bean & cheese burrito.
- Tyson grilled strips or whole-piece microwave chicken + rice, beans, frozen vegetables, or pasta.
- Pizza + frozen vegetables.

### Level 2: Low-Effort Batch

- Bulk rice + lentils, garbanzos, pinto beans, and cheddar.
- Pasta + tomato basil sauce + frozen vegetables.
- Rice + tofu + pesto or sauce.

## Neurodivergent Cart Rule

The cart needs both cheap staples and bridge foods. Staples lower cost over time; bridge foods protect against the moment where eating requires too many steps. The highest-ROI bridge foods are:

- Microwaveable and visible.
- No chopping.
- Three steps or fewer.
- Protein/fat/fiber included or easy to add.
- Familiar enough to eat on a low-sensory, low-decision day.

For future Vons passes, keep the bridge-food section to 4-6 defaults so the cart does not become another decision surface: one pizza, one burrito pack, one waffle/cereal breakfast lane, one yogurt or cottage-cheese tub, one peanut-butter/nut-butter anchor, and one emergency rice/chili/soup module.

## Approval Flags

- No checkout or purchase has been finalized.
- Latest live cart verification after protein and dried-legume swaps: Cart (23), $114.88 after savings / $138.87 before savings.
- The cart intentionally favors bigger staple sizes where the unit price is materially better.
- Non-organic substitutions are present for tofu and frozen vegetables.
- The earlier cauliflower pizza has been removed from the draft cart.
- The Lucerne cheddar coupon needs review: the product page showed a $4.77 coupon, but the live cart showed $7.90 and the offer text indicated `Add 5 Total for Offer`.
- User removals/corrections mean Greek yogurt, peanut butter, and ready-rice should not be re-added automatically without a fresh reason.
- No alcohol added.

## Research Anchors

- USDA MyPlate time-saving guidance supports keeping familiar freezer and pantry items on hand, buying bulk staples, and using frozen or ready-to-heat foods to reduce prep and cleanup: https://www.myplate.gov/eathealthy/budget/budget-weekly-meals
- CHADD frames ADHD meal planning around pantry/freezer staples, shopping from a list, and reducing last-minute dinner decisions: https://chadd.org/adhd-weekly/whats-for-dinner-tips-for-healthy-meal-planning/
- Today's Dietitian's 2026 neurodivergent meal-planning framework emphasizes flexible guidelines, minimum nourishment, and fat + fiber + protein + a satisfying "wow" factor rather than rigid perfection: https://www.todaysdietitian.com/flexible-meal-planning-for-autism-and-adhd/
