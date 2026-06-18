# Grocery Flywheel

**Local-first grocery replenishment engine that tracks inventory runway, captures depletion signals, and plans your next cart — for households and caregivers who want fewer grocery decisions.**

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI](https://img.shields.io/badge/CI-github%20actions-green.svg)](../../actions)

Grocery Flywheel is a Python 3.11+ CLI and analysis engine that reads a JSON state file containing purchase history, item consumption, preferences, dietary profiles, and substitution candidates — then computes inventory runway, generates a self-contained HTML dashboard, and surfaces the next-cart recommendation. It runs entirely locally with standard-library Python, never places orders, and never sends data anywhere.

---

## Features

- **Inventory runway estimation** — calculates days-of-stock remaining at the item and category level from purchase dates and consumption fractions.
- **Next-cart recommendation** — generates a prioritised shopping list based on depletion timing, unit economics, and preference scores.
- **Data Freshness panel** — surfaces staleness signals so you know which items need a fresh consumption update before the next dashboard render.
- **Static HTML dashboard** — produces a self-contained, shareable dashboard with visual breakdowns of consumed value, runway timelines, role-level summaries, and substitution scores.
- **Dietary profiles & substitutions** — models allergies, dietary restrictions, and ranked substitution candidates per item.
- **Three agent-friendly surfaces** — CLI, MCP server, and Skill manifest for integration with AI assistants and automation workflows.
- **Zero runtime dependencies** — uses only the Python standard library (`collections`, `datetime`, `json`, `pathlib`). No network calls, no telemetry.
- **Sourcing research integration** — attach cross-store sourcing notes to items and surface them in the dashboard for cost-aware shopping.

---

## Installation

Requires **Python 3.11+**.

```bash
# Clone the repository
git clone https://github.com/simon/grocery-flywheel.git
cd grocery-flywheel

# Create and activate a virtual environment
python3 -m venv .venv && source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

No additional packages are needed to run the tool — `.[dev]` installs `pytest` for the test suite only.

---

## Quick start

```bash
# Generate a dashboard from the bundled sample state
python -m grocery_flywheel.cli examples/sample_state.json --output dist/dashboard.html

# Open the dashboard in your browser
open dist/dashboard.html        # macOS
xdg-open dist/dashboard.html   # Linux

# Verify the installation
pytest
```

You should see a fully rendered HTML dashboard showing consumed value, estimated runway, role-level breakdowns, and the data-freshness panel.

---

## Usage

### CLI

```bash
python -m grocery_flywheel.cli <state.json> --output <dashboard.html>
```

Or using the installed entry point:

```bash
grocery-flywheel examples/sample_state.json --output dist/my-dashboard.html
```

### MCP server

Start a stdio MCP server that exposes state analysis, dashboard rendering, and sourcing research tools:

```bash
grocery-flywheel-mcp
```

Example MCP configuration for a compatible host:

```json
{
  "mcpServers": {
    "grocery-flywheel": {
      "command": "grocery-flywheel-mcp"
    }
  }
}
```

### Skill manifest

The file [`skills/grocery-flywheel/SKILL.md`](skills/grocery-flywheel/SKILL.md) tells compatible agents when to invoke the CLI, the MCP server, and where the local approval boundary sits.

### Capture visit CLI

```bash
grocery-flywheel-capture-visit
```

A lightweight entry point for recording store visits as depletion signals.

### Input format

The input is a JSON file describing:

- **Purchase history** — items with unit spend, quantity, and purchase date.
- **Consumption fractions** — how much of each item has been consumed (0.0–1.0).
- **Roles** — item categories (e.g. protein, produce, pantry staple).
- **Dietary profiles & substitutions** — allergies, preferences, and ranked alternates.
- **Sourcing research** — cross-store notes attached to items.

See [`examples/sample_state.json`](examples/sample_state.json) for a complete reference and [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md) for the full contract.

---

## How it works

Most grocery tools optimise lists. Grocery Flywheel optimises the **replenishment loop**:

1. **Observe** what was bought and when.
2. **Capture** tiny depletion pulses over time.
3. **Separate** preference signals from price math.
4. **Recommend** the next cart by runway, unit economics, and likelihood of actually being eaten.
5. **Render** a dashboard that explains the decision instead of making you re-decide everything.

The core insight is that past purchase history contains enough signal to estimate how long your current stock will last — if you track consumption fractions at the item level.

---

## Project structure

```
grocery-flywheel/
├── src/grocery_flywheel/   # Python package (CLI, MCP server, modules)
├── tests/                  # Pytest test suite
├── examples/               # Sample state and retailer profiles
├── skills/                 # Agent skill manifest
├── docs/                   # PRD, data model, workflow spec, ADRs, runbooks
├── DESIGN.md               # Design source of truth
├── AGENTS.md               # Agent guidance
├── llms.txt                # AI/GEO navigation file
└── pyproject.toml          # Build config and entry points
```

---

## FAQ

**Does Grocery Flywheel place grocery orders?**
No. It is a read-only analysis and planning tool. It never contacts retailers, places orders, or sends data over the network.

**What data does it send externally?**
Nothing. All computation happens locally and no telemetry is collected. The tool has zero runtime dependencies beyond the Python standard library.

**What Python version do I need?**
Python 3.11 or later. No third-party packages are required to run the tool itself.

**How do I track consumption over time?**
Update the consumption fractions in your JSON state file as items are used. The Data Freshness panel in the dashboard will flag items that haven't been updated recently.

**Can I use this with an AI assistant?**
Yes. Grocery Flywheel ships with three agent surfaces — CLI, MCP server, and a Skill manifest — so compatible AI agents can analyse your state, render dashboards, and summarise sourcing research.

---

## Documentation

| Document | Description |
|---|---|
| [PRD](docs/PRD.md) | Product requirements and MVP boundary |
| [Data model](docs/DATA_MODEL.md) | JSON state contract |
| [Workflow spec](docs/WORKFLOW_SPEC.md) | Operating loop and state transitions |
| [Dietary restrictions module](docs/DIETARY_RESTRICTIONS_MODULE.md) | Allergies and dietary profiles |
| [Retailer adapters](docs/RETAILER_ADAPTERS.md) | Connector architecture |
| [Sourcing research](docs/SOURCING_RESEARCH_STAGE.md) | Cross-store sourcing logic |
| [Operator runbook](docs/OPERATOR_RUNBOOK.md) | Verification and release paths |
| [Privacy & security baseline](docs/PRIVACY_SECURITY_BASELINE.md) | Data handling guarantees |
| [Decision register](docs/DECISION_REGISTER.md) | Architectural decision records |
| [Design source of truth](DESIGN.md) | Design principles and constraints |
| [AI/agent navigation](llms.txt) | Machine-readable project summary |

---

## Contributing

Contributions are welcome. To get started:

1. **Fork** the repository and create a feature branch from `main`.
2. **Install** dev dependencies: `pip install -e ".[dev]"`
3. **Make your changes** and add tests under `tests/`.
4. **Run the test suite** to verify nothing is broken: `pytest`
5. **Open a pull request** with a clear description of what the change does and why.

For larger changes, please open an issue first to discuss scope. See [`docs/OPERATOR_RUNBOOK.md`](docs/OPERATOR_RUNBOOK.md) for release and verification paths.

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for the full text.

---

## Links

- [llms.txt](llms.txt) — machine-readable project summary for AI/GEO discovery
- **KyaniteLabs:** [kyanitelabs.tech](https://kyanitelabs.tech)
- **Sibling projects:** [Print-OS](https://github.com/simongonzalezdc/Print-OS) · [GameStory-Lab](https://github.com/simongonzalezdc/GameStory-Lab) · [voice-to-sculpture-app](https://github.com/simongonzalezdc/voice-to-scultpure-app) · [CyberWitches](https://github.com/simongonzalezdc/CyberWitches) · [HealthAdvocate](https://github.com/simongonzalezdc/healthadvocate)