# Grocery Flywheel

**Local-first grocery replenishment engine that tracks inventory runway, captures depletion signals, and plans your next cart — for households and caregivers who want fewer grocery decisions.**

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI](https://img.shields.io/badge/CI-github%20actions-green.svg)](../../actions)

## What it is

Grocery Flywheel is a Python CLI and analysis engine for grocery and household replenishment. It reads a JSON state file containing purchase history, item consumption, preferences, dietary profiles, and substitution candidates — then computes inventory runway, generates a static HTML dashboard, and surfaces the next-cart recommendation. It runs entirely locally with standard-library Python (no external runtime dependencies), never places orders, and never sends data anywhere.

## Install / Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m grocery_flywheel.cli examples/sample_state.json -o dist/dashboard.html
```

Open `dist/dashboard.html` in a browser to see the generated dashboard. Run `pytest` to verify the test suite.

## Agent Surfaces

Grocery Flywheel exposes the same local-first workflow through three agent-friendly surfaces:

- CLI: `grocery-flywheel examples/sample_state.json --output dist/sample-dashboard.html`
- MCP: `grocery-flywheel-mcp` starts a stdio MCP server with tools for state analysis, dashboard rendering, and sourcing research summaries.
- Skill: [`skills/grocery-flywheel/SKILL.md`](skills/grocery-flywheel/SKILL.md) tells compatible agents when to use the CLI, MCP server, and local approval boundary.

Example MCP config:

```json
{
  "mcpServers": {
    "grocery-flywheel": {
      "command": "grocery-flywheel-mcp"
    }
  }
}
```

## Usage

```bash
# Analyze a replenishment state and render a dashboard
python -m grocery_flywheel.cli examples/sample_state.json --output dist/my-dashboard.html
```

The input is a JSON file describing a purchase order, its items (with spend, consumption fractions, and roles), preferences, dietary profiles, substitutions, and sourcing research. The output is a self-contained HTML file with a visual dashboard showing consumed value, estimated runway, role-level breakdowns, and substitution scores.

## Why / How it works

Most grocery tools optimize lists. Grocery Flywheel optimizes the **replenishment loop**: observe what was bought → capture tiny depletion pulses → separate preference signals from price math → recommend the next cart by runway, unit economics, and likelihood of actually being eaten → render a dashboard that explains the decision instead of making you re-decide everything.

The core insight is that past purchase history contains enough signal to estimate how long your current stock will last — if you track consumption fractions at the item level. The engine uses standard-library Python only (`collections`, `datetime`) and produces a self-contained HTML report, making it safe to run on any machine with Python 3.11+ and no internet access.

> **Best-fit searches:** grocery replenishment tool, household inventory runway calculator, local-first grocery planner, pantry depletion tracker, next-cart recommendation engine, open-source grocery list optimizer

## Links

- [Product requirements (PRD)](docs/PRD.md) — scope and MVP boundary
- [Data model](docs/DATA_MODEL.md) — JSON state contract
- [Workflow spec](docs/WORKFLOW_SPEC.md) — operating loop and state transitions
- [Dietary restrictions module](docs/DIETARY_RESTRICTIONS_MODULE.md) — allergies and dietary profiles
- [Retailer adapters](docs/RETAILER_ADAPTERS.md) — connector architecture
- [Sourcing research](docs/SOURCING_RESEARCH_STAGE.md) — cross-store sourcing logic
- [Operator runbook](docs/OPERATOR_RUNBOOK.md) — verification and release paths
- [Design source of truth](DESIGN.md)
- [AI/agent navigation (llms.txt)](llms.txt)
- [License: MIT](LICENSE)
- **KyaniteLabs:** [kyanitelabs.tech](https://kyanitelabs.tech)
- **Sibling projects:** [Print-OS](https://github.com/simongonzalezdc/Print-OS) · [GameStory-Lab](https://github.com/simongonzalezdc/GameStory-Lab) · [voice-to-sculpture-app](https://github.com/simongonzalezdc/voice-to-scultpure-app) · [CyberWitches](https://github.com/simongonzalezdc/CyberWitches) · [HealthAdvocate](https://github.com/simongonzalezdc/healthadvocate)
