# Review Cycle 9 Remediation Plan

## Return To Ralplan Reason

Architecture review found two remaining schema/consumer mismatches after cycle 8: adapter rows could contain malformed renderer-consumed fields, and adapter profile validation did not require scalar/list/boolean field shapes before inspect/scoring.

## Findings To Close

1. Render contract validation must validate the fields consumed by `render_adapter_row`, `render_sourcing`, `render_substitutions`, and `render_cart_plan`, including optional fields and list element types.
2. Retailer adapter profile validation must be schema-shaped: string identity fields, list-of-string channels/acquisition methods/constraints, object provenance/capabilities, and boolean capability values.
3. `adapters inspect` must fail closed for malformed profile scalar/list fields without a traceback.
4. Canonical state validation must reject non-object state payloads and non-object `order` values before any `.get` access.

## Acceptance Criteria

- `adapters inspect` returns validation errors without tracebacks for malformed `capabilities`, `acquisition_methods`, `channels`, and non-boolean capability values.
- `grocery-flywheel render` rejects malformed `adapter_matrix`, `sourcing_research`, `substitutions`, and `cart_plan` rows before writing HTML.
- `grocery-flywheel analyze` rejects top-level non-object state and non-object `order` before writing analysis, without tracebacks.
- Regression tests cover both architect reproductions.
- Full verification reruns clean: pytest, Ruff, compileall, diff check, Pyright, operator CLI path, installed console script, and visual smoke.
