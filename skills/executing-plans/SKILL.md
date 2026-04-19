---
name: executing-plans
description: >
  Use when there is a written implementation plan ready to execute, or when the user says "execute", "run the plan", "implement the plan", "start building", or references a plan file. Also activate when using subagent-driven development with independent tasks, when the user wants automated execution with quality gates, or when picking up a previously written plan. If a plan document exists and no one is executing it yet, this is the skill to use.
---

# Executing Plans

## When to Use

- Executing plans created with `writing-plans` skill
- Staying in current session with independent tasks
- Wanting quality gates without human delays
- Systematic implementation with verification

## When NOT to Use

- No plan exists yet -- use `writing-plans` first to create one
- Single-task work that does not need sequential execution or review gates
- Research or exploration where the goal is learning, not building

---

## Core Pattern

**"Fresh subagent per task + review between tasks = high quality, fast iteration"**

### Why Fresh Agents?

- Prevents context pollution between tasks
- Each task gets focused attention
- Failures don't cascade
- Easier to retry individual tasks

### Why Code Review Between Tasks?

- Catches issues early
- Ensures code matches intent
- Prevents technical debt accumulation
- Creates natural checkpoints

---

## Execution Workflow

### Step 1: Load Plan

```markdown
1. Read the plan file
2. Verify plan is complete and approved
3. Create TodoWrite with all tasks from plan
4. Set first task to in_progress
```

### Step 2: Execute Task

For each task:

```markdown
1. Dispatch fresh subagent with task details
2. Subagent implements following TDD cycle:
   - Write failing test
   - Verify test fails
   - Implement minimally
   - Verify test passes
   - Commit
3. Subagent returns completion summary
```

### Step 3: Code Review

After each task:

```markdown
1. Dispatch code-reviewer subagent
2. Review scope: only changes from current task
3. Reviewer returns findings:
   - Critical: Must fix before proceeding
   - Important: Should fix before proceeding
   - Minor: Can fix later
```

### Step 4: Handle Review Findings

```markdown
IF Critical or Important issues found:
  1. Dispatch fix subagent for each issue
  2. Re-request code review
  3. Repeat until no Critical/Important issues

IF only Minor issues:
  1. Note for later cleanup
  2. Proceed to next task
```

### Step 5: Mark Complete

```markdown
1. Update TodoWrite - mark task completed
2. Move to next task
3. Repeat from Step 2
```

### Step 6: Final Review

After all tasks complete:

```markdown
1. Dispatch comprehensive code review
2. Review entire implementation against plan
3. Verify all success criteria met
4. Run full test suite
5. Use `finishing-a-development-branch` skill
```

---

## Critical Rules

### Never Skip Code Reviews

Every task must be reviewed before proceeding. No exceptions.

### Never Proceed with Critical Issues

Critical issues must be fixed. The pattern is:
```
implement → review → fix critical → re-review → proceed
```

### Never Run Parallel Implementation

Tasks run sequentially:
```
WRONG: Run Task 1, 2, 3 simultaneously
RIGHT: Run Task 1 → Review → Task 2 → Review → Task 3 → Review
```

### Always Read Plan Before Implementing

```
WRONG: Start coding based on memory of plan
RIGHT: Read plan file, extract task details, then implement
```

---

## Subagent Communication

### Implementation Subagent Prompt

```markdown
## Task: [Task Name]

**Context**: Executing plan for [Feature Name]

**Files to modify**:
- [File paths from plan]

**Steps**:
[Exact steps from plan]

**Requirements**:
- Follow TDD: test first, then implement
- Commit after completion
- Return summary of what was done

**Output expected**:
- Files modified
- Tests added
- Commit hash
- Any issues encountered
```

### Stack-Specific Task Prompt Examples

**Python/FastAPI:**

