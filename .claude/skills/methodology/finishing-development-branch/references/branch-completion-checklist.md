# Branch Completion Checklist

Checklist and reference for completing a development branch and integrating work.

## Pre-Merge Checklist

### Code Quality

- [ ] All tests pass on the branch (`pytest -v` / `pnpm test`)
- [ ] No linting errors (`ruff check` / `eslint .`)
- [ ] Type checking passes (`mypy` / `tsc --noEmit`)
- [ ] No TODO/FIXME without a ticket reference
- [ ] No debugging artifacts (print statements, console.log, commented-out code)
- [ ] No hardcoded secrets, API keys, or credentials

### Review

- [ ] Code review requested and approved
- [ ] All review comments addressed (fixed, deferred with ticket, or discussed)
- [ ] No unresolved conversations in the PR

### Testing

- [ ] Unit tests added for new behavior
- [ ] Integration tests added for new endpoints/services
- [ ] Edge cases covered (empty input, max size, unauthorized, concurrent)
- [ ] Test coverage meets minimum threshold (80% overall, 95% critical paths)
- [ ] Manual testing completed for UI/UX changes

### Documentation

- [ ] Public API documentation updated (docstrings, OpenAPI spec)
- [ ] README updated (if setup steps changed)
- [ ] CHANGELOG entry added (if applicable)
- [ ] Migration guide written (if breaking changes)
- [ ] Architecture/design docs updated (if structural changes)

### Branch Hygiene

- [ ] Branch is up to date with main (rebase or merge)
- [ ] No merge conflicts
- [ ] Commit history is clean and meaningful
- [ ] Branch name follows convention (`feature/`, `fix/`, `hotfix/`, `chore/`)

### CI/CD

- [ ] CI pipeline is green (all checks pass)
- [ ] Build succeeds
- [ ] No new warnings introduced
- [ ] Performance benchmarks pass (if applicable)
- [ ] Security scan passes (if applicable)

### Database/Infrastructure

- [ ] Migrations are reversible
- [ ] Migrations have been tested (up and down)
- [ ] No destructive schema changes without a migration plan
- [ ] Environment variables documented (if new ones added)
- [ ] Feature flags configured (if using progressive rollout)

## Merge Strategy Decision

### Merge Commit (`git merge --no-ff`)

**When to use:**
- Feature branch with multiple meaningful commits
- You want to preserve the full development history
- Team convention requires merge commits

**Result:** Preserves all commits plus a merge commit. Creates a clear merge point in history.

```bash
git checkout main
git merge --no-ff feature/TICKET-123-description
```

### Squash Merge (`git merge --squash`)

**When to use:**
- Feature branch has messy/WIP commits
- The feature is a single logical unit
- You want a clean linear history on main

**Result:** All commits become one commit on main.

```bash
git checkout main
git merge --squash feature/TICKET-123-description
git commit -m "feat(orders): add bulk order cancellation (#123)"
```

### Rebase (`git rebase main` + fast-forward merge)

**When to use:**
- Small number of clean, atomic commits
- You want linear history without merge commits
- Each commit builds on the previous logically

**Result:** Commits are replayed on top of main. No merge commit.

```bash
git checkout feature/TICKET-123-description
git rebase main
git checkout main
git merge --ff-only feature/TICKET-123-description
```

### Decision Matrix

| Situation | Strategy |
|---|---|
| Feature with messy WIP commits | Squash |
| Feature with clean, meaningful commits | Merge commit or rebase |
| Single commit fix | Fast-forward (rebase) |
| Long-lived branch, multiple contributors | Merge commit |
| Team prefers linear history | Squash or rebase |
| Need to bisect individual changes later | Merge commit or rebase (not squash) |

## Update Branch Before Merging

### Option A: Rebase onto main

```bash
git checkout feature/TICKET-123-description
git fetch origin
git rebase origin/main
# Resolve conflicts if any
git push --force-with-lease  # update remote branch
```

**Pros:** Clean linear history.
**Cons:** Rewrites history (don't use if others are working on the branch).

### Option B: Merge main into branch

```bash
git checkout feature/TICKET-123-description
git fetch origin
git merge origin/main
# Resolve conflicts if any
git push
```

**Pros:** Safe, preserves history, works with shared branches.
**Cons:** Adds merge commits to the feature branch.

## Post-Merge Steps

### Immediate

- [ ] Delete the feature branch (local and remote)
  ```bash
  git branch -d feature/TICKET-123-description
  git push origin --delete feature/TICKET-123-description
  ```
- [ ] Verify main branch builds and tests pass
- [ ] Verify deployment to staging/preview environment succeeds

### Follow-Up

- [ ] Close the associated ticket/issue
- [ ] Notify the team (if significant change)
- [ ] Monitor logs and error rates after deployment
- [ ] Verify the feature works in the deployed environment
- [ ] Update project board/tracker

### If Something Goes Wrong

| Problem | Action |
|---|---|
| Tests fail on main after merge | Revert the merge commit immediately, investigate on a new branch |
| Deployment fails | Roll back deployment, investigate, do not push fixes to main under pressure |
| Bug found in production | Create a hotfix branch from main, fix, test, deploy |
| Need to undo a squash merge | `git revert <squash-commit-sha>` |
| Need to undo a merge commit | `git revert -m 1 <merge-commit-sha>` |

## Quick Reference: Common Commands

```bash
# Check if branch is up to date with main
git fetch origin && git log HEAD..origin/main --oneline

# See what will be merged
git log main..HEAD --oneline

# See the full diff against main
git diff main...HEAD

# Check CI status (GitHub CLI)
gh pr checks

# Merge via GitHub CLI
gh pr merge --squash  # or --merge, --rebase

# Delete branch after merge
gh pr merge --squash --delete-branch
```
