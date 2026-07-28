# Grocery Flywheel

Local-first grocery replenishment engine that tracks inventory runway, captures depletion signals, and plans your next cart — for households and caregivers who want fewer grocery decisions.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m grocery_flywheel.cli examples/sample_state.json -o dist/dashboard.html
```

## Docs

- [`skills/grocery-flywheel/SKILL.md`](skills/grocery-flywheel/SKILL.md)
- [Product requirements (PRD)](docs/PRD.md)
- [Data model](docs/DATA_MODEL.md)
- [Workflow spec](docs/WORKFLOW_SPEC.md)
- [Dietary restrictions module](docs/DIETARY_RESTRICTIONS_MODULE.md)

## License

See [LICENSE](LICENSE).
