# grocery-flywheel

## Project

Local-first grocery replenishment engine and household inventory runway calculator.

## Rules

- Keep real household data, dietary profiles, addresses, sourcing notes, and receipts out of the repository.
- Use sanitized sample state files for docs and tests.
- Prefer standard-library Python and local-only workflows unless a connector is explicitly documented.
- Verify changes with `pytest` and Gitleaks before publishing.

<!-- EMPOWER_ORCHESTRATOR:START -->
## Empower the Orchestrator

This repository follows the Empower Orchestrator law. If a top-level agent sees a repeatable task or recurring failure, it should consider the smallest durable improvement after stating the four-question blast-radius check: scale, severity, reversibility, and predictability.

Workers and subagents stay inside assigned scope and provide verification evidence before completion claims.

Full recipe: `docs/agent-law/empower-orchestrator.md`.
<!-- EMPOWER_ORCHESTRATOR:END -->

