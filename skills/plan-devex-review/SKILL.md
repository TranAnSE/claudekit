---
name: plan-devex-review
argument-hint: "[plan-path]"
user-invocable: true
description: >
  Use when the user wants a developer-experience review of a written implementation plan for APIs, CLIs, SDKs, libraries, or docs. Activate for keywords like "review the DX", "is this SDK ergonomic", "devex review", "API design review", "time to hello world", "how's the CLI". Reviews a plan doc on 5 dimensions (Time to Hello World, API/CLI ergonomics, error copy, docs structure, magical moments), scores 0-10 each, proposes concrete fixes, and applies user-selected fixes. Dispatches the devex-reviewer agent.
---

# Plan DEVEX Review

## When to Use

- Plan ships a developer-facing surface (API, CLI, SDK, library, docs)
- User wants a DX audit before shipping
- To catch ergonomics regressions, unhelpful error messages, or "reads like generated docs"

## When NOT to Use

- Plan has no developer-facing surface (pure internal backend, consumer UI only)
- You want strategic review — use `plan-ceo-review`
- The product is already shipped — (future `devex-review` in Bundle B will cover live DX audit)

---

## Workflow

### Step 1: Resolve the plan path

Same convention: arg > `docs/claudekit/plans/*` > `docs/plans/*` (generic fallback) > `plan.md`. Newest by mtime.

### Step 2: Dispatch the `devex-reviewer` agent

Invoke Agent tool with `subagent_type: "devex-reviewer"`. Pass plan path + 5 dimensions (Time to Hello World, API/CLI ergonomics, error copy, docs structure, magical moments) + output format.

### Step 3: Present the scorecard

Show returned DEVEX Review markdown verbatim.

### Step 4: Single consolidation gate

`AskUserQuestion` with `Recommended fixes`. Skip if empty.

### Step 5: Apply selected fixes

For each selected fix, use `Edit` on the plan file. Each fix is either:

- `Replace "<old>" with "<new>"` → `Edit` with `old_string=<old>`, `new_string=<new>`
- `In section "<heading>", add: <text>` → `Read` the file, locate the heading, use `Edit` to append `<text>` under it

If a fix is too vague to apply deterministically (fails the concreteness contract), skip it and report to the user as `Unapplied: <reason>`.

### Step 6: Write the review artifact

`docs/claudekit/reviews/<plan-basename>-devex-YYYY-MM-DD.md` with Applied/Skipped sections.

---

## Related Skills

- `writing-plans` — Produces the plan
- `plan-ceo-review`, `plan-eng-review`, `plan-design-review` — Complementary
- `autoplan` — Parallel fan-out
- `api-designer` agent — Generates API designs (complementary: designer creates, reviewer critiques)
