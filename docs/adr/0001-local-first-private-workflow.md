# ADR 0001: Keep Grocery Flywheel Local-First And Approval-First

Status: Accepted

## Context

The workflow uses sensitive purchase history, eating behavior, household usage behavior, and preference corrections. It can produce high-leverage recommendations, but checkout automation and grocery-account mutation have real risk.

## Decision

Grocery Flywheel starts as a local-first private workflow. It stores state in local files, renders static dashboards, and treats external cart changes and purchases as approval-only actions.

## Consequences

- The MVP can ship without a hosted backend.
- The user's private purchase history stays local unless deliberately pushed to a private repo.
- Browser or store integrations must preserve an explicit approval boundary.
- Collaboration is still possible through a private repository.

## Alternatives Considered

- Hosted SaaS first: rejected because privacy, auth, and checkout risk would dominate the MVP.
- Fully manual notes only: rejected because the workflow needs repeatable calculations and rendered decision surfaces.
- Autonomous checkout: rejected because purchase submission is irreversible enough to require explicit user approval.
