# ADR 0002: Gate Hosted Beta On Privacy Controls

Status: Accepted

## Context

The MVP can provide value as a local-first tool, but outside household testers
would introduce sensitive purchase history, dietary restrictions, correction
telemetry, and retailer-session handling. Those are high-trust data classes.

## Decision

Hosted beta is not required for local MVP completion. Hosted beta is allowed only
after these controls exist and are verified:

- export flow
- delete flow
- encryption at rest or hosting-provider equivalent
- retention criteria
- session clearing
- secrets and log hygiene
- no password storage

The implementation exposes this as a gate in `grocery_flywheel.privacy` so tests
can prove hosted readiness is explicit.

## Consequences

- Local MVP work can keep moving without premature hosting infrastructure.
- Outside testers cannot be treated as "just another local run."
- Privacy controls become a product gate, not a documentation afterthought.

## Alternatives Considered

- Hosted first: rejected because auth/privacy work would delay first-wow proof.
- Untracked hosted prototype: rejected because purchase and dietary data are too
  sensitive for implicit retention or unclear delete/export paths.
