# Review Cycle 10 Remediation Plan

## Return To Ralplan Reason

Code review found that render-contract validation still allowed `null` for list fields that the renderer joins or iterates directly.

## Finding To Close

- Reject `null` for renderer-consumed list fields rather than treating those fields as absent: sourcing alternative `constraints`, adapter row `acquisition_methods`, adapter row `enabled_capabilities`, and adapter row `errors`.

## Acceptance Criteria

- `grocery-flywheel render` rejects null renderer-consumed list fields with validation errors before writing HTML.
- No traceback is printed for those malformed analysis payloads.
- Regression tests cover null list values in sourcing and adapter rows.
- Full verification reruns clean: pytest, Ruff, compileall, diff check, Pyright, operator CLI path, installed console script, and visual smoke.
