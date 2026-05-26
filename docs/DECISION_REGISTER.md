# Decision Register

Updated: 2026-05-26

This register maps the user's answer dump onto the earlier product questions. When the user did not answer directly, the default is aligned to current product, privacy, accessibility, and security best practice as of May 2026.

## Source Principles Used For Defaults

- FTC privacy/security guidance: collect only what is needed, keep it safe, and dispose of it securely.
- California CCPA/CPRA guidance: data minimization, purpose limitation, deletion, correction, opt-out/limit rights where applicable.
- NIST Privacy Framework: identify and manage privacy risk across the data lifecycle.
- OWASP ASVS 5.0: current web-app security verification baseline.
- WCAG 2.2: accessibility floor for web/mobile surfaces.
- Apple App Review privacy guidance: disclose data collection, retention/deletion, consent, and withdrawal.
- FDA food allergen guidance: the U.S. major allergens are milk, eggs, fish, Crustacean shellfish, tree nuts, peanuts, wheat, soybeans, and sesame.

## P0 Decisions

| ID | Question | Decision | Status |
| --- | --- | --- | --- |
| P0-1 | First real user | User is first real user; first outside testers are other personal household users. | Resolved |
| P0-2 | First wow result | Estimated savings plus sourcing alternatives. Restock draft and stockout prevention come later in the journey. | Resolved |
| P0-3 | Setup complete | Retailer connected, purchase history imported, dashboard shown, user ready to place pickup/delivery/in-person order. | Resolved |
| P0-4 | Import methods | Support all methods through adapter capabilities. Best-practice priority: official API/export if available, retailer history import, browser-assisted import, email/order receipt import, receipt/photo/manual fallback. | Defaulted |
| P0-5 | Auth friction | Ask for login only after explaining the immediate value. Never store retailer passwords. Prefer OAuth/export/session-scoped browser import. | Defaulted |
| P0-6 | Cart behavior | Create a live cart draft when the user wants pickup/delivery. If the user shops in person, produce aisle/order/checklist mode instead. | Resolved |
| P0-7 | Approval boundary | Checkout requires direct hard approval. External cart mutation should be visible, reversible, and logged. User edits after draft creation become learning telemetry. | Resolved + defaulted |
| P0-8 | Data protection | Local-first by default; hosted mode requires encryption, minimization, export/delete, retention policy, and consent. | Defaulted |
| P0-9 | Platform | CLI for the user/development. Local web app for product surface. Hosted web app for testers. Mobile-responsive/PWA baseline. Browser extension only as retailer-adapter helper if needed. | Inferred |

## P1 Product Shape

| ID | Question | Decision | Status |
| --- | --- | --- | --- |
| P1-10 | Main surface | Guided setup + command center + assistant loop + sourcing research. Dashboard is proof surface; restock/cart draft is action. | Defaulted |
| P1-11 | Usage cadence | Mostly before shopping; optional daily/weekly depletion pulses; feedback always available when trying products. | Resolved |
| P1-12 | Product feel | Calm, helpful, accessible, extremely easy to read. Designed for neurodivergent needs without labeling it that way. | Resolved |
| P1-13 | Opinionated vs configurable | Product is opinionated in workflow but user-configurable in optimization objective. | Resolved |
| P1-14 | Optimization target | User chooses: lowest cost, lowest decision fatigue, best quality, fewer trips, balanced ROI, dietary restrictions, allergy-safe, or custom. | Resolved |
| P1-15 | Beautiful means | Premium, cozy, editorial, clean, high-quality, almost black/Apple-like but warmer and more useful. | Resolved |

## P1 Retailer Adapter System

| ID | Question | Decision | Status |
| --- | --- | --- | --- |
| P1-16 | Who creates adapters | Users name stores and provide access/examples; agents/tools create adapter profiles when possible. Users should not need to code. | Defaulted |
| P1-17 | Minimum viable adapter | Capability-based. Purchase history unlocks first value. Product search/price lookup/unit price unlock sourcing research. Cart draft is optional and approval-gated. | Defaulted |
| P1-18 | Shareable adapters | Adapter manifests can become shareable. Credentials, sessions, user history, and fragile personal selectors stay private. | Defaulted |
| P1-19 | Adapter contents | Store normalized schema plus capability metadata. Browser selectors/steps may exist in versioned adapter modules, isolated from user data. | Defaulted |
| P1-20 | Blocked/changing retailers | Degrade gracefully to export/email/receipt/manual. Do not bypass anti-bot or terms barriers. Show adapter health and confidence. | Defaulted |
| P1-21 | Vons data role | Vons can be a private test fixture because evidence exists. It is not the architecture. | Resolved |

