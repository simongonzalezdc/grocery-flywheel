# Worktree Directory

This directory contains isolated git worktrees for parallel development.

## Structure

```
.worktrees/
├── README.md           # This file
├── <feature-name>/     # Feature worktrees
└── agent-<id>/         # Agent-specific worktrees
```

## Rules

1. **One worktree per feature/bugfix** - Keeps branches isolated
2. **Name format:** `<issue-id>-<short-description>` or `agent-<task-id>`
3. **Clean up after merge:**
   ```bash
   git wtr <worktree-name>
   git branch -d <branch-name>
   ```
4. **Never commit this directory** - It's in `.gitignore`

## Quick Commands

| Command | Description |
|---------|-------------|
| `git wt <branch>` | Create and switch to worktree |
| `git wtl` | List all worktrees |
| `git wtc` | Clean up merged worktrees |
| `wt` | Fuzzy-find and switch worktrees |

## Multi-Agent Safety

Each agent operates in their own worktree:
- Agent A: `.worktrees/agent-a7b13158/`
- Agent B: `.worktrees/agent-ab731eb7/`
- No file conflicts, no git conflicts
