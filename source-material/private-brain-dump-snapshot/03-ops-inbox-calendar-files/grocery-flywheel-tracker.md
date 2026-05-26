# Grocery Flywheel Tracker

Purpose: keep the Vons dashboard alive as new evidence arrives instead of treating each grocery order as a one-off analysis.

Status: active. A recurring Codex thread check-in now runs every 3 days to ask how the May 20, 2026 grocery run is lasting.

## Operating Rule

Update the grocery model when either of these happens:

1. New Vons data appears: a new order, purchase-history row, item-detail page, receipt, or cart snapshot.
2. New depletion data appears: the user reports what is gone, what is still untouched, what got eaten quickly, or what felt too hard to use.

Do not place purchases or modify carts from this tracker alone. Cart actions need an explicit user request.

## Source Files

| File | Role |
| --- | --- |
| `vons-order-analysis-dashboard-2026-05-20.html` | Visual dashboard and decision surface. |
| `vons-final-order-analysis-2026-05-20.md` | Final placed-order facts, cadence, and price-normalization analysis. |
| `vons-next-stop-spice-topup-2026-05-20.md` | Next-stop gap and spice capsule. |
| `vons-pickup-draft.md` | Cart decision history, user removals, and learned preferences. |

## Data To Capture Every New Vons Order

| Field | Why It Matters |
| --- | --- |
| Order date | Updates cadence and next-runway forecast. |
| Order number | Lets us reconnect to Vons item details later. |
| Item count / unit count | Shows whether basket efficiency is improving. |
| Estimated subtotal / total | Updates burn rate and monthly pace. |
| Full item list with size and price | Enables same-SKU inflation checks and unit-price comparisons. |
| Repeated SKUs | Measures real item inflation over time. |
| Substitutions | Separates price increases from smarter package/brand changes. |
| Items removed by user | Preference data; prevents future over-adding. |

## Data To Capture During Runway Check-Ins

Use this compact inventory pulse:

| Category | Ask |
| --- | --- |
| Bridge foods | How many burritos, waffles, pizza, cereal, Fairlife, and Tyson chicken portions are left? |
| Pantry staples | Has rice, lentils, pinto beans, garbanzos, pasta, or sauce actually been used? |
| Protein | Are tofu, chicken, cheese, Fairlife, and legumes being eaten or avoided? |
| Coffee | How many Bustelo bricks remain? |
| Flavor | Did lack of spices/sauce block rice, beans, lentils, tofu, or chicken? |
| Top-up need | Is the next need flavor, fresh food, protein, emergency food, or another full shop? |

## Metrics To Recompute

| Metric | Formula |
| --- | --- |
| Actual days lasted | Date of next full grocery order minus 2026-05-20. |
| Current burn rate | $112.19 divided by actual days lasted. |
| Baseline comparison | Compare actual days lasted against 13.25-day old average and 14-day break-even. |
| Bridge-food burn | Count how fast immediate foods disappear. |
| Pantry activation | Count which shelf-stable staples actually entered rotation. |
| Coffee run rate | Two bricks / days until gone. |
| Same-SKU price movement | Current same item price vs prior same item price, normalized by size. |
| Substitution ROI | New unit price vs old role-equivalent unit price. |

## Current Baseline

| Baseline | Value |
| --- | ---: |
| Order date | 2026-05-20 |
| Order total | $112.19 |
| Old online-order average gap | 13.25 days |
| Break-even target | More than 14 days |
| Good target | 21 days |
| Strong target | 24+ days |
| Next full-order target window | 2026-06-06 to 2026-06-13 |

## Depletion Log

### 2026-05-21 Pulse

Source: user report on 2026-05-21.

