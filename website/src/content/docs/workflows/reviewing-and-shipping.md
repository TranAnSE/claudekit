---
title: Reviewing & Shipping
description: How Claude Kit handles code review, git workflows, PR creation, and branch management.
---

# Reviewing & Shipping

Claude Kit provides structured workflows for code review, committing, creating PRs, and finishing development branches.

## Code Review

### Requesting Reviews

**Triggers on**: completing features, before PRs, before merging

The requesting-code-review skill prepares code for review with:

- Clear scope of what changed and why
- Areas of concern flagged for reviewers
- Context on architectural decisions

### Receiving Reviews

**Triggers on**: review feedback, PR comments, review rejections

The receiving-code-review skill processes feedback systematically:

1. **Categorize** — Critical vs. important vs. minor
2. **Prioritize** — Fix critical issues first
3. **Implement** — Address feedback with evidence
4. **Re-request** — Summary of changes made

### Review Agents

| Agent | Focus |
|-------|-------|
| `code-reviewer` | Quality, security, performance, maintainability |
| `security-auditor` | OWASP compliance, vulnerability detection |

## Git Workflows

**Triggers on**: "commit", "push", "PR", "ship", "changelog"

The git-workflows skill enforces:

### Conventional Commits

```
type(scope): subject

feat(auth): add JWT token refresh endpoint
fix(cart): handle empty cart total calculation
docs(api): update OpenAPI spec for v2 endpoints
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Branch Naming

```
feature/AUTH-123-jwt-refresh
fix/CART-456-empty-total
hotfix/critical-payment-bug
chore/upgrade-dependencies
```

### PR Creation

Claude Kit generates well-structured PRs:

```markdown
## Summary
- Added JWT token refresh endpoint
- Tokens auto-refresh 5 minutes before expiry

## Test Plan
- [ ] Unit tests for token refresh logic
- [ ] Integration test for refresh endpoint
- [ ] Manual test: login → wait → verify auto-refresh
```

## Finishing a Branch

**Triggers on**: "ship it", "ready to merge", "branch is done", "create a PR"

The finishing-a-development-branch skill runs a completion checklist:

1. **Verify** — All tests pass, build succeeds
2. **Review** — Run final code review
3. **Options** — Present merge strategies:
   - Create PR for team review
   - Merge directly (if authorized)
   - Clean up worktree (if using git worktrees)

## Git Worktrees

**Triggers on**: "worktree", "isolated branch", "parallel branches"

The using-git-worktrees skill creates isolated working copies for:

- Feature work that shouldn't affect the main workspace
- Parallel development on multiple branches
- Safe experimentation without risk to in-progress work

```
main workspace:     d:/project/          (main branch)
feature worktree:   d:/project-feature/  (feature/auth branch)
hotfix worktree:    d:/project-hotfix/   (hotfix/payment branch)
```

## Changelog Generation

The git-workflows skill generates changelogs from conventional commits:

```markdown
## [1.2.0] - 2026-04-19

### Added
- JWT token refresh endpoint (AUTH-123)
- Auto-refresh 5 minutes before expiry

### Fixed
- Empty cart total calculation (CART-456)
```

## Supporting Skills

| Skill | When It Helps |
|-------|---------------|
| `documentation` | Generating/updating docs after code changes |
| `refactoring` | Improving code structure before shipping |
| `writing-concisely` | Token-efficient mode for high-volume review sessions |

## Supporting Agents

| Agent | Role |
|-------|------|
| `git-manager` | Stage, commit, push with conventional commits |
| `code-reviewer` | Comprehensive code review |
| `copywriter` | Release notes, changelogs, PR descriptions |
| `docs-manager` | Keep documentation in sync with code |

## Related Pages

- [Planning & Building](/claudekit/workflows/planning-and-building/) — Brainstorm, plan, execute
- [Testing & Debugging](/claudekit/workflows/testing-and-debugging/) — TDD and debugging workflows
- [Skills Reference](/claudekit/reference/skills/) — All 44 skills
