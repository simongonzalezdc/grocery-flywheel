# Vons Final Order Analysis - 2026-05-20

Status: Order placed by user.
Store: Pickup at 600 E Broadway.
Pickup window: Wednesday, May 20, 1 PM - 2 PM.
Order number: 172751073.

## Final Order Facts

| Metric | Value |
| --- | ---: |
| Unique SKUs | 19 |
| Total units | 22 |
| Original item subtotal | $135.88 |
| Estimated savings | $23.99 |
| Estimated subtotal after savings | $111.89 |
| Estimated taxes and fees | $0.30 |
| Estimated total | $112.19 |
| Savings rate | 17.7% |
| Average cost per unit | $5.09 |
| Average cost per SKU | $5.89 |

## Final Items

| Item | Qty | Est. Price |
| --- | ---: | ---: |
| Cafe Bustelo Espresso Style Dark Roast Ground Coffee Vacuum-Packed - 10 oz | 2 | $13.84 |
| Florida's Natural Ruby Red Grapefruit Juice 100% Chilled - 52 fl oz | 1 | $3.47 |
| Kashi Go Cereal Peanut Butter - 16.9 oz | 1 | $3.46 |
| Signature SELECT Dark Brown Sugar - 32 oz | 1 | $2.97 |
| Fairlife Ultra-Filtered Reduced Fat Chocolate 2% - 52 fl oz | 1 | $6.49 |
| Lucerne Sharp Cheddar - 32 oz | 1 | $7.91 |
| El Monterey Bean & Cheese Frozen Burritos 8 count - 32 oz | 1 | $6.42 |
| Signature SELECT California Style Vegetables - 32 oz | 1 | $4.94 |
| Signature SELECT Homestyle Waffles - 29.6 oz | 1 | $5.43 |
| Signature SELECT Rising Crust Supreme Pizza - 33.5 oz | 1 | $4.94 |
| Azumaya Extra Firm Tofu - 14 oz | 3 | $5.91 |
| Botan Calrose Rice - 20 lb | 1 | $19.80 |
| Signature SELECT Garbanzo Beans - 16 oz | 1 | $1.98 |
| Signature SELECT Pinto Beans - 32 oz | 1 | $2.97 |
| Signature SELECT Lentils - 32 oz | 1 | $2.97 |
| Signature SELECT Rigatoni - 16 oz | 1 | $1.48 |
| Signature SELECT Tomato Basil Pasta Sauce - 25 oz | 1 | $2.27 |
| Signature SELECT Pesto Sauce - 8.3 oz | 1 | $4.75 |
| Tyson Grilled & Ready Diced Oven Roasted Chicken Breast - 22 oz | 1 | $9.89 |

## Storage Mix

| Storage Type | SKUs | Units | Spend | Share |
| --- | ---: | ---: | ---: | ---: |
| Shelf-stable | 10 | 11 | $56.49 | 50.5% |
| Frozen | 5 | 5 | $31.62 | 28.3% |
| Refrigerated | 4 | 6 | $23.78 | 21.3% |

## Ticket Size vs Price Inflation

The right inflation metric is same-item price over time, not "what took the most dollars in this basket." Rice is the clearest example: the order moved from a 5 lb bag to a 20 lb bag, so the ticket line got bigger while the unit cost improved.

