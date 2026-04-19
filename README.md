# Claude Kit

A comprehensive Claude Code plugin to accelerate development workflows for teams working with Python and JavaScript/TypeScript.

## Features

- **44 Skills** - Auto-triggered by context: framework, language, methodology, patterns, workflows, optimization (all with YAML frontmatter and bundled resources)
- **20 Specialized Agents** - From planning to deployment
- **Interactive Setup Wizard** - `/claudekit:init` scaffolds rules, modes, hooks, and MCP configs into your project
- **7 Behavioral Modes** - Task-specific response optimization (installed via init)
- **Token Optimization** - 30-70% cost savings with compressed output modes
- **MCP Integrations** - Context7, Sequential Thinking, Playwright, Memory, Filesystem (configured via init)

## Quick Start

### Install via Marketplace

1. Add the claudekit marketplace:
   ```
   /plugin marketplace add duthaho/claudekit-marketplace
   ```

2. Install the plugin:
   ```
   /plugin install claudekit
   ```

3. Run the setup wizard to configure your project:
   ```
   /claudekit:init
   ```

   Or install everything at once:
   ```
   /claudekit:init --all
   ```

### Local Development

Test the plugin locally without installing:
```
claude --plugin-dir ./path/to/claudekit
```

## What `/claudekit:init` Configures

The setup wizard interactively scaffolds project-level configuration:

| Category | What | Location |
|----------|------|----------|
| **Rules** | API, frontend, migrations, security, testing | `.claude/rules/` |
| **Modes** | brainstorm, deep-research, default, implementation, orchestration, review, token-efficient | `.claude/modes/` |
| **Hooks** | auto-format, block-dangerous-commands, notifications | `.claude/hooks/` + `settings.local.json` |
| **MCP Servers** | Context7, Sequential, Playwright, Memory, Filesystem | `.mcp.json` |

## Plugin Structure

```
claudekit/
├── .claude-plugin/
│   └── plugin.json            # Plugin manifest
├── skills/                    # 44 skills (auto-triggered)
│   ├── init/                  # Setup wizard (/claudekit:init)
│   │   ├── SKILL.md
│   │   └── templates/         # Rules, modes, hooks, MCP templates
│   ├── brainstorming/
│   ├── systematic-debugging/
│   └── ...
├── agents/                    # 20 specialized agents
├── scripts/                   # Hook scripts (installed via init)
└── website/                   # Documentation site
```

## Agents

### Core Development
| Agent | Description |
|-------|-------------|
| `claudekit:planner` | Task decomposition and planning |
| `claudekit:debugger` | Error analysis and fixing |
| `claudekit:tester` | Test generation |
| `claudekit:code-reviewer` | Code review with security focus |
| `claudekit:scout` | Codebase exploration |

### Operations
| Agent | Description |
|-------|-------------|
| `claudekit:git-manager` | Git operations and PRs |
| `claudekit:docs-manager` | Documentation generation |
| `claudekit:project-manager` | Progress tracking |
| `claudekit:database-admin` | Schema and migrations |
| `claudekit:ui-ux-designer` | UI component creation |

### Content & Research
| Agent | Description |
|-------|-------------|
| `claudekit:researcher` | Technology research |
| `claudekit:scout-external` | External resource exploration |
| `claudekit:copywriter` | Marketing copy and release notes |
| `claudekit:journal-writer` | Development journals and decision logs |

### Extended
| Agent | Description |
|-------|-------------|
| `claudekit:cicd-manager` | CI/CD pipeline management |
| `claudekit:security-auditor` | Security reviews |
| `claudekit:api-designer` | API design and OpenAPI |
| `claudekit:vulnerability-scanner` | Security scanning |
| `claudekit:pipeline-architect` | Pipeline optimization |

## Skills (44 Total)

Skills auto-trigger based on context. After plugin install, invoke manually with `/claudekit:<skill-name>`.

### Tech Stack Skills (7)

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

### Workflow Skills (7)

| Skill | Description |
|-------|-------------|
| **feature-workflow** | End-to-end feature development: requirements -> planning -> implementation -> testing -> review |
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

### Setup Skill (1)

| Skill | Description |
|-------|-------------|
| **init** | Interactive setup wizard — scaffolds rules, modes, hooks, MCP configs |

### Bundled Resources

Skills include progressive-disclosure resources loaded on demand:

| Resource Type | Purpose | Examples |
|---------------|---------|----------|
| **references/** | Cheat sheets, decision trees, pattern catalogs | OWASP Top 10, index decision tree, auth flows |
| **templates/** | Starter files, boilerplate, configs | OpenAPI spec, Dockerfile, CI workflows |
| **scripts/** | Executable helpers for deterministic tasks | Security audit scanner, OpenAPI validator |

## Behavioral Modes

Installed via `/claudekit:init`. Switch modes to optimize responses:

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
"switch to brainstorm mode"     # -> mode-switching skill activates
"let's focus on implementation" # -> implementation mode
```

## MCP Integrations

Configured via `/claudekit:init`. MCP servers extend Claude Kit with powerful capabilities.

| Server | Package | Purpose |
|--------|---------|---------|
| Context7 | `@upstash/context7-mcp` | Up-to-date library documentation |
| Sequential | `@modelcontextprotocol/server-sequential-thinking` | Multi-step reasoning |
| Playwright | `@playwright/mcp` | Browser automation (Microsoft) |
| Memory | `@modelcontextprotocol/server-memory` | Persistent knowledge graph |
| Filesystem | `@modelcontextprotocol/server-filesystem` | Secure file operations |

## Workflow Chains

Skills chain automatically based on context:

### Feature Development
```
brainstorming -> writing-plans -> feature-workflow -> requesting-code-review -> git-workflows
```

### Bug Fix
```
systematic-debugging -> root-cause-tracing -> test-driven-development -> verification-before-completion
```

### Ship Code
```
verification-before-completion -> requesting-code-review -> git-workflows -> finishing-a-development-branch
```

### Parallel Work
```
dispatching-parallel-agents -> subagent-driven-development -> verification-before-completion
```

## Requirements

- Claude Code 1.0+
- Git
- Node.js or Python (depending on your stack)

## License

MIT

---

Built by duthaho
