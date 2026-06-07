# Review Cycle 19 Remediation Plan

## Findings

Fresh cycle-18 review found two more fail-closed validation gaps in raw
canonical state rows consumed before post-analysis validation:

- Malformed `sourcing_research` rows could omit `item` or provide unsafe
  alternative values, causing `first_wow` / cart-plan generation to raise a
  traceback during `analyze`.
- Malformed `substitutions` rows could provide non-numeric price/friction fields
  or non-list product evidence, causing ranking/dietary evaluation to raise a
  traceback during `analyze`.

## Fix

- Add canonical state validation for substitution rows:
  - required string `current` and `candidate`
  - required numeric `current_unit_price` and `candidate_unit_price`
  - optional numeric friction/quality/savings fields
  - list-shaped candidate evidence rows
- Add canonical state validation for sourcing research rows:
  - required string `item`
  - safe optional display fields and numeric unit/savings/friction fields
  - list-shaped alternatives, constraints, and checked dates
- Reuse product evidence row validation for item and substitution evidence.
- Add contract and CLI regression tests proving malformed rows fail closed before
  analysis, avoid tracebacks, and do not write output files.

## Verification

Pending full cycle-19 verification after implementation.