| Comparison | Type | Earlier Point | Current Point | Unit Change | Read |
| --- | --- | --- | --- | ---: | --- |
| Cafe Bustelo 10 oz | Exact SKU | May 8: $6.90 / 10 oz | May 20: $6.92 / 10 oz | +0.3% | No meaningful Vons price jump across these two orders. |
| Fairlife Chocolate 52 fl oz | Exact SKU | May 8: $6.49 / 52 fl oz | May 20: $6.49 / 52 fl oz | 0.0% | Flat in the visible order history. |
| Rice per lb | Package + brand change | May 8: Signature SELECT 5 lb, $6.90 / $1.38 per lb | May 20: Botan 20 lb, $19.80 / $0.99 per lb | -28.3% | Higher basket spend because the bag is 4x larger, but lower unit cost. |
| Frozen vegetables per oz | Brand swap | May 8: O Organics 32 oz, $5.42 / $0.169 per oz | May 20: Signature SELECT 32 oz, $4.94 / $0.154 per oz | -8.9% | Same role, cheaper store-brand unit economics. |
| Chicken per oz | Brand swap | May 8: Just Bare 24 oz, $13.80 / $0.575 per oz | May 20: Tyson diced chicken 22 oz, $9.89 / $0.450 per oz | -21.8% | Microwave-fast protein role kept, unit cost reduced. |
| Waffles per oz | Format swap | May 8: Kodiak 10.72 oz, $5.92 / $0.552 per oz | May 20: Signature SELECT 29.6 oz, $5.43 / $0.183 per oz | -66.8% | Trades protein branding for cheap immediate-food volume. |
| Frozen immediate meal per oz | Role swap | May 8: El Monterey taquitos 20 oz, $6.89 / $0.345 per oz | May 20: El Monterey burritos 32 oz, $6.42 / $0.201 per oz | -41.8% | Same no-thought role, better cost per ounce. |

## Derived Meal Architecture

The order has three layers:

1. Immediate food: burritos, waffles, cereal, pizza, Fairlife, grapefruit juice, Tyson chicken.
2. Low-effort batch food: rice, dry lentils, pinto beans, garbanzos, pasta, sauce, pesto, tofu, frozen vegetables, cheddar.
3. Long-run pantry: 20 lb rice, 5 lb total dry legumes, Bustelo, brown sugar.

## Duration Forecast

Assumption: one adult, using this order as the main food base and not counting large amounts of food already at home.

| Consumption Pattern | Expected Duration | Why |
| --- | ---: | --- |
| Mostly no-cook / microwave | 10-14 days | Immediate foods are finite: 8 burritos, one pizza, waffles, cereal, Fairlife, Tyson chicken. |
| Mixed immediate + batch cooking | 17-24 days | Rice, beans, lentils, tofu, pasta, cheese, and vegetables stretch the order into real meals. |
| With small top-ups | 25-35 days | Add eggs, fruit, greens, salsa/hot sauce, or another protein and the pantry base carries longer. |
| Pantry base only | 45-90 days | Rice, dry legumes, coffee, sugar, and some sauces remain after the bridge foods are gone. |

Estimated total cost per day:

| Days Covered | Cost / Day |
| ---: | ---: |
| 14 | $8.01 |
| 21 | $5.34 |
| 28 | $4.01 |
| 35 | $3.21 |

## Practical Read

The realistic answer is: this run should cover about 2.5 to 3.5 weeks of eating if the rice and legumes actually get cooked. If it is used mostly as immediate food, it is closer to 10-14 days. The smarter larger items do not make the whole order last 2-3 months; they make the staple base last that long while reducing how much the next grocery order needs to buy.

## Coffee Correction

The prior Vons purchase history undercounts coffee demand because the user was drawing from an older bulk stockpile rather than buying coffee through regular Vons orders. Coffee should be modeled as a recurring staple, not as a new indulgence.

Two Cafe Bustelo 10 oz bricks equal 20 oz / roughly 567 g of ground coffee. Approximate moka-pot runway:

| Daily Coffee Dose | Estimated Days From 2 Bricks |
| ---: | ---: |
| 30 g/day | 19 days |
| 25 g/day | 23 days |
| 20 g/day | 28 days |
| 15 g/day | 38 days |

Coffee conclusion: buying two bricks does raise the order subtotal, but it should also cover a longer interval. The right metric is cost per coffee-day, not whether coffee appears in one grocery run. If one brick previously lasted around a month, two bricks should plausibly cover about two months. If actual moka-pot dose is larger, use the table above.

Current non-Vons options checked:

