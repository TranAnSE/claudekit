---
title: Planning & Building
description: How Claude Kit guides you from idea to implementation using brainstorming, planning, and execution skills.
---

# Planning & Building

Claude Kit provides a structured workflow for turning ideas into working code: **Brainstorm > Plan > Execute > Verify**.

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
| `languages` | Python/TypeScript/JavaScript idioms and patterns |
| `backend-frameworks` | FastAPI, Django, NestJS, Express patterns |
| `frontend` | React, Next.js component architecture |
| `databases` | Schema design, queries, migrations |
| `state-management` | Choosing between useState, Zustand, TanStack Query |

## Supporting Agents

| Agent | Role |
|-------|------|
| `planner` | Research and create implementation plans |
| `brainstormer` | Explore solutions and evaluate trade-offs |
| `researcher` | Research technologies and best practices |

## Related Pages

- [Testing & Debugging](/claudekit/workflows/testing-and-debugging/) — TDD and debugging workflows
- [Reviewing & Shipping](/claudekit/workflows/reviewing-and-shipping/) — Code review and git workflows
- [Skills Reference](/claudekit/reference/skills/) — All 43 skills
