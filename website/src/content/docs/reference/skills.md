---
title: Skills Reference
description: All 35 skills in Claude Kit, organized around the 6-phase development workflow.
---

# Skills Reference

Claude Kit is organized around a **6-phase development workflow**. 13 spine skills are user-invocable — typed directly as `/claudekit:<name>` — and 22 supporting skills auto-trigger by context behind the scenes.

## How Skills Work

Skills have trigger descriptions with keywords. When your conversation matches, the skill loads automatically:

```
"fix this bug"           → systematic-debugging, root-cause-tracing
"plan the feature"       → brainstorming, writing-plans
"review my plan"         → plan-ceo-review, plan-eng-review
"switch to brainstorm"   → mode-switching, brainstorming
```

You can also invoke spine skills directly by typing `/claudekit:<name>`. Project-level skills go in `.claude/skills/`.

---

## 🧠 Think

Explore ideas, refine requirements, produce a spec.

| Skill | Description | Triggers On |
|-------|-------------|-------------|
| **brainstorming** | Interactive design — one question at a time. Includes Startup Mode (6 forcing questions) for new product ideas | "brainstorm", "design", "explore", "is this worth building" |
| **writing-plans** | Break a spec into bite-sized tasks with exact code, file paths, and verification commands | "plan", "break down", "task list", "implementation steps" |

## 🔍 Review

Pressure-test a written plan before coding. Each dimension scores 0-10 with a one-sentence rationale and concrete fixes. Selected fixes are written directly into the plan file.

| Skill | Dimensions scored | When to invoke |
|-------|------------------|----------------|
| **autoplan** | All 4 below, parallel fan-out, single consolidated fix gate | Full gauntlet before handoff — "autoplan", "auto review", "run all reviews" |
| **plan-ceo-review** | Ambition, problem clarity, wedge focus, demand reality, future-fit | Scope / strategy pressure-test — "think bigger", "scope review" |
| **plan-eng-review** | Data flow, failure modes, edge cases, test matrix, rollback | Architecture audit — "does this design make sense", "lock in the plan" |
| **plan-design-review** | Hierarchy, visual consistency, state coverage, accessibility, AI-slop avoidance | Plans with UI surfaces — "design critique", "avoid AI slop" |
| **plan-devex-review** | Time to Hello World, ergonomics, error copy, docs structure, magical moments | Plans shipping APIs / CLIs / SDKs — "DX review", "is this SDK ergonomic" |

## 🔨 Build

Implement with discipline — TDD, systematic debugging, and verification gates.

| Skill | Description | Triggers On |
|-------|-------------|-------------|
| **feature-workflow** | End-to-end orchestrator: requirements → plan → review → implement → test → review | "feature", "implement end-to-end" |
| **test-driven-development** | Strict red-green-refactor — no production code without a failing test first | "implement", "add feature", "fix bug", "build" |
| **systematic-debugging** | 4-phase investigation: observe, hypothesize, test, prove | "bug", "error", "broken", stack traces |
| **verification-before-completion** | Mandatory evidence before any completion claim | "done", "fixed", "tests pass" |

## 🎛️ Session

| Skill | Description | Triggers On |
|-------|-------------|-------------|
| **mode-switching** | Switch behavioral modes (brainstorm, token-efficient, deep-research, implementation, review) | "mode", "switch to brainstorm" |

## ⚙️ Setup

| Skill | Description | Triggers On |
|-------|-------------|-------------|
| **init** | Interactive setup wizard — scaffolds rules, modes, hooks, MCP configs into your project | `/claudekit:init` (user-invocable) |

---

## Supporting Skills (auto-trigger, non-user-invocable)

These 22 skills activate silently when Claude detects a matching context. You don't invoke them directly — they shape how Claude works within the spine phases above.

### Execution & Parallelism

| Skill | Triggers On |
|-------|-------------|
| **executing-plans** | "execute the plan", "run the plan" |
| **subagent-driven-development** | "use subagents", "dispatch agents", parallel task execution |
| **using-git-worktrees** | "worktree", "isolated branch", parallel development |
| **finishing-a-development-branch** | "ship it", "ready to merge", "branch is done" |
| **dispatching-parallel-agents** | 3+ independent failures or tasks |
| **condition-based-waiting** | "wait for", "check status", polling CI pipelines |

### Testing Discipline

| Skill | Triggers On |
|-------|-------------|
| **testing** | pytest, Vitest, Jest — fixtures, mocking, coverage config |
| **playwright** | E2E tests, page objects, visual regression |
| **testing-anti-patterns** | "flaky test", "mock", test review — catches unreliable tests |

### Debug Techniques

| Skill | Triggers On |
|-------|-------------|
| **root-cause-tracing** | Deep bugs where error location differs from bug origin |
| **defense-in-depth** | Data integrity bugs, single-point bypass scenarios |

### Review Etiquette

| Skill | Triggers On |
|-------|-------------|
| **requesting-code-review** | Before PRs, before merging |
| **receiving-code-review** | Review comments, PR feedback |

### Reasoning & Meta

| Skill | Triggers On |
|-------|-------------|
| **sequential-thinking** | Complex decisions needing step-by-step reasoning |
| **writing-concisely** | "be concise", "code only" — 30-70% token savings |
| **writing-skills** | "create a skill", "new skill" |
| **refactoring** | "refactor", "clean up", "simplify" |

### Operations

| Skill | Triggers On |
|-------|-------------|
| **devops** | Docker, GitHub Actions, Cloudflare Workers — CI/CD, deployment |
| **git-workflows** | "commit", "PR", "ship", "changelog" |
| **performance-optimization** | "slow", "optimize", "profiling", N+1 queries, bundle size |
| **session-management** | "checkpoint", "index", "status", context loading |

### Security

| Skill | Triggers On |
|-------|-------------|
| **owasp** | Security review, user input, authentication, CORS, CSP |

---

## Counts

- **Total:** 35 skills
- **Spine (user-invocable):** 13 — brainstorming, writing-plans, autoplan, plan-ceo-review, plan-eng-review, plan-design-review, plan-devex-review, feature-workflow, test-driven-development, systematic-debugging, verification-before-completion, mode-switching, init
- **Supporting (auto-trigger only):** 22
