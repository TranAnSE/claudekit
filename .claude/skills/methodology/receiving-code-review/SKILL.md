---
name: receiving-code-review
description: >
  Trigger this skill whenever code review feedback is received, whether from human reviewers, automated tools, or PR comments. Use when processing review comments, handling review rejections, iterating on feedback cycles, or deciding how to prioritize critical vs minor issues. Activate aggressively any time review feedback arrives -- categorize, prioritize, fix critical issues first, and re-request review with a clear summary of changes made.
---

# Receiving Code Review

## When to Use

- After receiving review feedback
- Processing automated review results
- Handling reviewer comments on PRs
- Iterating after code review rejection

## When NOT to Use

- Self-review of your own code where an independent perspective is what you actually need
- Initial implementation before any review has been requested or received
- Design or brainstorming phase where feedback is about ideas, not code

---

## Feedback Categories

### Critical Issues

**Definition**: Must fix before proceeding. Security vulnerabilities, data loss risks, broken functionality.

```markdown
Examples:
- SQL injection vulnerability
- Unhandled null pointer
- Data corruption possibility
- Authentication bypass
```

**Response**: Fix immediately. Do not proceed until resolved.

### Important Issues

**Definition**: Should fix before proceeding. Code quality, maintainability, potential bugs.

```markdown
Examples:
- Missing error handling
- Inefficient algorithm
- Poor naming
- Missing tests for edge cases
```

**Response**: Fix before merging. May defer to follow-up if blocking.

### Minor Issues

**Definition**: Can fix later. Style preferences, optional improvements.

```markdown
Examples:
- Variable naming suggestions
- Comment improvements
- Minor refactoring opportunities
- Documentation polish
```

**Response**: Note for later. Can merge without addressing.

---

## Processing Workflow

### Step 1: Categorize All Feedback

```markdown
## Review Feedback

### Critical (Must Fix)
1. Line 45: SQL query vulnerable to injection
2. Line 89: User data exposed in logs

### Important (Should Fix)
1. Line 23: Missing null check
2. Line 67: Test doesn't cover error path

### Minor (Can Defer)
1. Line 12: Consider renaming 'x' to 'count'
2. Line 34: Could extract to helper function
```

### Step 2: Fix Critical Issues First

```markdown
Addressing critical issue 1:
- File: src/db/queries.ts:45
- Issue: SQL injection vulnerability
- Fix: Use parameterized query
- Verification: Tested with malicious input
```

### Step 3: Fix Important Issues

```markdown
Addressing important issue 1:
- File: src/services/user.ts:23
- Issue: Missing null check
- Fix: Added guard clause
- Verification: Test added for null case
```

### Step 4: Note Minor Issues

```markdown
Deferred for follow-up:
- Line 12: Variable rename (tracked in TODO)
- Line 34: Extract helper (low priority)
```

### Step 5: Request Re-Review

After fixes applied, request re-review with:

```markdown
## Re-Review Request

### Fixed Issues
- [x] SQL injection (line 45) - Now uses parameterized query
- [x] Data exposure (line 89) - Removed user data from logs
- [x] Null check (line 23) - Added guard clause
- [x] Test coverage (line 67) - Added error path test

### Deferred (Minor)
- Variable rename (line 12) - Will address in cleanup PR

### Changes Since Last Review
- 4 files modified
- 2 tests added
- All previous feedback addressed
```

---

## Handling Disagreements

### When You Disagree with Feedback

```markdown
1. Don't dismiss immediately
2. Consider the reviewer's perspective
3. Explain your reasoning
4. Provide evidence (code, tests, docs)
5. Be open to being wrong
6. Escalate if needed (tech lead, team discussion)
```

### Disagreement Response Template

```markdown
## Re: [Feedback item]

I considered this feedback carefully. Here's my perspective:

**Reviewer's concern**: [Their point]

**My reasoning**: [Why I did it this way]

**Evidence**: [Tests, benchmarks, docs supporting approach]

**Proposed resolution**: [Accept, discuss, or defer]
```

---

## Common Feedback Types

### Security Issues

Always fix immediately:

```typescript
// Before (vulnerable)
const query = `SELECT * FROM users WHERE id = '${userId}'`;

// After (secure)
const query = 'SELECT * FROM users WHERE id = $1';
const result = await db.query(query, [userId]);
```

### Error Handling

Add comprehensive handling:

```typescript
// Before
const user = await getUser(id);
return user.name;

// After
const user = await getUser(id);
if (!user) {
  throw new NotFoundError(`User ${id} not found`);
}
return user.name;
```

### Test Coverage

Add missing tests:

```typescript
// Before: Only happy path tested
it('should return user', async () => {
  const user = await getUser('valid-id');
  expect(user).toBeDefined();
});

// After: Edge cases covered
it('should return user', async () => { /* ... */ });
it('should throw NotFoundError for missing user', async () => { /* ... */ });
it('should throw ValidationError for invalid id', async () => { /* ... */ });
```

### Performance

Address efficiency concerns:

```typescript
// Before (N+1 query)
const users = await getUsers();
for (const user of users) {
  user.orders = await getOrders(user.id);
}

// After (batch query)
const users = await getUsers();
const userIds = users.map(u => u.id);
const ordersByUser = await getOrdersForUsers(userIds);
users.forEach(u => u.orders = ordersByUser[u.id]);
```

---

## Re-Review Checklist

Before requesting re-review:

- [ ] All Critical issues fixed
- [ ] All Important issues fixed (or explicitly deferred with reason)
- [ ] Minor issues noted for follow-up
- [ ] Tests added/updated for fixes
- [ ] Full test suite passes
- [ ] Changes summarized for reviewer

---

## Iteration Limits

```markdown
If review requires 3+ cycles:
1. STOP
2. Schedule discussion with reviewer
3. Identify root cause of misalignment
4. May need design discussion
5. Don't keep iterating endlessly
```

---

## Related Skills

- `methodology/requesting-code-review` - Companion skill for initiating reviews with proper context before feedback is received
- `methodology/systematic-debugging` - Use systematic debugging techniques when review feedback reveals bugs that need investigation
- `methodology/verification-before-completion` - After addressing review feedback, verify all fixes before claiming completion
