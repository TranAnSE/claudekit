# Claude Kit

A comprehensive toolkit for Claude Code to accelerate development workflows for teams working with Python and JavaScript/TypeScript.

## Features

- **20 Specialized Agents** - From planning to deployment
- **43 Skills** - Auto-triggered by context: framework, language, methodology, patterns, workflows, optimization (all with YAML frontmatter and bundled resources)
- **7 Behavioral Modes** - Task-specific response optimization
- **Token Optimization** - 30-70% cost savings with compressed output modes
- **MCP Integrations** - Context7, Sequential Thinking, Playwright, Memory, Filesystem
- **Context Management** - Project indexing, checkpoints, parallel tasks

## Quick Start

1. Copy the `.claude` folder to your project root
2. Customize `.claude/CLAUDE.md` for your project
3. Start working — skills auto-trigger based on what you ask ("implement X", "fix Y", "review Z")

## Directory Structure

```
.claude/
├── CLAUDE.md              # Project context (customize this!)
├── settings.json          # Hooks, permissions, and MCP config
├── agents/                # 20 specialized agents
├── modes/                 # 7 behavioral mode definitions
├── mcp/                   # MCP server configurations
└── skills/                # 43 flat skills (router pattern)
    ├── <skill-name>/      # Each skill is a top-level directory
    │   ├── SKILL.md       # Trigger description + core patterns
    │   └── references/    # Deep content loaded on demand
    └── ...
```

## Agents

### Core Development
| Agent | Description |
|-------|-------------|
| `planner` | Task decomposition and planning |
| `researcher` | Technology research |
| `debugger` | Error analysis and fixing |
| `tester` | Test generation |
| `code-reviewer` | Code review with security focus |
| `scout` | Codebase exploration |

### Operations
| Agent | Description |
|-------|-------------|
| `git-manager` | Git operations and PRs |
| `docs-manager` | Documentation generation |
| `project-manager` | Progress tracking |
| `database-admin` | Schema and migrations |
| `ui-ux-designer` | UI component creation |

### Extended
| Agent | Description |
|-------|-------------|
| `cicd-manager` | CI/CD pipeline management |
| `security-auditor` | Security reviews |
| `api-designer` | API design and OpenAPI |
| `vulnerability-scanner` | Security scanning |
| `pipeline-architect` | Pipeline optimization |

## Skills as Commands

All former slash commands have been migrated to skills that auto-trigger based on context:

```bash
# Skills auto-trigger — just describe what you want:
"implement user authentication"     # → feature-workflow + authentication
"this endpoint is slow"             # → performance-optimization
"commit these changes"              # → git-workflows
"refactor this function"            # → refactoring
"add docs to this module"           # → documentation
"scan for security issues"          # → owasp
"switch to brainstorm mode"         # → mode-switching
```

## Skills (43 Total)

Every skill follows a flat directory structure with a router pattern: short `SKILL.md` for triggering + `references/` for deep content loaded on demand. Skills auto-trigger based on context — no slash commands needed.

### Tech Stack Skills (7 merged routers)

| Skill | Covers | Key Topics |
|-------|--------|------------|
| **languages** | Python, TypeScript, JavaScript | Type hints, generics, async, Pydantic, Zod, ES6+ |
| **backend-frameworks** | FastAPI, Django, NestJS, Express | Routes, DI, middleware, ORM, guards, pipes |
| **frontend** | React, Next.js, shadcn/ui | Hooks, App Router, server components, Suspense |
| **frontend-styling** | Tailwind CSS, accessibility | Responsive, dark mode, WCAG, ARIA, focus management |
| **databases** | PostgreSQL, MongoDB, Redis, migrations | Schema, indexing, aggregation, caching, Alembic/Prisma |
| **devops** | Docker, GitHub Actions, Cloudflare Workers | Multi-stage builds, CI/CD, edge deployment |
| **testing** | pytest, vitest, Jest | Fixtures, mocking, MSW, coverage, parametrize |

### Domain Skills (8)

