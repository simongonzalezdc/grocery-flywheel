# Empower Orchestrator Agent Law

This repo-local copy keeps the agent operating rule visible to Codex, Claude Code, GitHub reviewers, and CI.

## Rule

Every top-level/orchestrator agent session is an audition to improve the system, not only finish the current task.

If the agent notices a repeatable task done 3+ times or a recurring agent failure mode, it should consider shipping the smallest durable artifact that prevents the repetition.

## Four-Question Blast-Radius Check

Before dispatching automation or creating a durable system change, state the four-question blast-radius check in chat:

1. Scale: one file, one workspace, or many workspaces?
2. Severity: minor friction, broken workflow, data loss, or leaked content?
3. Reversibility: single revert, manual cleanup, or hard surgery?
4. Predictability: bounded failure mode, educated guess, or unknown?

All green permits automatic mode. Any yellow needs inline human approval. Any red means do the work inline or escalate.

## Worker Discipline

- Stay inside assigned scope.
- Do not widen the task without approval.
- Verify before completion claims.
- Return exact commands, files touched, and residual risk.

