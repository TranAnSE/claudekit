---
name: plan-design-review
argument-hint: "[plan-path]"
user-invocable: true
description: >
  Use when the user wants a UX/visual design review of a written implementation plan with UI components. Activate for keywords like "review the design plan", "design critique", "is the UX right", "check hierarchy", "visual review of the plan", "does this look generic", "avoid AI slop". Reviews a plan doc on 5 dimensions (information hierarchy, visual consistency, state coverage, accessibility, polish vs AI slop), scores 0-10 each, proposes concrete fixes, and applies user-selected fixes. Dispatches the design-reviewer agent.
---

# Plan DESIGN Review

## When to Use

- Plan includes UI components or user-facing screens
- User wants a designer's-eye critique before implementation
- To catch AI-slop patterns and missing states

## When NOT to Use

- Plan has no UI surface
- You want a live visual audit of shipped UI — (future `design-review` skill in Bundle B will cover that)
- You want architecture review — use `plan-eng-review`

---

## Workflow

### Step 1: Resolve the plan path

Same as other plan-reviews: arg > `docs/claudekit/plans/*` > `docs/plans/*` (generic fallback) > `plan.md`. Newest by mtime.

### Step 2: Dispatch the `design-reviewer` agent

Invoke Agent tool with `subagent_type: "design-reviewer"`. Pass plan path + 5 dimensions (information hierarchy, visual consistency, state coverage, accessibility, polish vs AI slop) + output format.

### Step 3: Present the scorecard

Show the returned DESIGN Review markdown verbatim.

### Step 4: Single consolidation gate

`AskUserQuestion` with `Recommended fixes`. Skip if empty.

### Step 5: Apply selected fixes

For each selected fix, use `Edit` on the plan file. Each fix is either:

- `Replace "<old>" with "<new>"` → `Edit` with `old_string=<old>`, `new_string=<new>`
- `In section "<heading>", add: <text>` → `Read` the file, locate the heading, use `Edit` to append `<text>` under it

If a fix is too vague to apply deterministically (fails the concreteness contract), skip it and report to the user as `Unapplied: <reason>`.

### Step 6: Write the review artifact

`docs/claudekit/reviews/<plan-basename>-design-YYYY-MM-DD.md` with Applied/Skipped sections.

---

## Related Skills

- `writing-plans` — Produces the plan
- `plan-ceo-review`, `plan-eng-review`, `plan-devex-review` — Complementary dimensions
- `autoplan` — Runs all four in parallel
- `ui-ux-designer` agent — Generates UI designs (complementary: designer creates, reviewer critiques)
