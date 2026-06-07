# Review Cycle 1 Remediation Plan

Status: approved for Ralph execution
Autopilot phase: ralplan
Review cycle: 1

## Review Verdict

The first code-review gate was not clean:

- Architect status: BLOCK
- Code-review recommendation: REQUEST CHANGES

## Blocking Findings

1. Safety-critical dietary substitutions can be marked safe without candidate-specific evidence.
2. Product evidence can be treated as current without an evidence type.
3. Adapter validation can miss secret-looking values stored under neutral keys.
4. Imported correction telemetry can bypass schema and privacy metadata.

## Additional Required Fixes

1. CLI operator paths must fail closed on canonical contract errors and show concise errors.
2. Dashboard correction controls must produce local, consent-aware correction telemetry instead of being inert.
3. Persisted analysis objects should carry privacy metadata for cart plans, run sheets, dietary evaluations, and draft/correction telemetry.
4. Adapter profile validation errors should be enforced during import/run and visible in dashboard status.

## Acceptance Criteria

- Unknown substitution candidates under active safety-critical dietary profiles default to `needs_review`, even when the current item is safe.
- Safety-critical `safe` requires current product evidence with `evidence_type`, `source`, `checked_date`, and label/certification content.
- Adapter profiles reject stored secrets by field name, auth/session/header containers, and secret-looking string values.
- Imported corrections and draft edit events are normalized or rejected and validated by `validate_canonical_state`.
- `grocery-flywheel analyze` and `grocery-flywheel run` return nonzero when canonical contract errors exist.
- Correction actions are operable in the static dashboard through local JSON/JSONL export and the CLI can persist consent-gated correction events.
- Tests, compile, diff check, CLI operator paths, installed console-script smoke, and visual dashboard smoke all pass before the next review gate.
