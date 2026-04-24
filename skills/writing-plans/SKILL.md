---
name: writing-plans
argument-hint: "[task description]"
user-invocable: true
description: >
  Use when a multi-step implementation task needs to be broken down before coding begins. Activate for keywords like "plan", "break down", "implementation steps", "task list", "how to implement", "write a plan", or when a feature spans multiple files or components. Also trigger when handing off work to another developer, when the user says "let's plan this out", or when a task is complex enough that jumping straight to code would be risky. If in doubt, plan first.
---

# Writing Plans

## When to Use

- After brainstorming/design is complete
- Before starting implementation
- When handing off work to another developer
- For complex features requiring structured approach

## When NOT to Use

- Single-file changes where the path forward is obvious
- Already has a plan to execute -- use `executing-plans` instead
- Exploration or research tasks where the goal is learning, not building

---

## Save Location

Write the plan document to:

```
docs/claudekit/plans/YYYY-MM-DD-<topic>-plan.md
```

Create the `docs/claudekit/plans/` directory if it does not exist. Use today's date and a short, kebab-case topic slug matching the related design doc (if any).

---

## Plan Document Format

### Header Section

```markdown
# Plan: [Feature Name]

**Required Skill**: executing-plans

## Goal
[One sentence describing what will be built]

## Architecture Overview
[2-3 sentences describing the approach]

## Tech Stack
- [Technology 1]
- [Technology 2]
```

### Task Structure (TypeScript)

Each numbered task contains:

```markdown
## Task [N]: [Task Name]

**Files**:
- Create: `path/to/new-file.ts`
- Modify: `path/to/existing-file.ts`
- Test: `path/to/test-file.test.ts`

**Steps**:

1. Write failing test
   ```typescript
   // Exact test code
   ```

2. Verify test fails
   ```bash
   npm test -- --grep "test name"
   # Expected: 1 failing
   ```

3. Implement minimally
   ```typescript
   // Exact implementation code
   ```

4. Verify test passes
   ```bash
   npm test -- --grep "test name"
   # Expected: 1 passing
   ```

5. Commit
   ```bash
   git add .
   git commit -m "feat: add [feature]"
   ```
```

### Task Structure (Python / FastAPI)

```markdown
## Task [N]: [Task Name]

**Files**:
- Create: `src/api/orders.py`
- Create: `src/schemas/order.py`
- Test: `tests/test_orders.py`

**Steps**:

1. Write failing test
   ```python
   import pytest
   from httpx import AsyncClient

   @pytest.mark.anyio
   async def test_create_order_returns_201(client: AsyncClient):
       response = await client.post("/api/orders", json={"item": "widget", "quantity": 2})
       assert response.status_code == 201
       assert response.json()["item"] == "widget"
   ```

2. Verify test fails
   ```bash
   pytest tests/test_orders.py -v
   # Expected: FAILED — 404 (route doesn't exist)
   ```

3. Implement minimally
   ```python
   from fastapi import APIRouter, status
   from pydantic import BaseModel

   router = APIRouter(prefix="/api/orders")

   class CreateOrderRequest(BaseModel):
       item: str
       quantity: int

   @router.post("", status_code=status.HTTP_201_CREATED)
   async def create_order(body: CreateOrderRequest):
       return {"id": "ord_1", "item": body.item, "quantity": body.quantity}
   ```

4. Verify test passes
   ```bash
   pytest tests/test_orders.py -v
   # Expected: 1 passed
   ```

5. Commit
   ```bash
   git add .
   git commit -m "feat: add create order endpoint"
   ```
```

---

## Task Granularity

### Bite-Sized Principle

Each task should be **2-5 minutes** of focused work:
- Write one test
- Implement one function
- Add one validation

### Why Small Tasks?

- Easier to verify correctness
- Natural commit points
- Reduces context switching
- Enables parallel work
- Clearer progress tracking

### Bad vs Good Task Breakdown

```
BAD: "Implement user authentication"

GOOD:
- Task 1: Create User model with email field
- Task 2: Add password hashing to User model
- Task 3: Create login endpoint
- Task 4: Add JWT token generation
- Task 5: Create auth middleware
- Task 6: Add token refresh endpoint
```

