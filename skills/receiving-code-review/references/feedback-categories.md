# Feedback Categories Reference

How to categorize, prioritize, and respond to code review feedback.

## Category Definitions

### Critical -- Must Fix Before Merge

**Impact**: Security vulnerability, data loss, crash, or correctness failure.

**Examples**:
- SQL injection or XSS vulnerability
- Missing authentication/authorization check
- Data corruption or silent data loss
- Unhandled exception that crashes the service
- Race condition that causes incorrect results
- Breaking change to public API without migration path

**Response**: Fix immediately. No merge until resolved. Thank the reviewer.

**Time**: Address within hours, not days.

### Important -- Should Fix

**Impact**: Logic error, missing edge case, performance issue, or maintainability concern.

**Examples**:
- Missing null/undefined check on a code path that can be reached
- N+1 query that will degrade with data growth
- Missing error handling for a plausible failure mode
- Incorrect business logic for an edge case
- Missing test for a significant code path
- Resource leak (connection, file handle, memory)

**Response**: Fix before merge unless there is a strong reason to defer (document with a ticket if deferring).

**Time**: Address before the next review round.

### Minor -- Fix If Easy

**Impact**: Code style, naming, comments, minor readability.

**Examples**:
- Variable name could be clearer
- Comment is slightly inaccurate
- Could extract a helper function for readability
- Import ordering
- Unnecessary intermediate variable
- Slightly verbose code that could be simplified

**Response**: Fix if the change is quick and low-risk. If fixing would require significant refactoring, note it for a follow-up.

**Time**: Address in the current PR or create a follow-up ticket.

### Subjective -- Discuss and Decide

**Impact**: Architectural preference, design philosophy, style choice where both options are valid.

**Examples**:
- "I would have used a class here instead of functions"
- "I prefer early returns over nested if-else"
- "Consider using pattern X instead of pattern Y"
- "This could also be modeled as an event-driven system"
- Disagreement on level of abstraction

**Response**: Engage in discussion. Consider the merits. Agree on a direction or escalate to team lead. Neither side is necessarily wrong.

**Time**: Resolve within one discussion round if possible.

## Prioritization Matrix

| Category | Merge Blocker? | Default Action | Can Defer? |
|---|---|---|---|
| Critical | Yes | Fix now | No |
| Important | Usually | Fix now or create ticket | With justification |
| Minor | No | Fix if quick | Yes, with follow-up |
| Subjective | No | Discuss | Yes, team decision |

## How to Handle Each Category

### Receiving Critical Feedback

1. Acknowledge the issue immediately
2. Do not be defensive -- this is protecting users
3. Fix and push the update
4. Add a test that would catch the issue
5. Consider if similar issues exist elsewhere

```
> Reviewer: This SQL query uses string interpolation, which is vulnerable to injection.
>
> You: Good catch -- fixed in abc1234. Added parameterized query and a test
> that verifies injection attempts are escaped. Also checked the other
> queries in this module; they all use parameterized queries already.
```

### Receiving Important Feedback

1. Evaluate whether the feedback is correct (verify, don't assume)
2. If correct, fix it
3. If you disagree, explain your reasoning with evidence
4. If deferring, create a ticket and reference it

```
> Reviewer: This will N+1 query when loading orders with items.
>
> You: You're right. Added eager loading with joinedload() in commit def5678.
> Added a test that asserts query count stays constant regardless of item count.
```

### Receiving Minor Feedback

1. Fix quickly if possible
2. If it requires significant refactoring, note it

```
> Reviewer: Consider renaming `data` to `order_summary` for clarity.
>
> You: Renamed in abc9012. Agreed it's clearer.
```

or

```
> Reviewer: This function could be extracted into a utility.
>
> You: Agree, but it's only used here for now. Created PROJ-789 to extract
> it if we need it elsewhere. Keeping it inline for this PR.
```

### Receiving Subjective Feedback

1. Consider the suggestion genuinely
2. Present your reasoning if you disagree
3. Look for objective criteria to decide (performance, testability, consistency with codebase)
4. If no clear winner, defer to existing codebase conventions
5. If still no consensus, the code author decides (or escalate)

```
> Reviewer: I'd prefer a class-based approach here.
>
> You: I considered that. Went with functions because: (1) no shared state
> between operations, (2) matches the pattern in src/services/auth.py,
> (3) easier to test in isolation. Happy to discuss further if you see
> benefits I'm missing.
```

## Handling Disagreements

### Step-by-Step Process

1. **Verify the claim**: Run the test, check the docs, reproduce the scenario. Do not argue from assumption.
2. **Propose an alternative**: If you disagree, suggest what you would do instead and explain why.
3. **Look for objective evidence**: Benchmarks, test results, documentation, or existing patterns in the codebase.
4. **Find common ground**: Often both approaches have merit. Look for a synthesis.
5. **Escalate if stuck**: Bring in a third opinion (tech lead, team discussion). Do not let PRs stall.

### What NOT to Do

- Do not dismiss feedback without investigation
- Do not agree with everything to avoid conflict (performative agreement hides bugs)
- Do not take feedback personally
- Do not let disagreements block merges for days -- timebox the discussion
- Do not relitigate decisions that were already agreed upon by the team

## Feedback Response Checklist

For each piece of feedback received:

- [ ] Read and understand the feedback fully
- [ ] Categorize it (critical / important / minor / subjective)
- [ ] If technical claim: verify it independently (run the code, check docs)
- [ ] Respond with what you did (fixed, deferred with ticket, or discussed)
- [ ] If fixed: reference the commit
- [ ] If deferred: reference the ticket
- [ ] If disagreeing: provide reasoning with evidence

## Quick Reference: Response Templates

**Agreeing and fixing:**
> Fixed in [commit]. Added test to prevent regression.

**Agreeing and deferring:**
> Agreed. Created [TICKET] to address this. Out of scope for this PR.

**Disagreeing with reasoning:**
> Considered this. Went with [approach] because [reason 1], [reason 2]. Here's [evidence]. Open to discussion.

**Asking for clarification:**
> Can you clarify what you mean by [X]? I want to make sure I address the right concern.
