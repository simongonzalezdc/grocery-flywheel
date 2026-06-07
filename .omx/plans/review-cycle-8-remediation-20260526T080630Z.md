# Review Cycle 8 Remediation Plan

## Return To Ralplan Reason

Code review remained non-clean because malformed normalized list entries and incomplete render-row validation could still produce raw tracebacks or invalid HTML output.

## Findings To Close

1. Normalized import and canonical validation must reject malformed `dietary_profiles[*]` and `restrictions[*]` entries before `analyze` reaches dietary evaluation.
2. `grocery-flywheel render` must require `contract_errors` and validate the row fields consumed by the renderer, not just top-level collection types.
3. `adapters inspect` must validate adapter profiles before building the capability matrix so malformed `capabilities` cannot traceback.

## Acceptance Criteria

- Malformed dietary profile entries fail with path-specific `ValueError` messages during import and canonical state validation.
- Render refuses missing `contract_errors`, malformed `contract_errors` entries, malformed item rows, malformed table rows, malformed cart rows, and malformed adapter rows before writing HTML.
- Adapter inspection returns a validation error without a traceback for malformed adapter profiles.
- Regression tests cover the reported reproduction cases.
- Full verification reruns clean: pytest, Ruff, compileall, diff check, Pyright, operator CLI path, installed console script, and visual smoke.
