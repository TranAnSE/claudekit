# Changelog Generation

## Keep a Changelog Format

Based on [keepachangelog.com](https://keepachangelog.com):

```markdown
## [1.2.0] - 2026-04-19

### Added
- Password reset functionality (#123)
- Email verification for new accounts

### Changed
- Improved error messages for validation failures
- Updated dependencies to latest versions

### Fixed
- Race condition in session handling (#456)
- Incorrect timezone in date displays

### Removed
- Legacy v1 API endpoints (deprecated since 1.0)
```

## Generating from Commits

```bash
# Get commits since last tag
git log --oneline $(git describe --tags --abbrev=0)..HEAD

# Group by type
git log --oneline --grep="^feat" $(git describe --tags --abbrev=0)..HEAD
git log --oneline --grep="^fix" $(git describe --tags --abbrev=0)..HEAD
```

## Category Mapping

| Commit Type | Changelog Category |
|-------------|-------------------|
| `feat` | Added |
| `fix` | Fixed |
| `refactor`, `perf` | Changed |
| removal commits | Removed |
| `docs` | Usually omitted |
| `chore`, `test`, `style` | Usually omitted |

## User-Friendly Descriptions

Transform commit messages into user-facing descriptions:

```
BAD:  feat(auth): add pwd reset (#123)
GOOD: Password reset functionality — users can now reset their password via email (#123)
```

- Write for users, not developers
- Include PR/issue references
- Explain the user-visible impact
