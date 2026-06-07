# Review Cycle 4 Remediation Plan

Status: approved for Ralph execution
Autopilot phase: ralplan
Review cycle: 4

## Review Verdict

The fourth code-review gate was not clean:

- Architect status: BLOCK
- Code-review recommendation: REQUEST CHANGES

## Blocking Findings

1. Canonical validation still treats falsey malformed sensitive event containers as absent.
2. Imported correction telemetry is normalized and persisted even when consent disables correction telemetry.

## Acceptance Criteria

- `validate_sensitive_events` treats only `None` as absent, accepts `[]`, and rejects every non-list value including `""`, `0`, `false`, and `{}`.
- Canonical contract tests cover falsey malformed `corrections` and `draft_edit_events`.
- Importing corrections with `consent.correction_telemetry` set to `disabled` or `none` fails closed with a concise `ValueError`.
- CLI import of disabled-consent corrections exits nonzero without tracebacks.
- Tests, Ruff, compile, diff check, Pyright, operator paths, installed console script, and visual smoke pass before the next review gate.
