# AGENTS.md instructions for simongonzalezdc/grocery-flywheel

<!-- EMPOWER_ORCHESTRATOR:START -->
## Empower the Orchestrator

This repository is governed by the Empower Orchestrator law. Every top-level/orchestrator agent session is an audition to improve the system, not only finish the current task.

When you notice a repeatable task done 3+ times or a recurring agent failure mode, consider shipping the smallest durable artifact that prevents the repetition: a tool, skill, slash command, hook, guardrail, memory entry, test, verifier, or doctrine doc.

Before dispatching automation or creating a durable system change, state the four-question blast-radius check in chat: scale, severity, reversibility, and predictability.

Background workers execute their assigned slice and do not independently widen scope. They must stay inside assigned scope and return verification evidence before completion claims.

Full recipe: `docs/agent-law/empower-orchestrator.md`.
<!-- EMPOWER_ORCHESTRATOR:END -->

