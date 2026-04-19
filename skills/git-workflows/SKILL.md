---
name: git-workflows
argument-hint: "[commit/ship/pr/changelog]"
description: >
  Use when committing code, creating pull requests, shipping changes, or generating changelogs. Trigger for keywords like "commit", "push", "PR", "pull request", "ship", "merge", "changelog", "release notes", "conventional commits", or any git workflow beyond basic status/diff. Also activate when preparing code for review or automating the commit-to-PR pipeline.
---

# Git Workflows

## When to Use

- Creating commits with conventional commit messages
- Shipping code (commit + review + push + PR)
- Creating pull requests with proper descriptions
- Generating changelogs from commit history
- Preparing code for review or merge

## When NOT to Use

- Basic git operations (status, diff, log) — just run them directly
- Branch management strategy — use `using-git-worktrees`
- Code review content — use `requesting-code-review`

---

## Quick Reference

| Workflow | Reference | Key content |
|----------|-----------|-------------|
| Committing | `references/committing.md` | Conventional commits, message format, pre-commit checks |
| Shipping | `references/shipping.md` | Full ship workflow: review → test → commit → push → PR |
| Pull Requests | `references/pull-requests.md` | PR creation, description templates, gh CLI patterns |
| Changelogs | `references/changelogs.md` | Changelog generation from commits, Keep a Changelog format |

---

## Conventional Commit Format

```
type(scope): subject

body (optional)

footer (optional)
```

| Type | When |
|------|------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code restructuring, no behavior change |
| `test` | Adding or fixing tests |
| `chore` | Maintenance, dependencies, CI |
| `style` | Formatting, whitespace |

### Subject Line Rules

- Max 50 characters, imperative mood ("Add" not "Added"), no trailing period

---

## Ship Workflow

```
1. Pre-ship checks (secrets, debug statements)
2. Self-review (code quality, style)
3. Run tests (full suite, coverage check)
4. Create commit (conventional format)
5. Push to remote
6. Create PR (summary, test plan, checklist)
```

---

## PR Description Template

```markdown
## Summary
- [Change 1]
- [Change 2]

## Test Plan
- [ ] Unit tests pass
- [ ] Manual testing done

## Checklist
- [ ] No breaking changes
- [ ] Tests added/updated
- [ ] Documentation updated
```

---

## Best Practices

1. **Atomic commits** — one logical change per commit, not one file per commit.
2. **Explain why, not what** — the diff shows what changed; the message explains why.
3. **Stage specific files** — prefer `git add <file>` over `git add -A` to avoid committing secrets or unrelated changes.
4. **Reference issues** — include `Closes #123` or `Fixes #456` in footers.
5. **Pre-commit checks** — verify no secrets, debug statements, or commented-out code before committing.
6. **PR descriptions matter** — reviewers read the description before the diff; make it count.

## Common Pitfalls

1. **Committing secrets** — `.env` files, API keys, tokens in staged changes.
2. **Vague commit messages** — "fix stuff", "updates", "WIP" provide no context.
3. **Giant PRs** — 500+ line PRs get rubber-stamped; split into focused chunks.
4. **Amending published commits** — rewriting history others have pulled causes conflicts.
5. **Skipping pre-commit hooks** — `--no-verify` hides real issues.
6. **Force pushing to shared branches** — can destroy teammates' work.

---

## Related Skills

- `requesting-code-review` — Preparing changes for reviewer feedback
- `finishing-a-development-branch` — End-of-branch workflow decisions
- `using-git-worktrees` — Isolated branch management
