---
name: plan-ceo-review
argument-hint: "[plan-path]"
user-invocable: true
description: >
  Use when the user wants strategic/scope review of a written implementation plan. Activate for keywords like "review my plan", "think bigger", "is this ambitious enough", "scope review", "strategy review", "expand scope", "10-star product", "what should we build", "is this worth building at this scope". Reviews a plan doc on 5 dimensions (ambition, problem clarity, wedge focus, demand reality, future-fit), scores 0-10 each, proposes concrete fixes, and applies user-selected fixes to the plan. Dispatches the ceo-reviewer agent for scoring.
---

# Plan CEO Review

## When to Use

- After a plan has been written (e.g., by `writing-plans` or `planner` agent)
- Before implementation begins — to pressure-test scope and ambition
- When the user says the plan "feels small" or "might be too narrow"
- When deciding whether to expand, hold, or reduce scope

## When NOT to Use

- No plan file exists yet — use `writing-plans` first
- Plan has already been implemented — use `requesting-code-review` on the code
- You want architecture review — use `plan-eng-review` instead

---

## Workflow

### Step 1: Resolve the plan path

- If `[plan-path]` argument provided, use it
- Else scan (in order): `docs/claudekit/plans/*.md`, `docs/plans/*.md` (generic fallback), `plan.md` in cwd
- If multiple matches, pick the newest by mtime
- If none found, stop and tell the user to run `/claudekit:writing-plans` first

### Step 2: Dispatch the `ceo-reviewer` agent

Invoke the Agent tool with `subagent_type: "ceo-reviewer"`. Pass a prompt containing:

- The absolute plan path
- The 5 dimensions (the agent already knows them, but re-state for grounding)
- The required output format (the markdown block from the agent's spec)

### Step 3: Present the scorecard

Show the returned CEO Review markdown to the user verbatim.

### Step 4: Single consolidation gate

Use `AskUserQuestion` with the `Recommended fixes` checklist from the scorecard. Multi-select. If the list is empty (no dimension scored <6), skip this step and tell the user "Plan scores well on strategy — no fixes recommended."

### Step 5: Apply selected fixes

For each selected fix, use `Edit` on the plan file. Each fix is either:

- `Replace "<old>" with "<new>"` → `Edit` with `old_string=<old>`, `new_string=<new>`
- `In section "<heading>", add: <text>` → `Read` the file, locate the heading, use `Edit` to append `<text>` under it

If a fix is too vague to apply deterministically (fails the concreteness contract), skip it and report it to the user as `Unapplied: <reason>`.

### Step 6: Write the review artifact

Write a copy of the CEO Review to `docs/claudekit/reviews/<plan-basename>-ceo-YYYY-MM-DD.md`. Create the directory if needed. Include an `Applied fixes` and `Skipped fixes` section at the bottom.

---

## Output Format (what the user sees)

```
# CEO Review: <plan-basename>
Overall: N.N/10

[scorecard table]
[critical issues]
[strengths]

> Please select which fixes to apply:
> [AskUserQuestion multi-select]

Applied N fixes to <plan-path>.
Skipped M fixes (reason: too vague / no match).
Review artifact saved: docs/claudekit/reviews/...
```

---

## Related Skills

- `writing-plans` — Produces the plan doc this skill reviews
- `plan-eng-review` — Architecture review (complementary dimension)
- `plan-design-review` — UX/visual review (complementary)
- `plan-devex-review` — DX review (complementary)
- `autoplan` — Runs this skill + the other three plan-reviews in parallel
