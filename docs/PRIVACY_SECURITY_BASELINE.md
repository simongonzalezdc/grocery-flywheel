# Privacy And Security Baseline

This is the default trust posture for Grocery Flywheel as of May 2026. It is product guidance, not legal advice.

## Core Requirements

1. Collect only what is needed for the current user-visible purpose.
2. Keep purchase history, household inventory, dietary profiles, allergy profiles, and retailer sessions private by default.
3. Do not store retailer passwords.
4. Encrypt hosted user data at rest and in transit.
5. Keep local mode available for private use.
6. Provide export and delete.
7. Show retention periods or retention criteria.
8. Label AI-generated recommendations and show evidence/provenance.
9. Never submit checkout without explicit final user approval.
10. Log user edits to drafts as learning telemetry only with clear consent.

## Data Classes

| Data | Sensitivity | Default Handling |
| --- | --- | --- |
| Retailer account/session | High | Session-scoped, no password storage, revoke/clear controls |
| Purchase history | High | Local-first, encrypted in hosted mode, export/delete |
| Household inventory | High | Local-first, minimize sharing |
| Dietary profile | High | Explicit opt-in, never used for ads |
| Allergy or safety-critical dietary profile | Very high | Explicit opt-in, strong warnings, never used for ads |
| Internal cart plan | Medium/high | User-visible, approval-gated |
| External cart draft | Very high | Excluded from MVP; later ADR required |
| Correction telemetry | Medium | Consent-based, delete/export with account |
| Aggregated product analytics | Lower | De-identify where possible, document clearly |

## MVP Implementation Boundary

- `src/grocery_flywheel/privacy.py` defines privacy classes and local-first consent defaults.
- `src/grocery_flywheel/contracts.py` rejects `external_cart_draft` in canonical MVP state.
- Correction telemetry defaults to `local_only`; hosted sync is opt-in only.
- Retailer adapter profiles must not contain passwords, tokens, session cookies, or API keys.
- `order_submit` must remain false for MVP profiles.
- Safety-critical dietary recommendations fail closed: unknown products and
  substitution candidates need candidate-specific evidence before they can be
  treated as safe.
- Persisted correction events, draft edit events, cart plans, run sheets, and
  dietary evaluations carry schema and privacy metadata.

## Retention Defaults

- Local prototype: user controls files.
- Hosted beta: keep active user data while the account is active; provide self-serve delete.
- Raw retailer import artifacts: minimize retention after normalization.
- Browser/session artifacts: clear after import unless the user explicitly saves connection.
- Aggregated diagnostics: keep separate from personal purchase history.

## Security Baseline

- Use OWASP ASVS 5.0 as the web-app verification baseline.
- Use least privilege for retailer adapters.
- Keep adapter code separate from user data.
- Keep secrets out of repos and logs.
- Use explicit consent for account imports.
- Show adapter provenance and confidence.
- Prefer official APIs/export/OAuth where available.
- Use browser-assisted import only as a user-initiated flow.
- Do not bypass retailer access controls or anti-bot defenses.

## Hosted Beta Gate

The local MVP can complete without a hosted deployment. Outside testers require:

- export flow
- delete flow
- encryption at rest or hosting-provider equivalent
- retention criteria
- session clearing
- secrets and log hygiene
- no password storage

## Privacy Sources

- FTC privacy/security guidance: https://www.ftc.gov/business-guidance/privacy-security
- California CCPA overview: https://www.oag.ca.gov/privacy/ccpa
- CPPA data minimization advisory: https://cppa.ca.gov/pdf/enfadvisory202401.pdf
- NIST Privacy Framework: https://www.nist.gov/privacy-framework
- Apple App Review privacy guidance: https://developer.apple.com/app-store/review/guidelines/
- OWASP ASVS: https://github.com/OWASP/ASVS
