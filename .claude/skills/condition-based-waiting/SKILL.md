---
name: condition-based-waiting
user-invocable: false
description: >
  Use when waiting on external conditions like CI pipeline runs, deployments, long builds, database migrations, or test suites. Trigger for keywords like "wait for", "check status", "poll", "monitor", "is it done", "build running", "deploy in progress", or when a background process needs to complete before the next step. Also activate when using run_in_background or Monitor tools in Claude Code.
---

# Condition-Based Waiting

## When to Use

- CI/CD pipeline is running and you need results before proceeding
- Deployment is in progress and you need to verify it succeeded
- Long-running build (Next.js, Docker) is executing
- Database migration is applying
- Test suite takes more than 30 seconds

## When NOT to Use

- Commands that complete in under 10 seconds (just run them normally)
- Checking static state that won't change (read the file instead)
- Polling for human action (ask the user instead)

---

## Claude Code Patterns

### Background execution for long commands

Use `run_in_background` when a command takes more than ~30 seconds:

```bash
# Long test suite — run in background, get notified when done
pytest -v --cov=src                    # run_in_background: true

# Docker build
docker build -t myapp .                # run_in_background: true

# Next.js production build
next build                             # run_in_background: true

# NestJS build + test
npm run build && npm test              # run_in_background: true
```

You'll be notified automatically when the command completes — **do not poll or sleep**.

### Monitor tool for streaming output

Use Monitor when you need to watch for specific output patterns:

```bash
# Watch for build completion
until curl -sf http://localhost:3000/health; do sleep 2; done

# Watch for migration completion
until alembic check 2>&1 | grep -q "No new upgrade"; do sleep 5; done
```

---

## Checking CI/CD Status

### GitHub Actions

```bash
# Watch a running workflow (blocks until complete)
gh run watch

# Check status of the latest run
gh run view --json status,conclusion

# Check specific workflow
gh run list --workflow=ci.yml --limit=1 --json status,conclusion

# Wait for all checks on a PR
gh pr checks --watch
```

### After CI completes

```bash
# Get detailed results
gh run view <run-id> --log-failed

# Re-run failed jobs only
gh run rerun <run-id> --failed
```

---

## Checking Deployments

### Health check polling

```bash
# Wait for deployment to be healthy
until curl -sf https://staging.example.com/health | grep -q '"status":"ok"'; do
  sleep 5
done
echo "Deployment is healthy"
```

### Vercel / Cloudflare

```bash
# Vercel — check latest deployment status
npx vercel ls --limit=1

# Cloudflare Pages — check deployment
npx wrangler pages deployment list --project-name=myapp
```

---

## Checking Build Output

### Framework-specific patterns

```bash
# Next.js — watch for "Compiled successfully"
# (use run_in_background for `next build`, read output when notified)

# Python — watch for test results
pytest -v --tb=short    # run_in_background: true

# Docker — watch for "Successfully built"
docker build -t myapp . # run_in_background: true
```

### Database migrations

```bash
# Alembic (Python)
alembic upgrade head    # run_in_background: true for large migrations

# Prisma (TypeScript)
npx prisma migrate deploy  # run_in_background: true

# Verify migration status
alembic check              # Python
npx prisma migrate status  # TypeScript
```

---

## Anti-Patterns

### Don't: Sleep loops

```bash
# BAD — burns cache, wastes tokens
sleep 60 && check_status
sleep 60 && check_status
sleep 60 && check_status

# GOOD — use run_in_background or until-loop with Monitor
```

### Don't: Poll too frequently

```bash
# BAD — checking every second
while true; do curl localhost:3000/health; sleep 1; done

# GOOD — reasonable interval based on expected duration
until curl -sf localhost:3000/health; do sleep 5; done
```

### Don't: Wait without timeouts

```bash
# BAD — waits forever
until curl -sf localhost:3000/health; do sleep 5; done

# GOOD — timeout after 5 minutes
timeout 300 bash -c 'until curl -sf localhost:3000/health; do sleep 5; done'
```

### Don't: Guess completion

```markdown
BAD: "The build probably finished by now, let's proceed"
GOOD: "Let me check the build status before proceeding"
```

---

## Timing Guide

| Operation | Expected Duration | Check Interval | Approach |
|-----------|------------------|----------------|----------|
| Unit tests (small) | 5-30s | N/A | Run inline |
| Unit tests (large) | 30s-5m | N/A | `run_in_background` |
| `next build` | 30s-3m | N/A | `run_in_background` |
| Docker build | 1-10m | N/A | `run_in_background` |
| CI pipeline | 2-15m | 30s | `gh run watch` |
| Deployment | 1-10m | 5s | Health check poll |
| DB migration (small) | 5-30s | N/A | Run inline |
| DB migration (large) | 1-30m | N/A | `run_in_background` |

---

## Related Skills

- `verification-before-completion` — After waiting, verify the result before claiming success
- `github-actions` — CI/CD workflow patterns
- `docker` — Container build patterns
- `systematic-debugging` — When the thing you're waiting for fails
