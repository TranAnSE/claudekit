---
name: feature-workflow
argument-hint: "[feature description or issue]"
user-invocable: true
description: >
  Use when implementing a complete feature end-to-end — from requirements analysis through planning, implementation, testing, and review. Trigger for keywords like "feature", "implement", "build", "add functionality", "end-to-end", or any task that spans planning through delivery. Also activate when the user provides a feature description, issue reference, or requirement spec that needs a structured development workflow.
---

# Feature Workflow

## When to Use

- Implementing a complete feature from requirements to delivery
- When given a feature description, issue number, or requirement spec
- Multi-phase work that needs planning, implementation, testing, and review
- Any task that benefits from a structured development workflow

## When NOT to Use

- Simple bug fixes — use `systematic-debugging`
- Pure refactoring — use `refactoring`
- Writing tests for existing code — use `testing`
- Already have a plan to execute — use `executing-plans`

---

## Workflow Phases

### Phase 1: Understanding

1. Parse the feature request thoroughly
2. Identify acceptance criteria
3. List assumptions that need validation
4. Clarify ambiguous requirements with the user

### Phase 2: Planning

1. Explore codebase for related implementations and patterns
2. Identify integration points and dependencies
3. Decompose into atomic, verifiable tasks
4. Order tasks by dependencies
5. Track all tasks with TodoWrite
6. (Optional, recommended for non-trivial features) Run `autoplan` on the resulting plan to pressure-test strategy, architecture, design, and DX before Phase 4 (Implementation)

### Phase 3: Research (if needed)

If the feature involves unfamiliar technology:
1. Research best practices and patterns
2. Find examples in the codebase or documentation
3. Identify potential pitfalls

### Phase 4: Implementation

For each task:
1. Write failing test first (TDD)
2. Implement minimally to pass the test
3. Refactor if needed
4. Mark task complete immediately

### Phase 5: Testing

1. Run full test suite — no regressions
2. Verify coverage — should not decrease
3. Test edge cases and error scenarios

```bash
# Python
pytest -v --cov=src

# TypeScript
pnpm test
```

### Phase 6: Review

Self-review checklist:
- [ ] Code follows project conventions
- [ ] No security vulnerabilities
- [ ] Error handling is complete
- [ ] Tests are passing
- [ ] No debug statements or TODOs

### Phase 7: Completion

1. Verify all tasks complete
2. Stage appropriate files
3. Generate commit message
4. Create PR if requested

---

## Output Format

```markdown
## Feature Implementation Complete

### Feature
[Feature description]

### Changes Made
- `path/to/file.ts` — [What was added/modified]
- `path/to/file.test.ts` — [Tests added]

### Tests
- [x] Unit tests passing
- [x] Integration tests passing
- [x] Coverage: XX%

### Ready for Review
```

---

## Best Practices

1. **Break down aggressively** — smaller tasks are easier to verify and commit.
2. **Test first** — every task starts with a failing test.
3. **Commit incrementally** — commit after each task, not at the end.
4. **Clarify before building** — ambiguous requirements lead to rework.
5. **Check existing patterns** — follow conventions already in the codebase.

## Common Pitfalls

1. **Starting without understanding** — jumping to code before clarifying requirements.
2. **Monolithic implementation** — implementing everything in one pass without incremental verification.
3. **Ignoring existing patterns** — building something inconsistent with the rest of the codebase.
4. **Skipping tests** — "I'll add tests later" means no tests.

---

## Related Skills

- `brainstorming` — Use before this skill when requirements are unclear or need exploration
- `writing-plans` — Use for detailed task breakdown when the feature is complex
- `test-driven-development` — The TDD discipline applied during Phase 4
- `git-workflows` — Committing and shipping the completed feature
- `requesting-code-review` — Getting feedback before merging
