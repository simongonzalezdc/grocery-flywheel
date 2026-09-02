# Grocery Flywheel v0.2.0 — Redesign via ralplan → wayfinder → to-spec → to-tickets

**Pipeline status:** ralplan consensus COMPLETE (Planner v2 → Architect SOUND-WITH-CONDITIONS, 6 conditions folded → Critic **APPROVE**, 4 advisory notes folded into tickets below). Wayfinder map charted (4 HITL decision tickets). Spec written. Ticket breakdown below. All artifacts materialize as step 0 since plan mode blocked writes.

## Consensus plan (deliberate mode)

**Principles:** truth before reach · one home per fact (documented exception: 3 schema vintages during migration) · accessibility is the feature · behavior-preserving first · every PR independently green + revertible.
**ADR:** 6-PR phased redesign with WIP library harvest and CI-truth-first sequencing. Rejected: big-bang on WIP base (unreviewable, no merge base, un-gatable); docs-first only (leaves contract void growing).

## Step 0 — Materialize the pipeline artifacts (first execution action)
- `.omx/context/grocery-flywheel-redesign-<ts>.md` (context snapshot — content already drafted)
- `.omx/plans/prd-` + `test-spec-` (consensus plan v2 + expanded test plan) and `.omx/state/ralplan-handoff-*.md` (Architect + Critic reviews, gate complete:true)
- Wayfinder map + D1–D4 decision tickets, spec, and tickets 01–10 → **Forgejo issues via `fj issue`** (source of truth; native dependencies as blocking edges; `ready-for-agent` label) + local mirror under `.scratch/v020-redesign/issues/`

## Tickets (dependency order; PR grouping in parens)

- **01 Canonical CI stops ignoring failures** (PR P0) — no blockers. Remove `|| true` + `2>/dev/null` output suppression from Forgejo CI; soften README scanning claim until gitleaks lands (09). AC: planted failing test → red Forgejo pipeline; no unenforced README security claim.
- **02 One truth for state — pure refactor** (PR P1a) — blocked by 01. model/ package: typed state contract, THE single consumed_fraction/age_in_days/clamp; shared state IO + render-to-file; argv-injectable mains + entry-point tests; version single-sourced (explicit PROTOCOL_VERSION cover-or-exempt decision). AC: golden dashboards **byte-identical**; precedence unit test (same item, both depletion encodings → same number).
- **03 Wire-or-delete + protocol pins** (PR P1b) — blocked by 02. hourly_value actually read (or promise removed); retailer_profiles consumed or dropped; adapter wired or explicitly parked for 05; fix lexicographic age sort; MCP tests PIN spec-correct notification silence + −32700 (do NOT change behavior — JSON-RPC 2.0).
- **05 Harvest the contract: canonical state + importers** (PR P2.1) — blocked by 03. Content-port contracts/privacy/normalization/importers + tests from `personal/autopilot-wip-2026-05-26`; lenient read, fail-closed write/import; schema bump KEEPING freshness fields + `added_on` presence semantics. AC: `import normalized|csv` end-to-end on example history; dual goldens (legacy unversioned + canonical) gate the PR.
- **06 Harvest the brain: dietary/corrections/objectives/sourcing** (PR P2.2) — blocked by 05. Fail-closed dietary (no evidence → needs_review); corrections alter next-cart ranking; objective-aware substitution; MCP `evaluate_dietary`.
- **07 Harvest the hands: cart plan + dashboard reconciliation** (PR P2.3) — blocked by 05, 06, **D1**. Introduce analysis/ panel registry (ordered (name, compute, render) callables — no plugin machinery) + rendering/ layer HERE; both panel families in chosen aesthetic; consent-gated corrections capture; always `needs_human_approval`, `checkout_available=False` asserted by test; MCP `plan_next_cart`.
- **08 Honest public face: README + docs collapse** (PR P3a) — blocked by 07, **D2**, **D3**. One positioning (personal, open-source, local-first); 30-second quick start with e2e-verified script; docs ~20→~11 via named merge map; scrub Vons/Bustelo/diced-chicken residue; document MCP + skills; link check.
- **09 Trust plumbing** (PR P3b) — blocked by 01, parallel with 08. Gitleaks in BOTH CIs (fake-secret branch → red); delete empty renovate.json; agent-law single copy + pointer AGENTS/CLAUDE/PR-template + guard update; unify checkout pinning.
- **10 Release v0.2.0 + fleet hygiene** (PR P4) — blocked by 08, 09, **D4**. Tag from single-sourced version; verify Forgejo/GitHub 0/0; delete stale branches/worktrees; apply the render_pulses tolerance fix + refresh its clone; codegraph sync; memory update.

**Decision tickets (HITL, no blockers — resolve early):** D1 dashboard aesthetic direction (prototype: main's static vs WIP dark command-center) · D2 design-preview.html keep/retire · D3 quick-start packaging (venv vs pipx-friendly) · D4 schema-vintage sunset policy.

## Verification spine (all phases)
Dual golden dashboards · MCP protocol suite · CLI e2e incl. quick-start script · both CIs blocking + gitleaks green · version single-source grep · docs link check · codegraph sync. Execution: work the frontier one ticket at a time, fresh context per ticket, PR per phase on Forgejo (`fj`), GitHub mirror verified 0/0 at release.