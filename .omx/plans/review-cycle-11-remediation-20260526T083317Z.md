# Review Cycle 11 Remediation Plan

## Return To Ralplan Reason

Architecture review found the null-list remediation was still incomplete for core/render-consumed dietary restrictions and cart plan items.

## Findings To Close

- Reject explicit `null` for `dietary_profiles[].restrictions` during normalized import, canonical state validation, and analysis render validation.
- Reject explicit `null` for `cart_plan.items` during analysis render validation.
- Validate `adapter_matrix` itself as a list before validating rows or rendering adapter status.

## Acceptance Criteria

- `grocery-flywheel analyze` rejects canonical states with `dietary_profiles[].restrictions = null` without a traceback or output write.
- `grocery-flywheel render` rejects analysis JSON with `dietary_profiles[].restrictions = null` and `cart_plan.items = null` without a traceback or HTML write.
- `grocery-flywheel render` rejects non-list `adapter_matrix` before writing HTML.
- Regression tests cover import, canonical validation, analyze, and render paths.
- Full verification reruns clean: pytest, Ruff, compileall, diff check, Pyright, operator CLI path, installed console script, and visual smoke.
