# Review Cycle 20 Remediation Plan

## Finding

Architecture review found that CLI operator paths validated canonical state before
analysis, but the exported package API `analyze_state` could still be called
directly with malformed state and raise `KeyError` before callers saw contract
errors.

## Fix

- Validate canonical state at the top of exported `analyze_state`.
- Raise a deterministic `ValueError` with contract validation details before any
  analysis, sourcing, substitution, cart-plan, or first-wow logic runs.
- Update direct core tests to use canonical fixtures.
- Add a public API regression test proving malformed `sourcing_research` fails
  closed through `analyze_state` itself.

## Verification

Pending full cycle-20 verification after implementation.

