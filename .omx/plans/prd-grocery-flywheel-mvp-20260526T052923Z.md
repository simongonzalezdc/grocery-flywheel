# PRD: Grocery Flywheel MVP

Created: 2026-05-26T05:29:23Z
Status: Consensus approved by Architect and Critic

## Product Objective

Build the first working Grocery Flywheel MVP: a local-first, mobile-responsive replenishment product that imports retailer purchase history through adapter profiles, estimates savings, finds sourcing alternatives, and renders a beautiful command-center dashboard with approval-safe cart/restock guidance.

## Primary User

The first user is the repo owner. The first outside testers are other personal household users.

## First Wow

The first wow result is:

1. "Here is what you regularly buy."
2. "Here is where you are overspending or buying from the wrong source."
3. "Here are the best sourcing alternatives and estimated savings."

Restock drafts, stockout prevention, and dietary restriction scanning are important, but they should not be the first thing the user must understand.

## Scope

### In Scope

- Retailer adapter profile architecture.
- Versioned canonical contracts and privacy classes before feature modules.
- Retailer purchase-history import from normalized files first, browser-assisted import as a later adapter implementation path.
- Savings analysis and sourcing research.
- Static and local web dashboard.
- Mobile-responsive command center.
- User-selectable optimization objective.
- Consent-aware correction telemetry from user edits.
- Dietary restrictions profile model and UI surface, with allergies as safety-critical subset.
- Privacy and security baseline suitable for hosted testers.
- Internal cart/restock plan generation that never checks out.

### Out Of Scope For MVP

- Autonomous checkout.
- External retailer cart mutation in MVP.
- Public repository release.
- Storing retailer passwords.
- Bypassing retailer anti-bot or access controls.
- Full restaurant POS/accounting/compliance.
- Medical advice or guarantees.

## User Journey

1. User opens local web app or hosted beta.
2. User names stores they use.
3. App creates or selects retailer adapter profiles.
4. App imports retailer history via available adapter path.
5. App normalizes items, sizes, unit prices, categories, and purchase cadence.
6. App surfaces first wow: estimated savings plus sourcing alternatives.
7. User corrects items, formats, preferences, and stores.
8. App renders dashboard with runway, savings, sourcing, dietary restrictions, and evidence.
9. If pickup/delivery is desired, app creates an internal approval-gated cart plan or restock draft.
10. If in-person shopping is desired, app creates a store-agnostic shopping run sheet.

## Acceptance Criteria

- User can run a CLI command to inspect retailer adapter profiles and see capability scores.
- User can run a CLI command to import normalized retailer history into a canonical state file.
- User can run a CLI command to generate a dashboard from imported state.
- Local web app can load the same state and show the command center.
- Dashboard includes estimated savings, sourcing alternatives, retailer adapter status, dietary restrictions, and correction actions.
- User-selectable optimization objective appears in analysis and dashboard.
- Adapter profile builder can create a valid retailer profile without hand-editing JSON.
- External retailer cart mutation and checkout are not implemented in MVP.
- Internal cart plans/restock drafts are user-visible and approval-gated.
- Tests validate adapter profiles, import normalization, savings calculations, sourcing ranking, dietary profile handling, and dashboard rendering.
- Tests validate ranking differences for lowest cost, fewer trips, balanced ROI, and allergy-safe objectives.
- Tests validate safety-critical dietary unknowns as `needs_review`.
- Tests validate first wow from imported fixture data, not only hand-authored state.
- Privacy/security docs are reflected in implementation boundaries.
- The app works on mobile viewport widths.
- Local MVP completion does not require hosted deployment; hosted beta requires privacy/security gate before outside testers.

## Success Metrics

- Time to first useful dashboard under 5 minutes for a tester with retailer history export or prepared browser import.
- At least one sourcing/savings insight appears on the first dashboard when recurring items exist.
- User can reject/correct at least 5 recommendation types: wrong format, too expensive, buy elsewhere, never again, dietary conflict.
- No tests are skipped for core analysis.
- No checkout path exists without hard approval.
