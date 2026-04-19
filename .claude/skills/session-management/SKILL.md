---
name: session-management
argument-hint: "[save/list/restore/index/load/status]"
description: >
  Use when managing session state — including saving/restoring checkpoints, generating project structure indexes, loading project components into context, or checking project status. Trigger for keywords like "checkpoint", "save state", "restore", "index", "project structure", "load context", "status", "what's the state", or any request to manage the working session. Also activate when resuming work from a previous session or when needing to understand the current project layout.
---

# Session Management

## When to Use

- Saving or restoring session state (checkpoints)
- Generating project structure indexes
- Loading specific project components into context
- Checking current project status (git, tasks, PRs)
- Resuming work from a previous session

## When NOT to Use

- Git operations (commit, push, PR) — use `git-workflows`
- Branch management — use `using-git-worktrees`
- Launching parallel background work — use `dispatching-parallel-agents`

---

## Quick Reference

| Topic | Reference | Key content |
|-------|-----------|-------------|
| Checkpoints | `references/checkpoints.md` | Save/restore/list/delete session state |
| Project indexing | `references/indexing.md` | Generate PROJECT_INDEX.md, scan structure |
| Context loading | `references/loading.md` | Load components by category or path |
| Status checking | `references/status.md` | Git state, tasks, recent activity |

---

## Checkpoints

Save and restore conversation context using git-based state:

```bash
# Save current state
# → creates git stash + metadata in .claude/checkpoints/
/checkpoint save feature-auth

# List available checkpoints
/checkpoint list

# Restore a checkpoint
/checkpoint restore feature-auth

# Delete old checkpoint
/checkpoint delete old-checkpoint
```

Auto-checkpoint is suggested before major refactoring, context switches, and risky operations.

---

## Project Indexing

Generate a comprehensive project structure index:

```bash
# Generate PROJECT_INDEX.md
/index

# Shallow index (3 levels deep)
/index --depth=3
```

The index categorizes files by type: entry points, API routes, models, services, utilities, tests, and configuration.

---

## Context Loading

Load specific components into context for focused work:

| Category | What It Loads |
|----------|---------------|
| `api` | API routes and endpoints |
| `models` | Data models and types |
| `services` | Business logic services |
| `auth` | Authentication related |
| `db` | Database related |
| `tests` | Test files |
| `config` | Configuration files |

```bash
/load api                    # Load all API routes
/load src/services/user.ts   # Load specific file
/load auth --related         # Load auth + related files
/load --all --shallow        # Quick overview of everything
```

---

## Status

Get current project status:

```bash
/status
```

Shows: git branch and status, in-progress/pending/completed tasks, recent commits, open PRs.

---

## Best Practices

1. **Checkpoint before context switches** — save state when switching tasks.
2. **Index periodically** — regenerate when project structure changes significantly.
3. **Load narrow, expand as needed** — start with specific components, add related files.
4. **Name checkpoints descriptively** — `auth-progress` beats `checkpoint-1`.

---

## Related Skills

- `using-git-worktrees` — Isolated branch management for parallel work
- `dispatching-parallel-agents` — Launching parallel background tasks
