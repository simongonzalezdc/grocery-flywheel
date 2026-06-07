# Review Cycle 16 Remediation Plan

## Return To Ralplan Reason

Architecture review found strict date validation was not applied to nested canonical and render-analysis date fields. Code review also found the documented legacy sample-state render path no longer worked under the stricter contract.

## Findings To Close

- Validate canonical nested date fields: product evidence `checked_date`, correction/draft `created_at`, pulse `date`, and sourcing alternative `checked_date`.
- Validate render-analysis date fields: analysis `as_of`, `order.date`, product evidence `checked_date`, pulse `date`, and sourcing alternative `checked_date`.
- Keep the documented positional `examples/sample_state.json` render path working by migrating the sample to canonical state shape and covering it with a CLI regression.

## Acceptance Criteria

- Non-canonical compact/week dates fail at contract boundaries without tracebacks or output writes.
- `examples/sample_state.json --output ...` succeeds through the legacy positional CLI path.
- Full verification reruns clean: pytest, Ruff, compileall, diff check, Pyright, operator CLI path, installed console script, and visual smoke.
