# Grocery Flywheel

**Free, open-source, local-first groceries without decision fatigue.**

Grocery Flywheel is a personal tool that ends the "what do we need?" loop. It tracks what you bought, notices what you've used, flags what's going stale, learns your corrections, and drafts the next cart — **you** approve everything. It never places orders, never touches a retailer account, and never sends your data anywhere. Python, zero runtime dependencies, works offline.

## Why you might like it

- **Runway, not lists.** Most grocery apps optimize the shopping list. This one optimizes the replenishment loop: observe depletion, estimate how many days you have left, and tell you before you run out — not after.
- **Your corrections stick.** Mark something "never again" or "wrong format" once; the flywheel remembers and stops suggesting it.
- **Allergy-safe by construction.** Dietary restrictions are evaluated against product evidence you control — and when evidence is missing, items are flagged for review instead of silently passing. Safety never fails open.
- **Private by design.** Everything is a JSON file on your machine. Privacy classes and consent flags are part of the data contract itself, not a policy page.
- **Works with your AI assistant.** A built-in MCP server (5 tools) lets Claude, Cursor, or any MCP client analyze your state, check dietary safety, and draft your next cart — locally.

## 30-second first look

```bash
pipx install git+https://github.com/simongonzalezdc/grocery-flywheel   # or: uv tool install git+https://github.com/simongonzalezdc/grocery-flywheel
grocery-flywheel examples/sample_state.json --output dist/sample-dashboard.html
```

Open `dist/sample-dashboard.html` in a browser: the dark command-center dashboard with runway, sourcing moves, dietary flags, and a next-cart plan that waits for your approval.

<details><summary>No pipx? Plain venv works too</summary>

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install git+https://github.com/simongonzalezdc/grocery-flywheel
```

</details>

## What it actually does today

Honest status, as of this release:

- **Working:** hand-authored or imported state → analysis → dark dashboard (runway, depletion, roles, freshness badges, easy-food rotation, trip overhead with amortized time cost, dietary evaluation, objective-aware substitutions, sourcing research, internal cart plan that always requires your approval).
- **Working:** import from normalized JSON or CSV retailer-history exports (`grocery-flywheel import normalized|csv`), with a versioned, fail-closed data contract on write.
- **Working:** MCP server (`grocery-flywheel-mcp`) — analyze, render dashboard, summarize sourcing, evaluate dietary, plan next cart.
- **Working:** trip logging (`grocery-flywheel-capture-visit`), corrections (`grocery-flywheel corrections add`), objectives (`--objective lowest_cost|fewer_trips|allergy_safe|…`).
- **Not automatic:** connecting to retailer accounts or scraping receipts. Import the export files your retailer gives you; adapters for deeper integration are designed (see `docs/adapters.md`) but nothing logs into anything, by design.

## The loop

1. Import or record what was bought.
2. Capture tiny depletion pulses after eating.
3. Record corrections; they become durable preferences.
4. Ask for the next cart by your objective (cost, trips, allergy-safe…).
5. Review the drafted plan — the approval boundary is structural: `checkout_available` is always `false`.

## Install for AI assistants (MCP)

```json
{
  "mcpServers": {
    "grocery-flywheel": {
      "command": "grocery-flywheel-mcp"
    }
  }
}
```

Tools: `analyze_replenishment_state`, `render_replenishment_dashboard`, `summarize_sourcing_research`, `evaluate_dietary`, `plan_next_cart`. JSON-RPC 2.0 over stdio, stateless. A packaged skill lives in [`skills/grocery-flywheel/SKILL.md`](skills/grocery-flywheel/SKILL.md).

## Repo map

- `src/grocery_flywheel/` — the engine. `model/` holds the state contract (lenient read-side types + fail-closed write-side contract); `rendering/` holds every HTML string behind a panel registry; importers, dietary, corrections, sourcing, optimization, and the MCP server are plain modules.
- `examples/sample_state.json` — sanitized example state. `examples/imports/` — example retailer-history payloads for the importers.
- `tests/golden/` — the two dashboard goldens (legacy + canonical) that gate every PR.
- `docs/PRD.md` — product requirements. `docs/DATA_MODEL.md` — the state contract, all vintages. `docs/adapters.md` — retailer adapters + onboarding + sourcing research. `docs/patterns.md` — reusable flywheel patterns + expansion markets. `docs/design.md` — design direction (visual companion: [design-preview.html](docs/design-preview.html)). `docs/DECISION_REGISTER.md` — every decision, ever. `docs/DIETARY_RESTRICTIONS_MODULE.md` — the safety model. `docs/WORKFLOW_SPEC.md` — the operating loop. `docs/OPERATOR_RUNBOOK.md` — run/verify/release. `docs/PRIVACY_SECURITY_BASELINE.md` — trust posture. `docs/adr/` — architecture decisions.
- [`CONTEXT.md`](CONTEXT.md) — the domain glossary (start here if terms like *runway* or *pulse* are new).
- [`llms.txt`](llms.txt) — machine-readable index for AI agents.
- [`SECURITY.md`](SECURITY.md) — how to report vulnerabilities.

## Contribute

```bash
git clone https://github.com/simongonzalezdc/grocery-flywheel
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

CI runs the full suite, lint, a docs link check, and secret scanning on every PR — a green build means green. MIT licensed. Development happens on Forgejo; GitHub is the public mirror.

## License

[MIT](LICENSE). No accounts, no cloud, no telemetry — just groceries.
