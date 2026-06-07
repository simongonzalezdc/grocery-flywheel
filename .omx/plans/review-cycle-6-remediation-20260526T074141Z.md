# Review Cycle 6 Remediation Plan

Status: approved for Ralph execution
Autopilot phase: ralplan
Review cycle: 6

## Review Verdict

The sixth code-review gate was not clean:

- Architect status: BLOCK
- Code-review recommendation: REQUEST CHANGES

## Blocking Findings

1. Normalized import can traceback on malformed top-level payloads and malformed `items` containers.
2. Dashboard rendering treats explicit malformed non-object analysis consent as local correction telemetry.

## Acceptance Criteria

- Normalized import rejects non-object payloads with `ValueError`.
- Normalized import treats absent or `null` `items` as empty if needed, but rejects every other non-list `items` container with `ValueError("items must be a list")`.
- CLI import regression covers `items: 0`, `false`, `""`, `{}`, and top-level JSON list without traceback and without output files.
- Dashboard correction controls treat explicit malformed non-object consent as `disabled`, not `local_only`.
- Tests, Ruff, compile, diff check, Pyright, operator paths, installed console script, and visual smoke pass before the next review gate.
