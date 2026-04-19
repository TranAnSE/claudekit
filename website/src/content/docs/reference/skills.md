---
title: Skills Reference
description: All 44 skills in Claude Kit, organized by category.
---

# Skills Reference

Skills are knowledge modules that auto-trigger based on keywords in your conversation. No commands needed — Claude activates the right skills based on what you're doing.

## How Skills Work

Each skill has a trigger description with keywords. When you say something that matches, the skill loads automatically:

```
"fix this bug"           → systematic-debugging, root-cause-tracing
"plan the feature"       → brainstorming, writing-plans
"review the code"        → requesting-code-review
"switch to brainstorm"   → mode-switching, brainstorming
```

Skills are bundled with the plugin and auto-trigger when installed. You can also create project-level skills in `.claude/skills/`.

---

## Development

Skills for languages, frameworks, and application patterns.

| Skill | Description | Triggers On |
|-------|-------------|-------------|
| **languages** | Python, TypeScript, JavaScript idioms — type hints, generics, async/await, Pydantic, Zod | Language-specific code patterns |
| **frontend** | React components, Next.js App Router, SSR/SSG, shadcn/ui, hooks | React, Next.js, component work |
| **frontend-styling** | Tailwind CSS, WCAG accessibility, ARIA, dark mode, responsive | Styling, accessibility |
| **backend-frameworks** | FastAPI, Django, NestJS, Express — routing, middleware, DI | API endpoints, server code |
| **databases** | PostgreSQL, MongoDB, Redis — schema, queries, indexing, migrations | Database operations |
| **state-management** | useState, Zustand, Jotai, TanStack Query, server/form/URL state | State architecture |
| **api-client** | axios, fetch, httpx — interceptors, retry logic, type-safe clients | HTTP requests, API integration |
| **openapi** | OpenAPI 3.1 design, error contracts, pagination, code-gen | API specification |

## Infrastructure

Skills for deployment, caching, logging, and operational concerns.

| Skill | Description | Triggers On |
|-------|-------------|-------------|
| **devops** | Docker, GitHub Actions, Cloudflare Workers, multi-stage builds | Containers, CI/CD, deployment |
| **caching** | Redis, memoization, HTTP cache headers, CDN, TTL policies | Cache strategy |
| **logging** | Logger setup, log levels, correlation IDs, sensitive data redaction | Logging, observability |
| **error-handling** | Try/catch, custom errors, retry logic, React error boundaries | Exception handling |
| **background-jobs** | Celery, BullMQ, task queues, cron jobs, async processing | Background tasks, workers |
| **authentication** | JWT, OAuth2, sessions, RBAC, password hashing, MFA | Login, auth, permissions |
| **performance-optimization** | Profiling, N+1 queries, bundle size, memory leaks, benchmarks | "slow", "optimize", "profiling" |

## Quality

Skills for testing, security, and code verification.

| Skill | Description | Triggers On |
|-------|-------------|-------------|
| **testing** | pytest, Vitest, Jest — fixtures, mocking, coverage, config | Writing/debugging tests |
| **test-driven-development** | Strict red-green-refactor — no production code without failing test | "implement", "add feature", "build" |
| **testing-anti-patterns** | Detecting unreliable tests, heavy mocking, false positives | "flaky test", "mock", test review |
| **playwright** | E2E tests, page objects, visual regression, cross-browser | End-to-end testing |
| **owasp** | OWASP Top 10, XSS, SQL injection, CSRF, dependency scanning | Security review, user input |
| **defense-in-depth** | Multi-layer validation, preventing single-point bypass | Data integrity bugs |
| **verification-before-completion** | Mandatory evidence before completion claims | "done", "fixed", "tests pass" |

## Debugging

Skills for investigating and resolving issues.

| Skill | Description | Triggers On |
|-------|-------------|-------------|
| **systematic-debugging** | Four-phase investigation: observe, hypothesize, test, fix | "bug", "error", "broken", stack traces |
| **root-cause-tracing** | Tracing bugs that manifest far from their origin | Deep bugs, data corruption |
| **sequential-thinking** | Step-by-step reasoning with confidence tracking | Complex decisions, analysis |
| **condition-based-waiting** | Polling CI pipelines, deployments, long-running processes | "wait for", "check status" |

## Workflow

Skills for development process and session management.

| Skill | Description | Triggers On |
|-------|-------------|-------------|
| **feature-workflow** | End-to-end: requirements → planning → implementation → review | "feature", "implement end-to-end" |
| **brainstorming** | Interactive design with one question at a time | "brainstorm", "design", "explore" |
| **writing-plans** | Detailed task breakdown with exact code and file paths | "plan", "break down", "task list" |
| **executing-plans** | Subagent-driven execution with review gates | "execute the plan", "run the plan" |
| **git-workflows** | Conventional commits, PRs, changelogs, release notes | "commit", "PR", "ship", "changelog" |
| **documentation** | Docstrings, JSDoc, README, API docs, tech specs | "document", "docstring", "README" |
| **refactoring** | Improving code structure without behavior change | "refactor", "clean up", "simplify" |
| **mode-switching** | Switching behavioral modes for the session | "mode", "switch to brainstorm" |
| **session-management** | Checkpoints, project indexing, context loading | "checkpoint", "index", "status" |
| **writing-concisely** | Token optimization, compressed output, 30-70% savings | "be concise", "code only" |

## Collaboration

Skills for multi-agent workflows and team processes.

| Skill | Description | Triggers On |
|-------|-------------|-------------|
| **dispatching-parallel-agents** | Launching parallel agents for independent tasks | 3+ independent failures/tasks |
| **subagent-driven-development** | Parallel task execution via Agent tool | "use subagents", "dispatch agents" |
| **using-git-worktrees** | Isolated branch work, parallel development | "worktree", "isolated branch" |
| **requesting-code-review** | Preparing code for review with clear context | Before PRs, before merging |
| **receiving-code-review** | Processing review feedback systematically | Review comments, PR feedback |
| **finishing-a-development-branch** | Branch completion: verify, review, merge/PR options | "ship it", "ready to merge" |
| **writing-skills** | Creating and editing skills for this kit | "create a skill", "new skill" |

## Setup

| Skill | Description | Triggers On |
|-------|-------------|-------------|
| **init** | Interactive setup wizard — scaffolds rules, modes, hooks, MCP configs | `/claudekit:init` (user-invocable) |