---

## Core Requirements

### Exact File Paths Always

Never use vague references:
```
BAD: "Update the user service"
GOOD: "Modify `src/services/user-service.ts`"
```

### Complete Code Samples

Include exact code, not descriptions:
```
BAD: "Add a function that validates email"

GOOD:
```typescript
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}
```
```

### Expected Output Specifications

Always specify expected command results:
```bash
npm test
# Expected output:
# PASS src/services/user.test.ts
#   User validation
#     ✓ validates correct email format (3ms)
#     ✓ rejects invalid email format (1ms)
# 2 passing
```

---

### Stack-Specific Task Commands

| Stack | Test Command | Lint Command | Build Command |
|-------|-------------|-------------|---------------|
| Python/FastAPI | `pytest -v --cov=src` | `ruff check .` | N/A |
| Python/Django | `python manage.py test` | `ruff check .` | N/A |
| TypeScript/NestJS | `npm test` | `npm run lint` | `npm run build` |
| Next.js | `npm test` or `npx vitest run` | `next lint` | `next build` |
| React (Vite) | `npx vitest run` | `npm run lint` | `npm run build` |

---

## Guiding Principles

### DRY (Don't Repeat Yourself)

- Identify patterns before implementation
- Plan for reusable components
- Note shared utilities needed

### YAGNI (You Aren't Gonna Need It)

- Only plan what's required now
- Remove speculative features
- Add complexity when justified

### TDD (Test-Driven Development)

Every task follows:
1. Write failing test
2. Verify it fails
3. Implement minimally
4. Verify it passes
5. Refactor if needed
6. Commit

### Frequent Commits

- Commit after each task
- Clear, descriptive messages
- Atomic changes only

---

## Execution Handoff

After plan is complete, offer two implementation pathways:

### Option 1: Subagent-Driven (Current Session)
```
Use the `executing-plans` skill for automated execution with:
- Fresh agent per task
- Code review between tasks
- Quality gates
```

### Option 2: Parallel Session (Separate Worktree)
```
Developer executes in separate environment:
- Read plan file
- Follow tasks sequentially
- Commit after each task
```

---

## Example Plan Snippet

```markdown
# Plan: Add Email Verification

**Required Skill**: executing-plans

## Goal
Add email verification to user registration flow.

## Architecture Overview
Send verification email on registration, validate token on click,
mark user as verified in database.

## Tech Stack
- Node.js, TypeScript
- PostgreSQL
- SendGrid for email

---

## Task 1: Add verified flag to User model

**Files**:
- Modify: `src/models/user.ts`
- Create: `src/migrations/add-verified-flag.ts`
- Test: `src/models/user.test.ts`

**Steps**:

1. Write failing test
   ```typescript
   describe('User model', () => {
     it('should have verified flag defaulting to false', () => {
       const user = new User({ email: 'test@example.com' });
       expect(user.verified).toBe(false);
     });
   });
   ```

2. Verify test fails
   ```bash
   npm test -- --grep "verified flag"
   # Expected: 1 failing (verified is undefined)
   ```

3. Add verified field to User model
   ```typescript
   // src/models/user.ts
   export class User {
     email: string;
     verified: boolean = false;  // Add this line
     // ...
   }
   ```

4. Verify test passes
   ```bash
   npm test -- --grep "verified flag"
   # Expected: 1 passing
   ```

5. Commit
   ```bash
   git add src/models/user.ts src/models/user.test.ts
   git commit -m "feat(user): add verified flag with false default"
   ```
```

---

## Related Skills

- `brainstorming` -- Use before writing plans when requirements are unclear or need exploration
- `autoplan` -- After the plan is written, run autoplan (or individual plan-*-review skills) to pressure-test it on strategy, architecture, design, and DX before implementation
- `plan-ceo-review`, `plan-eng-review`, `plan-design-review`, `plan-devex-review` -- Individual dimension reviews of a written plan
- `executing-plans` -- Use after writing a plan to execute it with subagent-driven development and review gates
- `test-driven-development` -- Plans follow TDD principles; reference this skill for strict red-green-refactor enforcement
