# Ship Workflow

Complete workflow: review → test → commit → push → PR.

## Phase 1: Pre-Ship Checks

```bash
git status
git diff --staged
```

Verify:
- [ ] No secrets in staged files
- [ ] No debug statements
- [ ] No commented-out code
- [ ] No unintended files

## Phase 2: Self-Review

- Check code quality and style compliance
- Verify security (no hardcoded secrets, proper input validation)
- Address critical issues before proceeding

## Phase 3: Run Tests

```bash
# Python
pytest -v

# TypeScript
pnpm test
```

- All tests must pass
- Coverage should not decrease
- No new warnings

## Phase 4: Create Commit

```bash
# Stage specific files
git add src/feature.ts src/feature.test.ts

# Commit with conventional format
git commit -m "$(cat <<'EOF'
feat(scope): description

- Change 1
- Change 2

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

## Phase 5: Push and Create PR

```bash
# Push with upstream tracking
git push -u origin feature/my-feature

# Create PR
gh pr create --title "feat(scope): description" --body "$(cat <<'EOF'
## Summary
- Change 1
- Change 2

## Test Plan
- [ ] Unit tests pass
- [ ] Manual testing done

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

## Quick Ship Mode

For small, low-risk changes:
1. Skip detailed self-review
2. Auto-generate commit message from diff
3. Minimal PR description

## Ship Report Format

```markdown
## Ship Complete

### Commit
**Hash**: `abc1234`
**Message**: `feat(auth): add password reset`

### Checks
- [x] Tests passing (42 tests)
- [x] Coverage: 85% (+3%)
- [x] No security issues

### Pull Request
**URL**: https://github.com/org/repo/pull/123
**Status**: Ready for review
```
