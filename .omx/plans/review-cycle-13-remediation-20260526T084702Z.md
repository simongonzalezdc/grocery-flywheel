# Review Cycle 13 Remediation Plan

## Return To Ralplan Reason

Code review found malformed display strings in `first_wow` could bypass validation and traceback during render.

## Findings To Close

- Validate `first_wow.headline` and `first_wow.best_sourcing_move` as strings before render.
- Validate adjacent renderer-consumed optional display strings: `objective_label`, item `category`/`confidence`, product evidence display fields, dietary profile labels/restriction display fields, and cart plan `mode`.

## Acceptance Criteria

- `grocery-flywheel render` rejects malformed `first_wow` display strings without traceback or HTML write.
- Adjacent malformed display strings are rejected by analysis contract validation before render.
- Full verification reruns clean: pytest, Ruff, compileall, diff check, Pyright, operator CLI path, installed console script, and visual smoke.
