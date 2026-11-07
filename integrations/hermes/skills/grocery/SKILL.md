---
name: grocery
description: Use for local grocery analysis and approval-only drafts.
---
# Grocery Flywheel native workflow

Use exactly one explicit `state_name` (profile-owned basename) or `state_json` on each tool.
Get consent before sending real household/dietary data into chat: Hermes may send inputs and
results to its configured model and retain transcripts. The engine itself is offline, not the host.
Recommend a verified local model/offline configuration for sensitive data. Never infer consent.

1. `grocery_analyze`: inspect runway and depleted inventory.
2. `grocery_dietary`: inspect supplied label evidence. Missing critical evidence means needs_review;
   safe means no matching token in current supplied evidence, not a medical guarantee.
3. `grocery_sourcing`: summarize supplied research questions, never live retailer research.
4. `grocery_plan`: draft only, all rows require human approval; no checkout or retailer cart mutation.
5. `grocery_dashboard`: private HTML artifact, not a server or automatic browser launch.

Dietary/plan accept objective: lowest_cost, fewer_trips, balanced_roi, dietary_restrictions,
allergy_safe, best_quality, lowest_decision_fatigue. Plan mode: pickup, delivery, in_person.
Other tools use the state's objective, not a top-level override.

Start with `/grocery help`, `/grocery status`, `/grocery sample` (sanitized, no state writes).
Then `/grocery analyze {"state_name":"sample.json"}`,
`/grocery dietary {"state_name":"sample.json","objective":"allergy_safe"}`,
`/grocery sourcing {"state_name":"sample.json"}`,
`/grocery plan {"state_name":"sample.json","mode":"pickup"}`,
`/grocery dashboard {"state_name":"sample.json"}`.

See [local workflow](references/local-workflow.md) for file ownership and removal.
