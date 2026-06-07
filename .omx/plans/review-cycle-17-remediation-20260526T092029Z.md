# Review Cycle 17 Remediation Plan

## Finding

Architectural review found that allowed retailer adapter provenance notes could
carry obvious free-text credential phrases such as `password: hunter2` without a
validation error.

## Risk

Retailer profiles are intended to be declarative capability records only. Allowing
credential-shaped notes weakens the local-first privacy boundary and could let
secrets land in repo, dashboard, or diagnostic surfaces.

## Fix

- Keep `provenance.notes` available for benign setup notes.
- Extend adapter profile secret scanning to reject generic credential phrases in
  any neutral string value.
- Cover `password:`, `cookie=`, `api key:`, `token=`, and `session:` notes with
  a regression test.

## Verification

- `python3 -m pytest tests/test_core.py -q` -> 13 passed.

