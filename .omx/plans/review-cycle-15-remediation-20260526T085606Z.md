# Review Cycle 15 Remediation Plan

## Return To Ralplan Reason

Code review found canonical date validation still accepted non-canonical ISO forms and render-bound display strings still allowed explicit `null`.

## Findings To Close

- Require literal `YYYY-MM-DD` dates before `date.fromisoformat`.
- Reject present-but-null render-bound display strings such as `first_wow.headline` and `first_wow.best_sourcing_move`.

## Acceptance Criteria

- `grocery-flywheel analyze` rejects compact and week-date strings without traceback or output write.
- `grocery-flywheel render` rejects null `first_wow` display fields without traceback or HTML write.
- Full verification reruns clean: pytest, Ruff, compileall, diff check, Pyright, operator CLI path, installed console script, and visual smoke.
