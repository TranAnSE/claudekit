---
title: Planning & Building
description: How Claude Kit guides you from idea to implementation using brainstorming, planning, and execution skills.
---

# Planning & Building

Claude Kit provides a structured workflow for turning ideas into working code: **Brainstorm > Plan > Review > Execute > Verify**.

## The Workflow

```
"I need to add user authentication"
        │
        ▼
┌─────────────────┐
│  Brainstorming   │  Explore requirements, ask questions,
│                  │  evaluate approaches, validate design
└────────┬────────┘
         ▼
┌─────────────────┐
│  Writing Plans   │  Break into tasks, exact file paths,
│                  │  code samples, verification steps
└────────┬────────┘
         ▼
┌─────────────────┐
│    Autoplan      │  Parallel 4-angle plan review:
│  (optional but   │  strategy, architecture, design, DX.
│   recommended)   │  Single fix-gate before implementation.
└────────┬────────┘
         ▼
┌─────────────────┐
│ Executing Plans  │  Fresh subagent per task, code review
│                  │  between tasks, quality gates
└────────┬────────┘
         ▼
┌─────────────────┐
│  Verification    │  Run tests, verify builds,
│                  │  evidence before claims
└─────────────────┘
```

## Phase 1: Brainstorming

**Triggers on**: "brainstorm", "design", "explore", "what if", "how should we", "trade-offs"

The brainstorming skill uses a three-phase process:

1. **Understanding** — Asks one question at a time to clarify requirements. Prefers multiple-choice over open-ended questions.
2. **Exploration** — Presents 2-3 approaches with trade-offs, leads with a recommendation.
3. **Design** — Presents the validated design in digestible 200-300 word sections.

### Example

```
You: "Let's brainstorm adding real-time notifications"

Claude: "Which delivery mechanism fits your use case best?
  a) WebSockets — persistent connection, instant delivery
  b) Server-Sent Events — simpler, one-way push
  c) Polling — simplest, but higher latency"

You: "b) SSE"

Claude: "## Approach 1: SSE + Redis Pub/Sub (Recommended)
  Server pushes events via SSE, Redis coordinates across instances.
  - Pros: Simple, works with load balancers, auto-reconnect built in
  - Cons: One-way only (client can't push back)

  ## Approach 2: SSE + PostgreSQL LISTEN/NOTIFY
  ..."
```

## Phase 2: Writing Plans

**Triggers on**: "plan", "break down", "implementation steps", "task list"

The writing-plans skill creates detailed implementation plans with:

- Exact file paths for every change
- Complete code samples (not descriptions)
- Verification commands with expected output
- 2-5 minute task granularity

### Plan Structure

```markdown
## Task 1: Create User model with email field

**Files**:
- Create: `src/models/user.ts`
- Test: `src/models/user.test.ts`

**Steps**:
1. Write failing test
2. Verify test fails
3. Implement minimally
4. Verify test passes
5. Commit
```

## Phase 2.5: Plan Review (Optional but recommended)

**Triggers on**: "autoplan", "auto review", "review my plan", "think bigger", "does this design make sense", "DX review"

Before jumping into execution, pressure-test the plan from four complementary angles. Each reviewer returns a 0-10 scorecard per dimension and proposes concrete fixes. Fixes are presented in a single multi-select prompt — you pick which ones to apply, and they're written directly into the plan file.

| Skill | Dimensions scored | When to invoke |
|-------|------------------|----------------|
| `plan-ceo-review` | Ambition, problem clarity, wedge focus, demand reality, future-fit | Plan scope / strategy pressure-test |
| `plan-eng-review` | Data flow, failure modes, edge cases, test matrix, rollback | Architecture audit before coding |
| `plan-design-review` | Hierarchy, visual consistency, states, accessibility, AI-slop avoidance | Plans with UI surfaces |
| `plan-devex-review` | Time to Hello World, ergonomics, error copy, docs structure, magical moments | Plans shipping APIs / CLIs / SDKs |
| `autoplan` | All 4 above, fanned out in parallel, single consolidated fix gate | Full gauntlet before handoff |

### Example

```
You: "/claudekit:autoplan"

Claude: [dispatches 4 reviewers in parallel]

# Autoplan Review: 2026-04-24-feature-x-plan
Overall Scores:
  CEO:    6.2/10 (lowest: Wedge focus 4/10)
  ENG:    7.8/10 (lowest: Rollback 5/10)
  DESIGN: 8.4/10
  DEVEX:  5.6/10 (lowest: Time to Hello World 3/10)

Critical Issues (worst first):
  [DEVEX] Time to Hello World: no quickstart specified
  [CEO]   Wedge focus: covers 3 personas simultaneously
  [ENG]   Rollback: no undo path for Phase 2 migration
  ...

> Which fixes to apply? [multi-select]
```

## Phase 3: Executing Plans

**Triggers on**: "execute the plan", "run the plan", "implement the plan"

The executing-plans skill runs each task with:

- **Fresh subagent per task** — Prevents context pollution
- **Code review between tasks** — Catches issues early
- **Quality gates** — Critical issues must be fixed before proceeding

### Execution Flow

```
Task 1 → Implement → Review → Fix issues → ✓
Task 2 → Implement → Review → Fix issues → ✓
Task 3 → Implement → Review → Fix issues → ✓
Final comprehensive review → ✓
```

## Phase 4: Verification

**Auto-triggers on**: completion claims ("done", "fixed", "tests pass")

The verification-before-completion skill requires evidence before any completion claim:

- Run the actual test suite and read the output
- Verify the build succeeds
- Check that the feature works as intended

## Supporting Skills

These skills activate automatically during planning and building:

| Skill | When It Helps |
|-------|---------------|
| `feature-workflow` | End-to-end feature development |
| `sequential-thinking` | Complex decisions needing step-by-step reasoning |
| `subagent-driven-development` | Fresh subagent per task with two-stage review |
| `using-git-worktrees` | Isolated branch work for parallel development |
| `dispatching-parallel-agents` | Launching independent parallel agents |
| `refactoring` | Improving code structure before shipping |

## Supporting Agents

| Agent | Role |
|-------|------|
| `planner` | Research and create implementation plans |
| `brainstormer` | Explore solutions and evaluate trade-offs |
| `researcher` | Research technologies and best practices |
| `ceo-reviewer` | Strategic/scope pressure test on a written plan |
| `eng-reviewer` | Architecture review on a written plan |
| `design-reviewer` | UX/visual review on a written plan |
| `devex-reviewer` | Developer-experience review on a written plan |

## Related Pages

- [Testing & Debugging](/workflows/testing-and-debugging/) — TDD and debugging workflows
- [Reviewing & Shipping](/workflows/reviewing-and-shipping/) — Code review and git workflows
- [Skills Reference](/reference/skills/) — All 35 skills
