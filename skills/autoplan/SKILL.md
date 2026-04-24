---
name: autoplan
argument-hint: "[plan-path]"
user-invocable: true
description: >
  Use when the user wants a full multi-angle review of a written implementation plan — strategy, architecture, UX, and developer experience all at once. Activate for keywords like "autoplan", "auto review", "review everything", "full review", "run all reviews", "auto review this plan", "review from every angle", "run the review gauntlet". Dispatches all 4 reviewer agents (ceo-reviewer, eng-reviewer, design-reviewer, devex-reviewer) in parallel, merges scorecards, and gates all recommended fixes through a single multi-select AskUserQuestion prompt. Applies selected fixes to the plan and saves a consolidated review artifact.
---

# Autoplan (Parallel Plan Review)

## When to Use

- Plan is complex enough to warrant reviews from multiple angles
- User has a plan and wants "the full gauntlet" before implementation
- Before merging a plan to main or handing off to execution

## When NOT to Use

- Plan doesn't exist yet — use `writing-plans` first
- You only need one dimension reviewed — use the individual `plan-*-review` skill
- Plan has been implemented — use `requesting-code-review` or `review` on the code

---

## Workflow

### Step 1: Resolve the plan path

- If `[plan-path]` argument provided, use it
- Else scan (in order): `docs/claudekit/plans/*.md`, `docs/plans/*.md` (generic fallback), `plan.md` in cwd
- Multiple matches → pick newest by mtime
- None found → stop and tell user to run `/claudekit:writing-plans` first

### Step 2: Parallel fan-out

Emit a single assistant message containing four `Agent` tool calls — one per reviewer. They must be in ONE message so they run concurrently. Do NOT emit them sequentially.

For each Agent call, use `subagent_type` matching the reviewer name (`ceo-reviewer`, `eng-reviewer`, `design-reviewer`, `devex-reviewer`). Prompt each with:

- The absolute plan path
- Its dimension rubric (5 dimensions)
- The required output format

### Step 3: Merge the four scorecards

Produce a consolidated report:

```markdown
# Autoplan Review: <plan-basename>
**Date**: YYYY-MM-DD

## Overall Scores
| Reviewer | Overall | Lowest dimension |
|---|---|---|
| CEO | N.N/10 | <dim>: N/10 |
| ENG | N.N/10 | <dim>: N/10 |
| DESIGN | N.N/10 | <dim>: N/10 |
| DEVEX | N.N/10 | <dim>: N/10 |

## Critical Issues (sorted by score ascending — worst first)
| Reviewer | Dimension | Score | Issue | Fix (preview) |
|---|---|---|---|---|
...

## All Strengths
- [CEO] ...
- [ENG] ...
...

## Consolidated Fix Checklist (dedup across reviewers)
- [ ] autoplan-fix-1 — [CEO, DEVEX] "Onboarding not thought through" — In section "Onboarding", add: ...
- [ ] autoplan-fix-2 — [ENG] "No rollback for Phase 2" — In section "Phase 2", add: ...
...
```

**Dedup rule**: if two reviewers flag semantically similar issues (heuristic: same section cited + overlapping fix text), merge into one checklist row with both reviewer tags. Otherwise keep separate.

### Step 4: Single consolidation gate

If the consolidated fix checklist is empty (no dimension across any reviewer scored <6), skip this step entirely. Tell the user: "Plan scores well across all 4 dimensions — no fixes recommended." Still proceed to Step 6 to write the artifact (recording a clean review is useful).

Otherwise, use `AskUserQuestion` with all `autoplan-fix-*` items as multi-select options. One prompt. Include an "Apply none" option.

### Step 5: Apply selected fixes

For each selected fix, use `Edit` on the plan file. Each fix is either:

- `Replace "<old>" with "<new>"` → `Edit` with `old_string=<old>`, `new_string=<new>`
- `In section "<heading>", add: <text>` → `Read` the file, locate the heading, `Edit` to append `<text>` under it

If a fix is too vague to apply deterministically (fails the concreteness contract), skip it and report to the user as `Unapplied: <reason>`.

### Step 6: Write the consolidated artifact

Write the consolidated report (including `Applied fixes` + `Skipped fixes` sections) to `docs/claudekit/reviews/<plan-basename>-autoplan-YYYY-MM-DD.md`. Create the `docs/claudekit/reviews/` directory if it does not exist.

### Step 7: Error handling

- If one of the four agent dispatches fails, proceed with the remaining three and note `[dimension] review unavailable: <reason>` in the merged report.
- If the plan file is empty or unparseable, each reviewer will return `Overall: 0/10` with a single fix "Plan is empty". Surface to user without a fix-selection gate.
- If `Edit` fails on a fix (stale match after concurrent modifications), report as skipped with reason `stale_match`.

---

## Output Format (what the user sees)

```
# Autoplan Review: <plan-basename>
[overall scores table]
[critical issues table]
[strengths]
[consolidated fix checklist]

> Which fixes to apply?
> [AskUserQuestion multi-select + "Apply none" option]

Applied N fixes across <K> dimensions to <plan-path>.
Skipped M fixes (reason: too vague / stale match / agent unavailable).
Artifact: docs/claudekit/reviews/<plan-basename>-autoplan-YYYY-MM-DD.md
```

---

## Related Skills

- `writing-plans` — Produces the plan this reviews
- `plan-ceo-review`, `plan-eng-review`, `plan-design-review`, `plan-devex-review` — Individual dimensions (autoplan runs them in parallel)
- `dispatching-parallel-agents` — The parallel-dispatch pattern this skill uses
- `feature-workflow` — In a full feature workflow, run autoplan between Planning and Implementation phases
