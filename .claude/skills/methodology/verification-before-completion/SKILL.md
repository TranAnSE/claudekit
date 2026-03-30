---
name: verification-before-completion
description: >
  Trigger this skill whenever about to claim ANY work is complete, fixed, passing, or done. Activate whenever you are tempted to say "done", "fixed", "tests pass", "build succeeds", "deployed", or any completion claim. Also trigger before committing code, before creating PRs, before responding to the user that a task is finished, or when reviewing agent-produced work. This is mandatory -- NEVER claim completion without running verification commands and reading their output. Evidence before assertions, always.
---

# Verification Before Completion

## When to Use

- Before claiming tests pass
- Before claiming build succeeds
- Before claiming bug is fixed
- Before marking any task complete
- Before declaring success to user

## When NOT to Use

- Mid-task progress updates where you are reporting interim status, not claiming completion
- Research or exploration tasks where the output is knowledge, not code
- Design or brainstorming phases where no verifiable artifacts have been produced yet

---

## The 5-Step Verification Process

### Step 1: IDENTIFY

Determine the command that proves your assertion:

```markdown
Claim: "Tests pass"
Verification command: npm test

Claim: "Build succeeds"
Verification command: npm run build

Claim: "Linting passes"
Verification command: npm run lint
```

### Step 2: EXECUTE

Run the command fully and freshly:

```bash
# Don't rely on cached results
# Don't assume previous run is still valid
npm test
```

### Step 3: READ

Read the complete output and exit codes:

```bash
# Check output carefully
# Don't skim - read every line
# Note exit code (0 = success)
```

### Step 4: VERIFY

Confirm the output matches your claim:

```markdown
Claim: "All tests pass"
Output shows: "42 passing, 0 failing"
Verification: ✓ Claim is accurate
```

### Step 5: CLAIM

Only now make the claim, with evidence:

```markdown
✓ All tests pass (42 passing, verified at 2024-01-15 14:30)
```

---

## Required Validations by Category

### Testing

```bash
# Run test command
npm test

# Verify in output:
# - Zero failures
# - Expected test count
# - No skipped tests (unless intentional)
```

**Not valid**: "Tests should pass" without running them

### Linting

```bash
# Run linter completely
npm run lint

# Verify in output:
# - Zero errors
# - Zero warnings (or acceptable known warnings)
```

**Not valid**: Using lint as proxy for build success

### Building

```bash
# Run build command
npm run build

# Verify:
# - Exit code 0
# - Build artifacts created
# - No errors in output
```

**Not valid**: Assuming lint passing means build passes

### Bug Fixes

```bash
# Step 1: Reproduce original bug
npm test -- --grep "failing test"
# Should fail

# Step 2: Apply fix

# Step 3: Verify fix works
npm test -- --grep "failing test"
# Should pass
```

**Not valid**: Claiming fix works without reproducing original failure

### Regression Tests

Complete red-green cycle required:

```bash
# 1. Write test, run it
npm test  # Should PASS with new test

# 2. Revert the fix
git stash

# 3. Run test again
npm test  # Should FAIL (proves test catches the bug)

# 4. Restore fix
git stash pop

# 5. Run test again
npm test  # Should PASS
```

### Requirements Verification

```markdown
## Original Requirements
1. User can login with email
2. User can reset password
3. Session expires after 24 hours

## Verification Checklist
- [x] Requirement 1: Tested login flow manually + unit tests
- [x] Requirement 2: Tested reset flow manually + integration test
- [x] Requirement 3: Verified SESSION_TIMEOUT=86400 in config + test
```

### Agent Work Verification

Don't trust agent reports blindly:

```bash
# Agent claims: "Fixed the bug in user.ts"

# Verify independently:
git diff src/user.ts  # Check actual changes
npm test              # Verify tests pass
```

---

## Forbidden Language

Never use these phrases without verification:

| Forbidden | Why |
|-----------|-----|
| "should work" | Implies uncertainty |
| "probably fixed" | Not verified |
| "seems to pass" | Didn't read output |
| "I think it's done" | Guessing |
| "Great!" (before checking) | Premature celebration |
| "Done!" (before verification) | Unverified claim |

### Replace With

| Instead Say | After |
|-------------|-------|
| "Tests pass" | Running tests, seeing 0 failures |
| "Build succeeds" | Running build, exit code 0 |
| "Bug is fixed" | Reproducing bug, verifying fix |

---

## Anti-Patterns

### Partial Verification

```markdown
BAD: "I ran one test and it passed"
GOOD: "Full test suite passes (42/42)"
```

### Relying on Prior Runs

```markdown
BAD: "Tests passed earlier"
GOOD: "Tests pass now (just ran)"
```

### Skipping Verification

```markdown
BAD: "This is a small change, no need to verify"
GOOD: "Small change, but verified: tests pass, lint clean"
```

### Trusting Without Checking

```markdown
BAD: Agent said it's fixed, so it's fixed
GOOD: Agent said it's fixed, I verified by running tests
```

---

## Verification Checklist Template

Use before claiming completion:

```markdown
## Task: [Task Name]

### Verification Steps
- [ ] Tests run: `npm test`
  - Result: [X passing, Y failing]
- [ ] Lint passes: `npm run lint`
  - Result: [No errors]
- [ ] Build succeeds: `npm run build`
  - Result: [Exit code 0]
- [ ] Requirements met:
  - [ ] Requirement 1: [How verified]
  - [ ] Requirement 2: [How verified]

### Evidence
[Paste relevant output or screenshots]

### Conclusion
✓ Task complete, all verifications passed
```

---

## Related Skills

- `methodology/test-driven-development` -- TDD naturally produces verifiable work; verification confirms the TDD cycle was followed correctly
- `methodology/systematic-debugging` -- After debugging, verification ensures the fix actually resolves the issue
- `methodology/requesting-code-review` -- Verification should happen before requesting review to avoid wasting reviewer time on broken code