| Skill | Description |
|-------|-------------|
| **openapi** | OpenAPI 3.1 spec, pagination, versioning, error schemas, webhooks |
| **owasp** | Top 10, auth, CORS, CSP, secret management, rate limiting |
| **playwright** | E2E testing, page objects, visual regression, cross-browser |
| **error-handling** | Custom errors, retry patterns, Result type, error boundaries |
| **state-management** | React state, Zustand, TanStack Query, form state, URL state |
| **logging** | Structured logging, log levels, correlation IDs, redaction |
| **caching** | Memoization, HTTP cache, Redis, CDN, cache invalidation |
| **api-client** | HTTP clients, interceptors, retry, type-safe clients |

### Pattern Skills (3)

| Skill | Description |
|-------|-------------|
| **authentication** | JWT, OAuth2, sessions, RBAC, MFA, password hashing |
| **background-jobs** | Celery, BullMQ, task queues, scheduled tasks, async workers |
| **writing-concisely** | Compressed output modes (30-70% token savings) |

### Workflow Skills (7 — migrated from commands)

| Skill | Description |
|-------|-------------|
| **feature-workflow** | End-to-end feature development: requirements → planning → implementation → testing → review |
| **git-workflows** | Conventional commits, shipping, PRs, changelogs |
| **documentation** | Docstrings, JSDoc, API docs, README generation |
| **refactoring** | Code smell detection, extract/rename/simplify patterns, safe refactoring workflow |
| **performance-optimization** | Profiling (cProfile, DevTools), N+1 queries, bundle size, memory leaks, benchmarking |
| **mode-switching** | Session behavioral modes (brainstorm, token-efficient, deep-research, implementation, review) |
| **session-management** | Checkpoints, project indexing, context loading, status checking |

### Methodology Skills (18)

| Category | Skills |
|----------|--------|
| **Planning** | brainstorming, writing-plans, executing-plans, writing-skills |
| **Testing** | test-driven-development, verification-before-completion, testing-anti-patterns |
| **Debugging** | systematic-debugging, root-cause-tracing, defense-in-depth |
| **Collaboration** | dispatching-parallel-agents, requesting-code-review, receiving-code-review, finishing-a-development-branch |
| **Execution** | subagent-driven-development, using-git-worktrees, condition-based-waiting |
| **Reasoning** | sequential-thinking |

Key methodology principles:
- **TDD Strict**: No production code without failing test first
- **Verification**: Evidence-based completion claims
- **Quality Gates**: Code review between every task
- **Bite-sized Tasks**: 2-5 minute increments with exact code
- **Sequential Thinking**: Step-by-step reasoning with confidence scores

### Bundled Resources

Skills include progressive-disclosure resources loaded on demand:

