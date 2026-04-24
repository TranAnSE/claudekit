---
name: plan-eng-review
argument-hint: "[plan-path]"
user-invocable: true
description: >
  Use when the user wants an architecture/execution review of a written implementation plan. Activate for keywords like "review the architecture", "does this design make sense", "lock in the plan", "engineering review", "architecture review", "audit this plan", "pre-implementation review". Reviews a plan doc on 5 dimensions (data flow, failure modes, edge cases & invariants, test matrix, rollback & migration), scores 0-10 each, proposes concrete fixes, and applies user-selected fixes. Dispatches the eng-reviewer agent for scoring.
---

# Plan ENG Review

## When to Use

- After a plan has been written and before coding starts
- When the user wants a tech-lead-style architecture audit
- When the plan may be missing failure modes, edge cases, or rollback strategy

## When NOT to Use

- No plan file exists — use `writing-plans` first
- You want strategic review — use `plan-ceo-review`
- The code exists and you need diff review — use `requesting-code-review`

---

## Workflow

### Step 1: Resolve the plan path

- If `[plan-path]` argument provided, use it
- Else scan: `docs/claudekit/plans/*.md`, `docs/plans/*.md` (generic fallback), `plan.md` in cwd
- Newest by mtime wins
- None found → stop and tell user to run `/claudekit:writing-plans` first

### Step 2: Dispatch the `eng-reviewer` agent

Invoke the Agent tool with `subagent_type: "eng-reviewer"`. Pass:

- The absolute plan path
- The 5 dimensions (data flow, failure modes, edge cases & invariants, test matrix, rollback & migration)
- The required output format

### Step 3: Present the scorecard

Show the returned ENG Review markdown verbatim.

### Step 4: Single consolidation gate

`AskUserQuestion` with the `Recommended fixes` checklist. Skip if empty.

### Step 5: Apply selected fixes

For each selected fix, use `Edit` on the plan file. Each fix is either:

- `Replace "<old>" with "<new>"` → `Edit` with `old_string=<old>`, `new_string=<new>`
- `In section "<heading>", add: <text>` → `Read` the file, locate the heading, use `Edit` to append `<text>` under it

If a fix is too vague to apply deterministically (fails the concreteness contract), skip it and report to the user as `Unapplied: <reason>`.

### Step 6: Write the review artifact

Save to `docs/claudekit/reviews/<plan-basename>-eng-YYYY-MM-DD.md` with `Applied fixes` and `Skipped fixes` sections.

---

## Output Format

Identical structure to `plan-ceo-review` but with ENG rubric.

---

## Related Skills

- `writing-plans` — Produces the plan this reviews
- `plan-ceo-review` — Strategic review (complementary)
- `plan-design-review` — UX review (complementary)
- `plan-devex-review` — DX review (complementary)
- `autoplan` — Fan-out all four reviews in parallel
- `planner` agent — Often produces the plan this reviews