| Category | Reported State | Model Update |
| --- | --- | --- |
| Burritos | 2 eaten from 8-pack; 6 left. | 25% of burrito bridge lane consumed. Still fine, but this lane will disappear quickly if it becomes the default meal. |
| Waffles | 4 waffles eaten. | Immediate breakfast lane is active. Package count was not recorded, so exact remaining percentage is unknown. |
| Cheese | About 1/8 used. | 32 oz block implies about 4 oz used and 28 oz left. Cheese is being used at a real pace. |
| Coffee | One Bustelo brick just opened; second brick still sealed. | Coffee runway is healthy. Do not rebuy yet. Start consumption clock from first opened brick. |
| Juice | About 1/10 consumed. | 52 fl oz bottle implies about 5.2 fl oz consumed and 46.8 fl oz left. Not a fast depletion risk. |
| Pantry staples | New rice, beans, vegetables, and tofu are unopened because older grocery-run stock still exists. | This is reserve depth, not avoidance. The May 20 pantry base is extending runway before it is even opened. |
| New Vons data | None reported. | No new order-history or cart update needed. |

Correction: the unopened rice, beans, vegetables, and tofu should not be read as pantry non-activation. The user still has earlier grocery-run stock, so the May 20 staples are functioning as buffer inventory. That improves the runway forecast because the new order is not yet being consumed in those categories.

Interpretation: day-1 behavior is bridge-food oriented for quick eating, while the new pantry base is still in reserve. That is healthier than the first read. Highest leverage next action is still flavor infrastructure, but the urgency is lower: spices/sauce/acid are for making the existing and reserve staples easier to use, not because the new staples are being avoided.

Calculation implications:

| Calculation | Previous Interpretation | Corrected Interpretation |
| --- | --- | --- |
| May 20 order depletion | Untouched staples might mean pantry foods are not entering rotation. | Untouched staples mean May 20 pantry stock is reserve inventory because older stock is still being used. |
| Cost/day from May 20 order | Could be treated as current food burn. | Must be treated as inventory drawdown only; it undercounts total eating while older groceries are still feeding meals. |
| Runway forecast | 17-24 days depended on the May 20 order feeding the current pantry meals immediately. | Forecast should shift toward the strong side because part of the May 20 order has not started its depletion clock yet. |
| Reorder trigger | Watch for pantry non-use. | Watch for bridge-food depletion plus exhaustion of older pantry stock. |
| Top-up need | Flavor infrastructure looked urgent because staples were untouched. | Flavor infrastructure still has high ROI, but it is an unlock for both older and new staples, not proof that the new order is failing. |

Approximate May 20 order drawdown so far:

| Item | Approx. Value Consumed | Notes |
| --- | ---: | --- |
| Burritos | $1.61 | 2 of 8 eaten from a $6.42 pack. |
| Cheese | $0.99 | About 1/8 of a $7.91 block. |
| Juice | $0.35 | About 1/10 of a $3.47 bottle. |
| Waffles | ~$0.90-$1.20 | Exact package count not recorded; 4 waffles eaten from a $5.43 box. |
| Coffee | Unknown | One brick opened, but opened is not consumed. Track when first brick is actually gone. |

Approximate known May 20 depletion excluding coffee: about $3.85-$4.15, or roughly 3.4%-3.7% of the $112.19 order. This is not the user's total food consumption for the day because older groceries are still in use.

Watch next check:

- Is the user still eating older rice, beans, vegetables, or tofu before opening the May 20 stock?
- Are burritos below 4 left?
- Is cheese being used as a meal unlock or just as a snack?
- Is the opened Bustelo brick visibly dropping, or only newly opened?
- Did lack of spices block the pantry base?

### 2026-05-23 Pulse

Source: user report on 2026-05-23.

| Category | Reported State | Model Update |
| --- | --- | --- |
| Burritos | 1 burrito left from 8-pack. | 7 of 8 eaten; this bridge lane is almost depleted. Next food risk is "microwave meal is gone," not "full groceries are gone." |
| Waffles | 14 waffles left. | Waffle breakfast bridge is still healthy. Since 4 waffles had already been eaten on May 21, the box appears to have started around 18 waffles. |
| Pizza | Eaten. | Real-pizza bridge lane is depleted. This was good morale/value food, but it no longer protects a low-effort meal moment. |
| Tofu | One tofu opened. | Cooking phase has started. Treat one 14 oz tofu as active inventory, not fully consumed yet. |
| Cheese | No change from prior report. | Still about 1/8 used and 7/8 remaining. Cheese is stable. |
| New Vons data | No new orders. | No order-history or price update needed. |

Calculation update:

