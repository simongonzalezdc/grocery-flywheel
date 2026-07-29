# Grocery Flywheel

Local-first grocery and household replenishment engine: inventory runway, depletion tracking, preference-aware restock planning, sourcing research, and dashboard generation.

## Quick start

```bash
git clone https://github.com/simongonzalezdc/grocery-flywheel.git
cd grocery-flywheel
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m grocery_flywheel.cli examples/sample_state.json -o dist/dashboard.html
```

## Docs

- [Skill](skills/grocery-flywheel/SKILL.md)
- [PRD](docs/PRD.md)
- [Data model](docs/DATA_MODEL.md)
- [Workflow](docs/WORKFLOW_SPEC.md)

## License

See [LICENSE](LICENSE).
