---
name: using-git-worktrees
description: >
  Use when starting feature work that needs isolation from the current workspace, before executing implementation plans, or when working on multiple branches simultaneously. Trigger for keywords like "worktree", "isolated branch", "parallel branches", "feature isolation", or when dispatching subagents that need separate working directories. Also activate when the user wants to test against main while developing on a feature branch.
---

# Using Git Worktrees

## When to Use

- Starting feature work that needs isolation from the current workspace
- Executing implementation plans with subagents (one worktree per task)
- Working on multiple branches simultaneously (e.g., hotfix while feature is in progress)
- Testing against main while developing on a feature branch
- Running long builds/tests on one branch while coding on another

## When NOT to Use

- Simple single-branch work with no isolation needs
- Quick fixes that can be done on the current branch
- When the repo has uncommitted changes you haven't stashed (clean up first)

---

## Creating a Worktree

### Basic pattern

```bash
# Create worktree from current branch
git worktree add ../project-feature-auth feature/auth

# Create worktree from a new branch off main
git worktree add -b feature/orders ../project-feature-orders main

# Create worktree for a hotfix off production
git worktree add -b hotfix/session-fix ../project-hotfix-session production
```

### Naming convention

Use `../project-<branch-slug>` to keep worktrees adjacent to the main repo:

```
d:/hop/code/work/
├── myapp/                          # Main worktree
├── myapp-feature-auth/             # Feature worktree
├── myapp-feature-orders/           # Another feature
└── myapp-hotfix-session/           # Hotfix worktree
```

### Safety checks before creating

```bash
# 1. Ensure clean working state
git status  # no uncommitted changes

# 2. Fetch latest from remote
git fetch origin

# 3. Verify the base branch is up to date
git log --oneline origin/main..main  # should be empty

# 4. Create the worktree
git worktree add -b feature/new-feature ../project-feature-new origin/main
```

---

## Working in a Worktree

### Install dependencies (each worktree needs its own)

```bash
# Python
cd ../project-feature-auth
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Node.js
cd ../project-feature-auth
pnpm install
```

### Run tests independently

```bash
# In worktree — won't affect main workspace
cd ../project-feature-auth
pytest -v --cov=src          # Python
npm test                      # TypeScript
```

### Subagent integration

When dispatching subagents for parallel work, each agent gets its own worktree:

```markdown
Agent 1 worktree: ../project-task-1 (branch: task/backend-api)
Agent 2 worktree: ../project-task-2 (branch: task/frontend-ui)
Agent 3 worktree: ../project-task-3 (branch: task/db-migration)
```

Each agent works in isolation — no merge conflicts during development.

---

## Cleanup

### Remove a worktree after merging

```bash
# 1. Switch back to main worktree
cd ../myapp

# 2. Merge the feature branch
git merge feature/auth

# 3. Remove the worktree
git worktree remove ../project-feature-auth

# 4. Delete the branch if no longer needed
git branch -d feature/auth
```

### Prune stale worktrees

```bash
# List all worktrees
git worktree list

# Remove stale references (worktrees whose directories were deleted)
git worktree prune
```

---

## Common Pitfalls

1. **Forgetting to install dependencies.** Each worktree has its own `node_modules` / `venv`. Run `pnpm install` or `pip install -r requirements.txt` after creating.
2. **Stale worktrees.** If you delete a worktree directory manually, run `git worktree prune` to clean up references.
3. **Branch conflicts.** You can't check out the same branch in two worktrees. If you need to, create a new branch off it.
4. **Database state.** Worktrees share the same git history but not local databases. Ensure migrations are applied in each worktree.
5. **IDE confusion.** Open each worktree as a separate project/window in your IDE. Don't mix paths.
6. **Forgetting to clean up.** After merging, always remove the worktree. Stale worktrees waste disk space and create confusion.

---

## Related Skills

- `subagent-driven-development` — Use worktrees to give each subagent an isolated workspace
- `dispatching-parallel-agents` — Dispatch agents into separate worktrees for true parallel work
- `executing-plans` — Worktrees enable isolated task execution from plans
- `finishing-a-development-branch` — Cleanup and merge workflow after worktree work is complete