| Item | Approx. May 20 Value Consumed | Notes |
| --- | ---: | --- |
| Burritos | $5.62 | 7 of 8 eaten from a $6.42 pack. |
| Waffles | ~$1.21 | 4 eaten and 14 left implies about 18 waffles total from a $5.43 box. |
| Pizza | $4.94 | One Signature SELECT Rising Crust Supreme pizza eaten. |
| Tofu | $0.00 consumed / $1.97 active | One 14 oz tofu from the 3-pack equivalent is opened. Count when eaten, but track as active perishable inventory. |
| Cheese | $0.99 | Still about 1/8 of a $7.91 block. |
| Juice | $0.35 | Still using May 21 estimate until updated. |

Approximate known May 20 depletion excluding coffee: about $13.11, or roughly 11.7% of the $112.19 order. This is still a low total-order drawdown, but the immediate microwave/ready-meal layer is narrowing: burritos are almost gone and pizza is gone.

User correction: exhausting the ready/no-thought foods first and then starting to cook is a normal personal pattern. This should not be treated as a failure mode by itself.

Corrected interpretation: the grocery run is still on track because the bulk pantry and older stock are carrying runway. The ready-meal layer narrowing has produced the expected phase change from bridge foods into cooking: tofu has now been opened. Do not trigger a full grocery order from this alone. The next high-leverage support is making the opened tofu easy to finish with spices, sauce/acid, visible batch options, and very low-friction first cooked meals.

### 2026-05-24 Pulse

Source: user report on 2026-05-24.

| Category | Reported State | Model Update |
| --- | --- | --- |
| Burritos | Finished. | Burrito bridge lane is fully depleted: 8 of 8 eaten. This is expected under the user's bridge-first pattern. |
| Tofu | Half of one tofu eaten. | Cooking phase is confirmed. Count half of one 14 oz tofu as consumed and half as active/open inventory. |
| Cereal | About 2/3 full. | Treat Kashi cereal as active; about 1/3 consumed. |
| Milk / Fairlife | About 2/3 full. | Assuming this refers to the Fairlife from the May 20 order. About 1/3 consumed unless corrected. |

Calculation update:

| Item | Approx. May 20 Value Consumed | Notes |
| --- | ---: | --- |
| Burritos | $6.42 | 8 of 8 eaten from a $6.42 pack. |
| Tofu | $0.99 | Half of one 14 oz tofu eaten. Three tofu cost $5.91, so one tofu is about $1.97. |
| Kashi cereal | $1.15 | About 1/3 of a $3.46 box consumed. |
| Fairlife / milk | $2.16 | About 1/3 of a $6.49 bottle consumed, assuming this is the May 20 Fairlife. |

Approximate known May 20 depletion excluding coffee is now about $18.21, or roughly 16.2% of the $112.19 order. The order is still on track; the active consumption pattern has moved from bridge foods plus breakfast into confirmed cooking via tofu.

## Current Learned Preferences

- Bustelo is the moka-pot default; do not re-add Lavazza automatically.
- Dry beans are acceptable because overnight soaking is viable.
- Garbanzos and lentils are preferred staples.
- Normal eating pattern: ready/no-thought foods get exhausted first, then cooking starts. Model this as an expected phase change, not as a problem.
- Do not auto-add Greek yogurt, peanut butter, ready-rice pouches, canned beans, Just Bare, or Kashi Chocolate Crunch without a fresh reason.
- Microwave chicken form factor matters: avoid diced chicken next time; prefer strips, fillets, or whole pieces. Saved Vons math had Tyson diced and Tyson grilled strips at the same shelf unit price, so strips should be the next default if still available.
- Flavor variety is currently the highest-ROI missing system piece because the pantry base depends on spices/sauces to stay usable.

## Update Protocol

When new data arrives:

1. Append or update facts in this tracker.
2. Update `vons-final-order-analysis-2026-05-20.md` if the new data changes the analysis.
3. Update `vons-order-analysis-dashboard-2026-05-20.html` if the user-facing visualization should change.
4. Preserve the difference between:
   - exact same-SKU price inflation,
   - package-size or brand substitution economics,
   - behavior/preference data,
   - and public CPI context.

## Next Scheduled Check

Recurring thread check-in: every 3 days at 9:00 AM local time.
