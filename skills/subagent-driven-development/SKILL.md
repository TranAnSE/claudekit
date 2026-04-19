---
name: subagent-driven-development
description: >
  Use when executing implementation plans with independent tasks in the current session. Trigger when 3+ independent tasks exist, when a plan is ready to execute with the Agent tool, or when the user says "use subagents", "dispatch agents", "parallel implementation". Also activate when tasks touch different files/modules with no shared state, making them safe to parallelize via Claude Code's Agent tool.
---

# Subagent-Driven Development

## When to Use

- A written plan exists with 3+ independent tasks
- Tasks touch different files/modules with no shared state
- Each task has a clear verification command (test suite, build)
- You want faster execution through parallelism

## When NOT to Use

- Tasks have sequential dependencies (task B needs task A's output)
- Tasks modify the same files (will cause merge conflicts)
- The codebase is unfamiliar and you need to explore first
- Fewer than 3 tasks (overhead of dispatch isn't worth it)

---

## Task Decomposition

### Identifying independent units

Tasks are independent when they answer **NO** to all three questions:

| Question | If YES → Sequential |
|----------|---------------------|
| Does task B read files that task A writes? | Shared state |
| Does task B import modules that task A creates? | Dependency chain |
| Do both tasks modify the same file? | Merge conflict |

### Good decomposition example

```markdown
## Plan: User Order Feature

### Task 1 — Backend API (independent)
- Files: src/api/orders.py, tests/test_orders.py
- Verify: pytest tests/test_orders.py -v

### Task 2 — Frontend Component (independent)
- Files: src/components/order-form.tsx, src/components/order-form.test.tsx
- Verify: npm test -- --testPathPattern=order-form

### Task 3 — Database Migration (independent)
- Files: migrations/003_create_orders.sql, tests/test_orders_migration.py
- Verify: pytest tests/test_orders_migration.py -v
```

All three tasks touch different files, different test suites, no shared imports.

---

## Subagent Prompt Template

Each subagent prompt must be **self-contained** — the agent has no context from your conversation.

```markdown
## Task
[One-sentence goal]

## Context
- Project: [framework, language, key conventions]
- Architecture: [relevant module structure]
- Related code: [existing patterns to follow — file paths]

## Files to Create/Modify
- [exact file paths]

## Constraints
- [validation rules, error format, naming conventions]
- [test-first: write failing test, then implement]

## Verification
- Run: [exact command]
- Expected: [what success looks like]
```

### Python/FastAPI example prompt

```markdown
## Task
Implement POST /api/orders endpoint with Pydantic validation.

## Context
- Project: FastAPI + SQLAlchemy async + Pydantic v2
- Architecture: src/api/ for routes, src/models/ for SQLAlchemy, src/schemas/ for Pydantic
- Follow pattern in: src/api/users.py (dependency injection, error handling)

## Files to Create/Modify
- src/schemas/order.py (CreateOrderRequest, OrderResponse)
- src/api/orders.py (POST endpoint)
- tests/test_orders.py (test with httpx.AsyncClient)

## Constraints
- Use Depends(get_db) for database session injection
- Return 201 on success, RFC 9457 ProblemDetails on error
- Test-first: write failing test, verify red, implement, verify green

## Verification
- Run: pytest tests/test_orders.py -v
- Expected: all tests pass, no warnings
```

### TypeScript/NestJS example prompt

```markdown
## Task
Implement OrdersModule with CRUD controller and Prisma service.

## Context
- Project: NestJS + Prisma + class-validator
- Architecture: src/<feature>/ modules with controller, service, dto/, entities/
- Follow pattern in: src/users/ (module structure, DTO validation, Prisma injection)

## Files to Create/Modify
- src/orders/orders.module.ts
- src/orders/orders.controller.ts
- src/orders/orders.service.ts
- src/orders/dto/create-order.dto.ts
- src/orders/orders.controller.spec.ts

## Constraints
- Use ValidationPipe with whitelist: true
- PartialType for UpdateOrderDto
- ProblemDetails error format via global exception filter

## Verification
- Run: npm test -- --testPathPattern=orders
- Expected: all tests pass
```

### React/Next.js example prompt

```markdown
## Task
Build OrderForm component with validation and submission.

## Context
- Project: Next.js App Router + shadcn/ui + react-hook-form + Zod
- Architecture: src/components/ for shared, src/app/(routes)/ for pages
- Follow pattern in: src/components/user-form.tsx

## Files to Create/Modify
- src/components/order-form.tsx
- src/components/order-form.test.tsx

## Constraints
- Client component ('use client')
- Zod schema for validation, react-hook-form for state
- shadcn/ui Form, Input, Button components
- Test with Testing Library + vitest

## Verification
- Run: npx vitest run src/components/order-form.test.tsx
- Expected: all tests pass
```

---

## Execution Pattern

### 1. Dispatch all independent tasks

```markdown
Launch Agent 1: Backend task (background)
Launch Agent 2: Frontend task (background)
Launch Agent 3: Database task (background)
```

### 2. Collect and verify results

As each agent completes:
- Read the files it created/modified
- Run its verification command
- Check for quality issues

### 3. Review between tasks

After all agents complete, run a review pass:
- Do the pieces integrate correctly?
- Are there any naming inconsistencies?
- Run the full test suite (not just individual task tests)

### 4. Integration verification

```bash
# Python
pytest -v --cov=src

# TypeScript
npm test && npm run build

# Full stack
pytest -v && npm test && npm run build
```

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Agent task fails verification | Retry once with error context in prompt |
| Agent produces wrong pattern | Fix manually, don't retry |
| 2+ failures on same task | Stop, investigate root cause |
| Merge conflict between agents | Tasks weren't truly independent — fix decomposition |

### Retry prompt template

```markdown
## Task (retry — previous attempt failed)
[Same task as before]

## Previous Error
[Exact error message/test failure output]

## What Went Wrong
[Your analysis of why it failed]

## Additional Context
[Any clarification the agent needs]
```

---

## Related Skills

- `dispatching-parallel-agents` — When to parallelize and how to manage concurrent work
- `executing-plans` — Sequential plan execution with review gates
- `using-git-worktrees` — Give each subagent an isolated workspace
- `writing-plans` — Create plans with proper task decomposition for subagent execution
