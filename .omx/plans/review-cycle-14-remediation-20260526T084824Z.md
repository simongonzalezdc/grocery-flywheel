# Review Cycle 14 Remediation Plan

## Return To Ralplan Reason

Architecture review returned `WATCH` because product evidence rows missing required metadata were silently dropped during import, and canonical date semantics were validated only at analysis runtime.

## Findings To Close

- Normalized import must reject product evidence rows missing `evidence_type`, `source`, or `checked_date`.
- Canonical state validation must parse-check `as_of` and `order.date` as ISO dates.
- The cycle-13 code-review finding remains included: renderer-consumed display strings must be validated before render.

## Acceptance Criteria

- Malformed product evidence metadata fails during import with a path-specific error.
- `grocery-flywheel analyze` rejects invalid `as_of` and `order.date` strings before `analyze_state`, without traceback or output write.
- `grocery-flywheel render` rejects malformed display strings before HTML write.
- Full verification reruns clean: pytest, Ruff, compileall, diff check, Pyright, operator CLI path, installed console script, and visual smoke.
