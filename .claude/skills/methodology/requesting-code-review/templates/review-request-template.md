# Review Request Template

Use this template when requesting code review. Copy the structure below and fill in each section. Remove sections that are not applicable, but err on the side of including more context.

---

## Review Request

### Summary

_One to three sentences describing the change at a high level. What does this change do and why?_

**Type**: `feature` | `bugfix` | `refactor` | `performance` | `security` | `chore`

**Ticket/Issue**: [Link or ID]

**Branch**: `feature/TICKET-123-description` -> `main`

---

### Changes Made

_List the key changes. Group by area if touching multiple parts of the codebase._

**Core changes:**
- [ ] Changed X in `src/path/to/file.py` to support Y
- [ ] Added new endpoint `POST /api/resource` in `src/api/routes.py`
- [ ] Updated database schema: added `column_name` to `table_name`

**Supporting changes:**
- [ ] Added migration `migrations/0042_add_column.py`
- [ ] Updated config for new feature flag `ENABLE_FEATURE_X`

**Files changed:** _N files, +X/-Y lines_ (or let the PR tool calculate)

---

### Testing Done

_Describe what testing was performed. Be specific._

- [ ] Unit tests added/updated: `tests/test_feature.py`
- [ ] Integration tests added/updated: `tests/integration/test_api.py`
- [ ] Manual testing steps:
  1. Step one
  2. Step two
  3. Expected result
- [ ] Edge cases tested:
  - Empty input
  - Maximum size input
  - Unauthorized user
  - Concurrent requests
- [ ] All existing tests pass: `pytest -v` / `pnpm test`

---

### Areas of Concern

_Be honest about parts you are unsure about. This helps reviewers focus._

- [ ] The caching logic in `src/services/cache.py` lines 42-67 may have race conditions under high concurrency
- [ ] Not sure if the error handling in `handleTimeout()` covers all edge cases
- [ ] Performance impact of the new query has not been benchmarked
- [ ] _None -- I am confident in this change_

---

### Reviewer Focus Areas

_Tell the reviewer where to spend their time. Rank by priority._

1. **Security**: Authentication logic in `src/auth/middleware.py` -- does the token validation cover all cases?
2. **Correctness**: State machine transitions in `src/services/order.py` -- are all transitions valid?
3. **Performance**: New database query in `src/repos/order_repo.py` -- is it using the right index?
4. **Design**: Is the service layer abstraction appropriate, or should this be split?

---

### How to Test Locally

_Step-by-step instructions so the reviewer can verify the change._

```bash
# 1. Set up environment
git checkout feature/TICKET-123-description
pip install -r requirements.txt  # or: pnpm install

# 2. Run migrations (if applicable)
python manage.py migrate  # or: pnpm db:migrate

# 3. Set required environment variables (if applicable)
export FEATURE_X_ENABLED=true

# 4. Run the application
python -m uvicorn main:app --reload  # or: pnpm dev

# 5. Test the change
curl -X POST http://localhost:8000/api/resource \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
# Expected: 201 Created with response body { "id": "...", "key": "value" }

# 6. Run tests
pytest tests/ -v  # or: pnpm test
```

---

### Additional Context

_Optional. Screenshots, diagrams, links to design docs, related PRs, or anything else that helps the reviewer._

- Design doc: [link]
- Related PR: #42
- Screenshot of UI change: [attached]
- Before/after performance metrics: [data]

---

## Quick Version (For Small Changes)

For small, low-risk changes, use this abbreviated format:

```
## Review Request
**Summary**: Fix off-by-one in pagination (returns N+1 results instead of N)
**Ticket**: PROJ-456
**Changes**: `src/api/pagination.py` line 23: `< limit` changed to `<= limit`
**Tests**: Updated `tests/test_pagination.py`, all pass
**Risk**: Low -- single line change, well-covered by tests
```

---

## Checklist Before Submitting

- [ ] Self-reviewed the diff (read your own PR as if you were the reviewer)
- [ ] Tests added for new behavior
- [ ] No TODO/FIXME/HACK comments left without a ticket reference
- [ ] No debugging artifacts (print statements, console.log, commented-out code)
- [ ] Documentation updated (if user-facing behavior changed)
- [ ] Migration is reversible (if schema changed)
- [ ] No secrets in the diff
