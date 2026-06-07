# Review Cycle 2 Remediation Plan

Status: approved for Ralph execution
Autopilot phase: ralplan
Review cycle: 2

## Review Verdict

The second code-review gate was not clean:

- Architect status: CLEAR
- Code-review recommendation: REQUEST CHANGES

## Blocking Findings

1. Inline dashboard JavaScript embeds untrusted consent values with regular `json.dumps`, allowing `</script>` breakout.
2. Canonical validation is skipped for unversioned state, so `external_cart_draft` can evade fail-closed operator paths.
3. Imported `draft_edit_events` are silently dropped instead of being normalized or rejected.

## Acceptance Criteria

- Dashboard script data is encoded with script-safe JSON escaping and consent telemetry values are validated to an allowed enum.
- `analyze_state` and CLI contract checks run `validate_canonical_state` unconditionally for canonical operator paths.
- Legacy/sample rendering is explicit and still rejects excluded cart mutation fields.
- Normalized imports carry valid draft edit events with schema/privacy metadata and reject malformed draft telemetry with concise errors.
- Regression tests cover XSS-safe render output, invalid consent rejection, unversioned external cart draft failure, and draft edit event normalization/rejection.
- Tests, Ruff, compile, diff check, operator paths, installed console script, and desktop/mobile visual smoke pass before the next review gate.