| Source | Visible Price | Read |
| --- | ---: | --- |
| Vons final order | $6.92 per 10 oz brick / $0.69 per oz | Baseline convenience price. |
| Target | $6.99 per 10 oz brick, with visible buy-one-get-one-25%-off deal on select Cafe Bustelo coffee | Best practical two-brick replenishment if the deal is live: about $6.12 per brick before any card discount. |
| Walmart | $6.62 per 10 oz brick / $0.66 per oz | Slightly better than Vons for singles. |
| Walmart 12-pack | $71.47 for 12 x 10 oz / $0.596 per oz | Best confirmed bulk option found, but only if storing 12 bricks is acceptable. |
| Ralphs | $7.99 per 10 oz / $0.80 per oz | Not better than Vons unless couponed. |
| Smart & Final | $7.99-$9.49 per 10 oz listings | Not better than Vons in visible listings. |

Coffee buying rule: do not automatically buy Bustelo at Vons. Replenish at Vons only if convenient or if price is under about $6.50 per brick. Prefer Target deal cycles or Walmart bulk when the effective price is around $6.10 per brick or lower. Set a personal restock floor of 2 bricks and a normal target of 4-6 bricks, not the old giant stockpile.

## Previous Vons Online Order Cadence

Source: Vons `Purchase history` online tab, visible last-90-days orders.

| Date | Items | Total |
| --- | ---: | ---: |
| 2026-02-03 | 19 | $107.48 |
| 2026-02-17 | 15 | $90.55 |
| 2026-02-26 | 19 | $111.43 |
| 2026-03-16 | 16 | $138.76 |
| 2026-03-25 | 15 | $94.20 |
| 2026-04-14 | 16 | $93.12 |
| 2026-04-20 | 16 | $114.09 |
| 2026-05-08 | 12 | $99.54 |
| 2026-05-20 | 22 | $112.19 |

Intervals before this order: 14, 9, 18, 9, 20, 6, 18, and 12 days.

| Baseline Metric | Value |
| --- | ---: |
| Average grocery interval | 13.25 days |
| Median grocery interval | 13 days |
| Previous average order size | 16 units |
| Previous average order total | $106.15 |
| Previous average cost per unit | $6.63 |
| Previous estimated Vons grocery burn | $8.01/day |

The in-store purchase tab showed older 2025 purchases, not recent 2026 gap-filling trips, so the current cadence baseline should come from online pickup orders.

## Cadence Comparison

This order increased quantity much more than spend:

| Comparison | Value |
| --- | ---: |
| Units vs previous average | +37.5% |
| Spend vs previous average | +5.7% |
| Cost per unit reduction | -23.1% |
| Break-even duration vs old burn rate | 14.0 days |

Meaning: if this order lasts more than 14 days, it beats the previous grocery pattern. If it lasts 21-24 days, it is a major improvement.

| If This Order Lasts | Cost / Day | Monthly Vons Pace |
| ---: | ---: | ---: |
| Old baseline | $8.01 | ~$244/month |
| 17 days | $6.60 | ~$201/month |
| 21 days | $5.34 | ~$163/month |
| 24 days | $4.67 | ~$142/month |

## Calendar Forecast

Current order date: 2026-05-20.

| Scenario | Next Major Grocery Need |
| --- | --- |
| Old pattern continues | Around 2026-06-02 |
| Conservative smarter-run outcome | Around 2026-06-06 |
| Good smarter-run outcome | Around 2026-06-10 |
| Strong smarter-run outcome | Around 2026-06-13 |

Target: make the next full grocery order no earlier than 2026-06-06. A small fresh-food top-up before then is fine; it should not turn into another full order.

Next high-ROI top-ups when the bridge layer starts to run out:

- Eggs or another easy protein.
- Fruit plus one crisp vegetable.
- Salsa, hot sauce, or seasoning that makes rice/beans/tofu feel different.
- Another frozen vegetable bag.
- One more no-thought meal module if burritos/pizza run out first.
