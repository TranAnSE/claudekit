# Pull Request Patterns

## Pre-PR Checklist

- [ ] All tests passing
- [ ] Code self-reviewed
- [ ] No merge conflicts with base branch
- [ ] Branch pushed to remote
- [ ] Commit history is clean (no "WIP" or "fix typo" noise)

## Creating a PR

```bash
# Check current state
git status
git diff main...HEAD
git log --oneline main..HEAD

# Push if needed
git push -u origin $(git branch --show-current)

# Create PR
gh pr create --title "feat(scope): description" --body "$(cat <<'EOF'
## Summary
- [Change 1]
- [Change 2]

## Test Plan
- [ ] Unit tests added
- [ ] Manual testing done
- [ ] Edge cases covered

## Checklist
- [ ] No breaking changes
- [ ] Tests added/updated
- [ ] Documentation updated

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

## PR Title Format

Follow conventional commits: `type(scope): description`

- Max 70 characters
- Use description/body for details, not the title

## PR Size Guidelines

| Size | Lines Changed | Review Time |
|------|--------------|-------------|
| Small | < 100 | Quick review |
| Medium | 100-300 | Thorough review |
| Large | 300-500 | Split if possible |
| Too Large | > 500 | Must split |

## Viewing PR Comments

```bash
# View PR comments
gh api repos/owner/repo/pulls/123/comments

# View PR review comments
gh pr view 123 --comments
```

## Draft PRs

```bash
# Create as draft for early feedback
gh pr create --draft --title "WIP: feature" --body "Early draft for feedback"

# Mark ready when done
gh pr ready 123
```
