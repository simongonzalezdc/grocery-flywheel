# Review Cycle 12 Remediation Plan

## Return To Ralplan Reason

Architecture review found canonical state validation did not yet require all fields indexed by `analyze_state`, and render analysis validation accepted unsupported schema versions.

## Findings To Close

- `validate_canonical_state` must require `as_of` as a string.
- `validate_canonical_state` must require `order.store` and `order.date` as strings and `order.total` as numeric.
- `validate_analysis_contract` must reject unsupported analysis `schema_version` values using the canonical MVP schema version.

## Acceptance Criteria

- `grocery-flywheel analyze` rejects state missing `order.total` without traceback or analysis write.
- Canonical validation reports missing or malformed `as_of`, `order.store`, `order.date`, and `order.total`.
- `grocery-flywheel render` rejects unsupported analysis schema versions without traceback or HTML write.
- Full verification reruns clean: pytest, Ruff, compileall, diff check, Pyright, operator CLI path, installed console script, and visual smoke.
