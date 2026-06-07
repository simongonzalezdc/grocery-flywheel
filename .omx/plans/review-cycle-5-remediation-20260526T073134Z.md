# Review Cycle 5 Remediation Plan

Status: approved for Ralph execution
Autopilot phase: ralplan
Review cycle: 5

## Review Verdict

The fifth code-review gate was not clean:

- Architect status: BLOCK
- Code-review recommendation: REQUEST CHANGES

## Blocking Findings

1. Explicit malformed falsey consent is defaulted to `local_only` during normalized import.
2. Canonical validation allows nonempty correction/draft telemetry when consent is `disabled` or `none`.
3. Malformed `items` containers can raise tracebacks before contract validation is reported.

## Acceptance Criteria

- Import defaults consent only when the field is absent or explicitly `null`; every other non-object consent value raises `ValueError`.
- Canonical validation rejects nonempty `corrections` and `draft_edit_events` unless correction telemetry consent is `local_only` or `hosted_opt_in`.
- Canonical validation short-circuits malformed `items` before iteration.
- CLI `analyze` fails closed without traceback for malformed `items`, malformed consent, and disabled/none consent with persisted telemetry.
- Tests, Ruff, compile, diff check, Pyright, operator paths, installed console script, and visual smoke pass before the next review gate.
