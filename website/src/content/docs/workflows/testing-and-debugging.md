---
title: Testing & Debugging
description: How Claude Kit enforces test-driven development, systematic debugging, and verification.
---

# Testing & Debugging

Claude Kit enforces quality through three connected workflows: **TDD for building**, **systematic debugging for fixing**, and **verification before completion**.

## Test-Driven Development

**Triggers on**: "implement", "add feature", "fix bug", "write code", "build"

The TDD skill enforces a strict red-green-refactor cycle for all production code changes:

```
1. Write a failing test     → Run it → Confirm it fails (RED)
2. Write minimal code       → Run it → Confirm it passes (GREEN)
3. Refactor if needed       → Run it → Confirm it still passes
4. Commit
```

### Why TDD by Default?

- Tests document intent, not just behavior
- Catches regressions immediately
- Forces small, focused changes
- Creates natural commit points

### Stack-Specific Commands

| Stack | Test Command | Full Verify |
|-------|-------------|-------------|
| Python/FastAPI | `pytest tests/test_<module>.py -v` | `pytest -v && ruff check .` |
| TypeScript/NestJS | `npm test -- --testPathPattern=<module>` | `npm test && npm run lint && npm run build` |
| Next.js/React | `npx vitest run <file>` | `npm test && next lint && next build` |

## Systematic Debugging

**Triggers on**: "bug", "error", "failing", "broken", "doesn't work", "TypeError", stack traces

The systematic-debugging skill follows a four-phase investigation:

### Phase 1: Observe

Gather evidence before forming hypotheses:
- Read the error message and stack trace
- Reproduce the issue
- Check logs and recent changes

### Phase 2: Hypothesize

Form specific, testable theories:
- "The null check on line 42 doesn't handle the empty array case"
- Not: "Something is wrong with the data"

### Phase 3: Test

Verify each hypothesis systematically:
- Add logging or breakpoints
- Write a test that reproduces the bug
- Isolate the failing component

### Phase 4: Fix

Apply the minimal fix:
- Fix the root cause, not the symptom
- Add a regression test
- Verify the original error is gone

### Root Cause Tracing

**Triggers on**: deep bugs where the error location differs from the bug origin

For bugs that manifest far from their source, the root-cause-tracing skill traces the data flow backward to find where things first went wrong:

```
Error: NullPointerException at OrderService.getTotal()
  ↓ trace backward
OrderService.getTotal() receives null item
  ↓ trace backward
CartService.getItems() returns null for empty cart
  ↓ root cause
CartRepository.findByUserId() returns null instead of []
```

## Verification Before Completion

**Auto-triggers on**: "done", "fixed", "tests pass", "build succeeds"

The verification skill prevents false completion claims. Before saying "done", Claude must:

1. **Run the test suite** and read the output
2. **Run the build** and confirm it succeeds
3. **Check for regressions** in related functionality
4. **Show evidence** — actual command output, not assumptions

### What Gets Caught

```
Without verification:
  "I've fixed the bug" → Actually introduced a new failing test

With verification:
  Run pytest → See 2 failures → Fix both → Run again → All green → "Fixed"
```

## Testing Anti-Patterns

**Triggers on**: "mock", "flaky test", "test passes but bug ships", "false positive"

The testing-anti-patterns skill catches common mistakes:

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Heavy mocking | Tests pass but production breaks | Test real integrations |
| Testing implementation | Tests break on refactor | Test behavior, not internals |
| No edge cases | Happy path works, edge cases crash | Test boundaries and errors |
| Flaky tests | Random failures erode trust | Fix or delete, never ignore |

## Defense in Depth

**Triggers on**: data validation bugs, "it slipped through", bypass scenarios

The defense-in-depth skill adds validation at multiple layers so a single-point failure can't cause data corruption:

```
API layer:      Validate input shape (Pydantic/Zod)
Service layer:  Validate business rules
Database layer: Constraints (NOT NULL, UNIQUE, CHECK)
```

## Supporting Agents

| Agent | Role |
|-------|------|
| `tester` | Run test suites, analyze coverage, validate error handling |
| `debugger` | Investigate bugs, check logs, reproduce issues |
| `security-auditor` | Security-focused code review |

## Related Pages

- [Planning & Building](/claudekit/workflows/planning-and-building/) — Brainstorm, plan, execute
- [Reviewing & Shipping](/claudekit/workflows/reviewing-and-shipping/) — Code review and git workflows
- [Skills Reference](/claudekit/reference/skills/) — All 44 skills
