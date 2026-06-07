# Review Cycle 18 Remediation Plan

## Findings

Code review found two high-severity validation gaps:

- The credential phrase scanner rejected the cycle-17 exact notes cases but missed
  common variants such as `api_key:`, `api-key:`, and `session id:`.
- Canonical state validation allowed malformed item rows, so `analyze` could
  crash on a missing `name` instead of failing closed with contract errors.

## Fix

- Broaden the retailer profile credential phrase scanner for common underscore,
  hyphen, and multi-word API/session/token variants.
- Add regression coverage for those credential phrase variants in neutral
  provenance notes.
- Validate canonical item analysis fields before analysis:
  - required non-empty string `name`
  - required numeric `spend`
  - optional numeric fields used by runway math
- Add CLI regression coverage that malformed item fields return validation
  errors, avoid tracebacks, and do not write analysis output.

## Verification

Pending full cycle-18 verification after implementation.

