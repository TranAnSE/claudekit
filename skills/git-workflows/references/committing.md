# Committing Patterns

## Pre-Commit Checklist

Before staging:
- [ ] No secrets (`.env`, API keys, tokens)
- [ ] No debug statements (`console.log`, `print()`, `debugger`)
- [ ] No commented-out code blocks
- [ ] Code is formatted (prettier/ruff)

## Conventional Commit Format

```
type(scope): subject

body (optional - explain why, not what)

footer (optional - references, breaking changes)
```

### Types

| Type | When | Example |
|------|------|---------|
| `feat` | New feature | `feat(auth): add OAuth2 login` |
| `fix` | Bug fix | `fix(api): handle null user in profile` |
| `docs` | Documentation | `docs(readme): update install steps` |
| `refactor` | Restructure, no behavior change | `refactor(db): extract query builders` |
| `test` | Add/fix tests | `test(auth): add login edge cases` |
| `chore` | Maintenance | `chore(deps): update React to 19` |
| `style` | Formatting | `style: apply prettier` |
| `perf` | Performance | `perf(query): add index on user_id` |

### Subject Line Rules

- Max 50 characters
- Imperative mood: "Add" not "Added" or "Adds"
- No trailing period
- Capitalize first letter

### Body Rules

- Wrap at 72 characters
- Explain **why**, not what (the diff shows what)
- Use bullet points for multiple changes

### Footer Patterns

```
Closes #123
Fixes #456
BREAKING CHANGE: removed legacy auth endpoint
Co-Authored-By: Claude <noreply@anthropic.com>
```

## Staging Best Practices

```bash
# Prefer specific files over blanket add
git add src/auth/login.ts src/auth/login.test.ts

# Review what you're committing
git diff --staged

# Never commit these
# .env, credentials.json, *.pem, *.key
```

## Commit Command Pattern

```bash
git commit -m "$(cat <<'EOF'
feat(auth): add password reset flow

- Add reset token generation with 1h expiry
- Implement email sending via SendGrid
- Add rate limiting (3 requests/hour)

Closes #123

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

## Amending vs New Commit

- **Amend**: Only for unpushed commits, only when fixing the same logical change
- **New commit**: Always for pushed commits, or when adding distinct changes
- **Never amend after pre-commit hook failure** — the commit didn't happen, so amend would modify the previous commit