```markdown
## Task: Implement GET /api/users endpoint

**Context**: FastAPI + SQLAlchemy async + Pydantic v2
**Files**: src/api/users.py, tests/test_users.py
**Pattern**: Follow src/api/health.py for router setup

**Steps**:
1. Write test: GET /api/users returns 200 with list
2. Verify test fails (404 — route doesn't exist)
3. Implement: APIRouter, async def, Depends(get_db)
4. Verify test passes
5. Add edge case: GET /api/users/999 returns 404 ProblemDetails

**Verify**: pytest tests/test_users.py -v (all green)
```

**TypeScript/NestJS:**

```markdown
## Task: Implement UsersController with CRUD

**Context**: NestJS + Prisma + class-validator DTOs
**Files**: src/users/users.controller.ts, src/users/users.controller.spec.ts
**Pattern**: Follow src/health/ module structure

**Steps**:
1. Write spec: POST /users returns 201 with user
2. Verify spec fails (404 — no route)
3. Implement: Controller, Service, CreateUserDto with @IsEmail()
4. Verify spec passes
5. Add: GET /users/:id returns 404 for missing user

**Verify**: npm test -- --testPathPattern=users.controller (all green)
```

**React/Next.js:**

```markdown
## Task: Build UserTable with sorting and pagination

**Context**: Next.js App Router + TanStack Table + shadcn/ui
**Files**: src/components/user-table.tsx, src/components/user-table.test.tsx
**Pattern**: Follow src/components/data-table.tsx for column defs

**Steps**:
1. Write test: renders table with user data
2. Verify test fails (component doesn't exist)
3. Implement: columns, DataTable wrapper, sort handlers
4. Verify test passes
5. Add test: clicking column header sorts data

**Verify**: npx vitest run src/components/user-table.test.tsx (all green)
```

### Stack-Specific Verification Commands

| Stack | Test Command | Full Verify |
|-------|-------------|-------------|
| Python/FastAPI | `pytest tests/test_<module>.py -v` | `pytest -v && ruff check . && mypy src/` |
| TypeScript/NestJS | `npm test -- --testPathPattern=<module>` | `npm test && npm run lint && npm run build` |
| Next.js | `npx vitest run <file>` | `npm test && next lint && next build` |

### Code Review Subagent Prompt

```markdown
## Code Review Request

**Scope**: Changes from Task [N]

**Files changed**:
- [List of files]

**Review against**:
- Plan requirements for this task
- Code quality standards
- Security best practices
- Test coverage

**Return**:
- Critical issues (must fix)
- Important issues (should fix)
- Minor issues (can defer)
- Approval status
```

---

## TodoWrite Integration

Maintain task status throughout:

```markdown
| Task | Status |
|------|--------|
| Task 1: Create model | completed |
| Task 2: Add validation | completed |
| Task 3: Create endpoint | in_progress |
| Task 4: Add tests | pending |
| Task 5: Documentation | pending |
```

Update status in real-time:
- `pending` → `in_progress` when starting
- `in_progress` → `completed` when reviewed and approved

---

## Error Handling

### Task Fails

```markdown
1. Capture error details
2. Attempt fix (max 2 retries)
3. If still failing, pause execution
4. Report to user with:
   - Which task failed
   - Error details
   - Suggested resolution
5. Wait for user decision
```

### Review Finds Major Issues

```markdown
1. List all Critical/Important issues
2. Dispatch fix subagent for each
3. Re-run code review
4. If issues persist after 2 cycles:
   - Pause execution
   - Report to user
   - May need plan revision
```

---

## Completion Checklist

Before declaring plan execution complete:

- [ ] All tasks marked completed
- [ ] All code reviews passed
- [ ] Full test suite passes
- [ ] No Critical issues outstanding
- [ ] No Important issues outstanding
- [ ] Final comprehensive review done
- [ ] Ready for `finishing-a-development-branch`

---

## Related Skills

- `writing-plans` -- Use to create the plan before executing it
- `dispatching-parallel-agents` -- For coordinating multiple independent agents when plan tasks allow parallelism
- `verification-before-completion` -- Ensures each task and the final result are properly verified before claiming completion