| Resource Type | Purpose | Examples |
|---------------|---------|----------|
| **references/** | Cheat sheets, decision trees, pattern catalogs | OWASP Top 10, index decision tree, auth flows |
| **templates/** | Starter files, boilerplate, configs | OpenAPI spec, Dockerfile, CI workflows |
| **scripts/** | Executable helpers for deterministic tasks | Security audit scanner, OpenAPI validator |

## Behavioral Modes

Switch modes to optimize responses for different task types:

| Mode | Description | Best For |
|------|-------------|----------|
| `default` | Balanced standard behavior | General tasks |
| `brainstorm` | Creative exploration, questions | Design, ideation |
| `token-efficient` | Compressed, concise output | Cost savings |
| `deep-research` | Thorough analysis, citations | Investigation |
| `implementation` | Code-focused, minimal prose | Executing plans |
| `review` | Critical analysis, finding issues | Code review |
| `orchestration` | Multi-task coordination | Parallel work |

```
"switch to brainstorm mode"   # → mode-switching skill activates
"let's focus on implementation" # → implementation mode
```

## Token Optimization

Reduce costs by 30-70% with compressed output modes:

| Level | Activation | Savings |
|-------|------------|---------|
| Standard | (default) | 0% |
| Concise | Ask for concise output | 30-40% |
| Ultra | Ask for code-only responses | 60-70% |
| Session | "switch to token-efficient mode" | 30-70% |

## MCP Integrations

MCP servers extend Claude Kit with powerful capabilities. They are **automatically used** when configured.

| Server | Package | Purpose |
|--------|---------|---------|
| Context7 | `@upstash/context7-mcp` | Up-to-date library documentation |
| Sequential | `@modelcontextprotocol/server-sequential-thinking` | Multi-step reasoning |
| Playwright | `@playwright/mcp` | Browser automation (Microsoft) |
| Memory | `@modelcontextprotocol/server-memory` | Persistent knowledge graph |
| Filesystem | `@modelcontextprotocol/server-filesystem` | Secure file operations |

### How MCP Servers Enhance Skills

| Skill | MCP Servers Used | Enhancement |
|-------|------------------|-------------|
| feature-workflow | Context7, Sequential, Filesystem | Accurate docs, structured planning, safe file ops |
| systematic-debugging | Sequential, Memory, Playwright | Step-by-step debugging, context recall, browser testing |
| testing, playwright | Playwright, Filesystem | E2E browser tests, test file management |
| writing-plans | Sequential, Memory | Structured breakdown, remembers decisions |
| brainstorming | Sequential, Memory, Context7 | Creative exploration, persistent ideas |
| session-management | Filesystem, Memory | Project scanning, context persistence |

### Example: Full Feature Development

```
"Add user profile with avatar upload"
```

1. **feature-workflow** skill activates → orchestrates the workflow
2. **Context7** → Fetches latest React/Next.js file upload docs
3. **Sequential** → Plans component structure step-by-step
4. **Memory** → Recalls your UI patterns from previous sessions
5. **Playwright** → Tests the upload flow in browser

Setup: See `.claude/mcp/README.md`

## Customization

### CLAUDE.md

The `.claude/CLAUDE.md` file is your project context. Customize it with:

```markdown
# Project: Your Project Name

## Tech Stack
- **Backend**: FastAPI
- **Frontend**: Next.js
- **Database**: PostgreSQL

## Conventions
- Use type hints
- 80% test coverage
- Conventional commits

## Agent Overrides
### Tester
- Framework: pytest
- Coverage: 90%
```

### Adding Custom Skills

Create a new skill in `.claude/skills/<name>/SKILL.md`:

```yaml
---
name: my-skill
description: >
  What this skill does and when to trigger it. Be specific — list
  contexts, keywords, and scenarios. 2-4 pushy sentences.
---
```

```markdown
# My Skill

Brief overview.

## When to Use
- Scenario 1
- Scenario 2

## When NOT to Use
- Anti-trigger scenario

---

## Core Patterns
### Pattern Name
Code examples with good/bad comparisons.

## Best Practices
## Common Pitfalls
## Related Skills
```

Optionally add bundled resources:
```
my-skill/
├── SKILL.md
├── references/    # Loaded into context on demand
├── scripts/       # Executed without loading into context
└── templates/     # Scaffolded into user's project
```

## Workflow Chains

Skills chain automatically based on context. Here are common flows:

### Feature Development
```
brainstorming → writing-plans → feature-workflow → requesting-code-review → git-workflows
```

### Bug Fix
```
systematic-debugging → root-cause-tracing → test-driven-development → verification-before-completion
```

### Ship Code
```
verification-before-completion → requesting-code-review → git-workflows → finishing-a-development-branch
```

### Superpowers Workflow (Detailed)
```
brainstorming → writing-plans → executing-plans → git-workflows
```
Uses one-question-at-a-time design, 2-5 min tasks with exact code, subagent execution with code review gates.

### Parallel Work
```
dispatching-parallel-agents → subagent-driven-development → verification-before-completion
```
Launch multiple agents for independent tasks, then verify results.

### Cost-Optimized Session
```
"switch to token-efficient mode" → [work on tasks] → "switch to default mode"
```
Enable compressed outputs for high-volume sessions.

## Requirements

- Claude Code 1.0+
- Git
- Node.js or Python (depending on your stack)

## License

MIT

---

Built with duthaho
