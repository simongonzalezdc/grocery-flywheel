---
name: grocery-flywheel
description: Use Grocery Flywheel for local-first grocery and household replenishment analysis, inventory runway, preference-aware restock planning, sourcing research, and dashboard generation. Trigger when an agent needs to reason from a Grocery Flywheel state JSON file or help plan the next cart without submitting orders.
---

# Grocery Flywheel

Use this skill when a task involves household replenishment, grocery runway, preference corrections, sourcing research, or the Grocery Flywheel state model.

## Start Here

- Read `../../README.md` for the product boundary and local workflow.
- Read `../../docs/DATA_MODEL.md` before changing state JSON.
- Use the CLI for dashboard generation: `grocery-flywheel examples/sample_state.json --output dist/sample-dashboard.html`.
- Use the MCP server when an agent host should call tools directly: `grocery-flywheel-mcp`.

## Workflow

1. Load the state file and identify the inventory surface, acquisition channel, and `as_of` date.
2. Analyze runway before suggesting purchases. The core questions are what is being depleted, what is ignored, and which replenishment decisions are recurring.
3. Treat preferences separately from price math. A cheaper item is not better if the household will not use it.
4. Keep sourcing research as a draft or recommendation. Do not submit orders or modify carts without explicit user approval.
5. Render an HTML dashboard when the human needs to inspect the decision rather than read raw JSON.

## MCP Setup

```json
{
  "mcpServers": {
    "grocery-flywheel": {
      "command": "grocery-flywheel-mcp"
    }
  }
}
```

## Guardrails

- Keep the workflow local-first and approval-first.
- Do not infer allergies, medical diets, or household constraints from thin evidence.
- Preserve private source material boundaries; public examples should stay sanitized.
- Never place grocery orders or change carts automatically.