## P1 Data And Intelligence

| ID | Question | Decision | Status |
| --- | --- | --- | --- |
| P1-22 | Enough history | 3+ months preferred, 3 orders acceptable, 1 order allowed with low confidence. | Defaulted |
| P1-23 | Learning method | Explicit corrections are high confidence. Repeated behavior can be inferred but should remain lower confidence until confirmed. | Defaulted |
| P1-24 | Food/non-food model | Shared replenishment core with role/category modules for food, household consumables, pet supplies, operator supplies, allergies, etc. | Resolved |
| P1-25 | Nutrition/protein | Do not make nutrition a default product promise. Support optional dietary restriction and nutrition goals. Prioritize safety-critical restrictions, including allergies, over general health advice. | Defaulted |
| P1-26 | Price history | Track same-SKU price history, personal price history, and current unit economics separately. | Defaulted |
| P1-27 | Confidence | Show confidence and evidence. Low-confidence outputs are allowed if clearly labeled and useful. | Defaulted |

## P1 Sourcing Research

| ID | Question | Decision | Status |
| --- | --- | --- | --- |
| P1-28 | When to source | Detect patterns and run in background for recurring, high-spend, bulk-friendly, suspiciously expensive, or user-flagged items. | Resolved |
| P1-29 | Extra-trip burden | Model trip burden as friction cost. Savings must beat extra effort unless user explicitly wants best price. | Defaulted |
| P1-30 | Source types | Include grocery, warehouse, online, restaurant supply, office supply, ethnic markets, specialty/local stores where relevant. | Resolved |
| P1-31 | Membership/coupons/shipping | Model total effective price, including membership, coupons, shipping, delivery fees, pickup minimums, taxes where available. | Resolved |
| P1-32 | Subscriptions/bulk | Bulk buys are allowed when storage and use pattern fit. Subscriptions are opt-in only because the user dislikes them. | Resolved |

## P2 Business And Distribution

| ID | Question | Decision | Status |
| --- | --- | --- | --- |
| P2-33 | Scope timing | Build for the user first, but aim immediately at other personal household users/testers. | Resolved |
| P2-34 | Business shape | Likely open-source toolkit plus paid hosted app and/or implementation services. Keep options open. | Inferred |
| P2-35 | Public/private split | Eventually public core plus private examples is plausible. Current repo stays private until explicit permission. | Resolved |
| P2-36 | First paid use case | Household grocery savings is first. Dietary restrictions optimization is a strong adjacent paid/safety path, with allergy-safe cart scanning as a subset. | Resolved |

## P2 Trust, Safety, UX

| ID | Question | Decision | Status |
| --- | --- | --- | --- |
| P2-37 | Delete history | Yes. Self-serve export and delete are required. | Defaulted |
| P2-38 | Evidence | Yes. Use progressive disclosure: summary first, evidence drawer when wanted. | Defaulted |
| P2-39 | AI labels | Yes. Label AI-generated recommendations and show evidence/provenance. | Defaulted |
| P2-40 | Correction chips | Include: never again, buy elsewhere, emergency only, good default, wrong size, wrong format, too expensive, dietary conflict, allergy risk, bad quality, too much friction. | Defaulted |
| P2-41 | Worst failure | Priority: safety-critical dietary/allergy conflict, unauthorized checkout, wrong item/cart mutation, wrong price, missed critical stockout, too many questions. | Defaulted |

## Remaining Taste Decisions

These do not block the next prototype, but they should be revisited after seeing the first working flow:

1. Exact visual style: premium black editorial vs warmer household command center.
2. Hosted app business model: hosted subscription, implementation service, or open-core hybrid.
3. Dietary restrictions module depth: label scanner only, cart-level blocker, or household profile system.
4. In-person shopping mode: checklist, aisle route, or store-agnostic run sheet.
5. How much automation users trust before they want to inspect every step.
