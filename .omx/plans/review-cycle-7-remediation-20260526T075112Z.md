# Review Cycle 7 Remediation Plan

Status: approved for Ralph execution
Autopilot phase: ralplan
Review cycle: 7

## Review Verdict

The seventh code-review gate was not clean:

- Architect status: CLEAR
- Code-review recommendation: REQUEST CHANGES

## Blocking Finding

Malformed normalized item objects still produce raw tracebacks when item entries are objects but lack required fields or have malformed nested `product_evidence`.

## Watch To Close

`grocery-flywheel render` trusts producer-populated `contract_errors` and does not independently validate minimal analysis shape or consent.

## Acceptance Criteria

- Normalized item validation rejects missing `name`, invalid numeric fields, malformed `product_evidence`, malformed evidence rows, and malformed list-like evidence fields with `ValueError`.
- CLI normalized import regressions assert nonzero exit, no traceback, and no output file for missing `name`, invalid numeric fields, and malformed `product_evidence`.
- Render has a small analysis contract validator for required render fields, consent shape/value, and basic collection shapes.
- Render regressions assert malformed analysis consent and missing render fields fail closed before HTML is written.
- Tests, Ruff, compile, diff check, Pyright, operator paths, installed console script, and visual smoke pass before the next review gate.
