# Review Cycle 3 Remediation Plan

Status: approved for Ralph execution
Autopilot phase: ralplan
Review cycle: 3

## Review Verdict

The third code-review gate was not clean:

- Architect status: CLEAR
- Code-review recommendation: REQUEST CHANGES

## Blocking Findings

1. Falsey malformed `draft_edit_events` such as `""`, `0`, or `false` are treated as absent instead of rejected.
2. Malformed imported corrections can raise non-operator-friendly exceptions instead of concise `ValueError` messages.
3. Pyright reports optional access in renderer consent handling and a possible `None` subscript in a draft telemetry test.

## Acceptance Criteria

- Draft edit event normalization treats only `None` as absent, accepts `[]`, and rejects all other non-list containers.
- Correction normalization rejects non-list correction containers, non-object entries, and missing `item` / `signal` with `ValueError`.
- CLI import of malformed correction telemetry exits nonzero without tracebacks.
- Pyright, pytest, Ruff, compile, diff check, operator paths, installed console script, and visual smoke are clean before the next review gate.
