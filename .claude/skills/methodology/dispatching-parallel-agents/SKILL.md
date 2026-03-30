---
name: dispatching-parallel-agents
description: >
  Trigger this skill when facing 3 or more independent failures across different domains, when multiple subsystems are broken with no shared state, or when test failures span unrelated modules. Use whenever you see independent bugs in auth, cart, user, or other separate domains that can be fixed concurrently. Activate aggressively for any scenario where parallel work would reduce total resolution time without creating merge conflicts.
---

# Dispatching Parallel Agents

## When to Use

- Multiple subsystems broken independently
- No shared state between failures
- Each fix is self-contained
- Parallel work won't create conflicts

## When NOT to Use

- Tasks with shared state or sequential dependencies where one fix affects another
- Single-file changes that don't benefit from parallelization overhead
- Sequential workflows where each step depends on the output of the previous step

---

## Core Principle

**"Dispatch one agent per independent problem domain. Let them work concurrently."**

### Why Parallel?

- Faster resolution (3 problems in time of 1)
- Focused context per agent
- No context pollution between fixes
- Easy to integrate results

### Why Not Always Parallel?

- Related problems need shared context
- Exploration requires system-wide view
- Conflicting changes cause merge issues
- Some fixes depend on others

---

## Identification Pattern

### Step 1: Group Failures by Domain

```markdown
Test failures:
- src/auth/login.test.ts (3 failures) → Auth domain
- src/cart/checkout.test.ts (2 failures) → Cart domain
- src/user/profile.test.ts (1 failure) → User domain

Each is independent - fixing one doesn't affect others.
```

### Step 2: Verify Independence

```markdown
Ask for each group:
- Does it share state with other groups? NO
- Does fixing it require changes to other groups? NO
- Could fixes conflict with each other? NO

If all NO → Parallel is safe
If any YES → Sequential or combined approach
```

---

## Task Creation Pattern

Each agent receives:

### 1. Specific Scope

```markdown
BAD: "Fix all the tests"
GOOD: "Fix auth/login.test.ts - 3 failing tests"
```

### 2. Clear Goal

```markdown
BAD: "Make it work"
GOOD: "Make all tests in auth/login.test.ts pass"
```

### 3. Constraints

```markdown
- Only modify files in src/auth/
- Don't change the test expectations
- Don't modify shared utilities
```

### 4. Expected Output

```markdown
Return:
- Files modified
- Tests now passing
- Summary of changes
- Any concerns
```

---

## Execution Pattern

### Dispatch Agents Concurrently

```markdown
Agent 1: Fix auth/login.test.ts
Agent 2: Fix cart/checkout.test.ts
Agent 3: Fix user/profile.test.ts

All three run simultaneously.
```

### Monitor Progress

```markdown
While agents working:
- Check for early failures
- Watch for scope violations
- Ready to pause if conflicts detected
```

---

## Integration Pattern

### Step 1: Collect Results

```markdown
Agent 1 returned:
- Modified: src/auth/login-service.ts
- Tests: 3/3 passing
- Summary: Fixed token validation edge case

Agent 2 returned:
- Modified: src/cart/checkout-service.ts
- Tests: 2/2 passing
- Summary: Fixed price calculation rounding

Agent 3 returned:
- Modified: src/user/profile-service.ts
- Tests: 1/1 passing
- Summary: Fixed null handling in profile update
```

### Step 2: Verify No Conflicts

```markdown
Check:
- No overlapping file modifications
- No conflicting changes to shared types
- No incompatible API changes
```

### Step 3: Run Full Test Suite

```bash
npm test
# All tests should pass including:
# - The 6 originally failing tests
# - All other tests (no regressions)
```

### Step 4: Integrate Changes

```bash
# If all agents used branches
git merge agent-1-auth-fixes
git merge agent-2-cart-fixes
git merge agent-3-user-fixes
```

---

## Example Prompts

### Agent Task Prompt Template

```markdown
## Task: Fix [specific test file]

**Scope**: Only modify files in [directory]

**Failing tests**:
1. [test name 1]
2. [test name 2]

**Constraints**:
- Do not modify test expectations
- Do not change shared utilities in src/utils/
- Do not modify types in src/types/

**Goal**: Make all tests in [file] pass

**Return**:
- List of files modified
- Summary of changes made
- Number of tests now passing
- Any concerns about the changes
```

### Result Collection Prompt

```markdown
## Parallel Agent Results

**Agent 1 (Auth)**:
[Paste agent 1 results]

**Agent 2 (Cart)**:
[Paste agent 2 results]

**Agent 3 (User)**:
[Paste agent 3 results]

## Integration Checklist
- [ ] No file conflicts
- [ ] Full test suite passes
- [ ] Changes are isolated to domains
- [ ] Ready to merge
```

---

## Conflict Resolution

If conflicts detected:

```markdown
1. STOP parallel execution
2. Identify conflicting changes
3. Decide which takes priority
4. Continue sequentially from conflict point
5. Learn: Update domain boundaries
```

---

## Checklist

Before parallel dispatch:
- [ ] 3+ independent failures identified
- [ ] Failures grouped by domain
- [ ] Independence verified (no shared state)
- [ ] Scope boundaries clear
- [ ] Conflict potential assessed

After parallel completion:
- [ ] All agent results collected
- [ ] No file conflicts detected
- [ ] Full test suite passes
- [ ] Changes integrated successfully

---

## Related Skills

- `methodology/executing-plans` - Use executing-plans when tasks are sequential; use dispatching-parallel-agents when tasks are independent and can run concurrently
- `methodology/writing-plans` - Write a plan first to identify which tasks are independent before dispatching parallel agents
