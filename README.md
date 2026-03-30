# Claude Kit

A comprehensive toolkit for Claude Code to accelerate development workflows for teams working with Python and JavaScript/TypeScript.

## Features

- **20 Specialized Agents** - From planning to deployment
- **27+ Slash Commands** - Workflow automation with flag support
- **38 Skills** - Framework, language, methodology, patterns, and optimization expertise (all with YAML frontmatter and bundled resources)
- **7 Behavioral Modes** - Task-specific response optimization
- **Command Flag System** - Combinable `--flag` syntax for customization
- **Token Optimization** - 30-70% cost savings with compressed output modes
- **MCP Integrations** - Context7, Sequential Thinking, Playwright, Memory, Filesystem
- **Context Management** - Project indexing, checkpoints, parallel tasks

## Quick Start

1. Copy the `.claude` folder to your project root
2. Customize `.claude/CLAUDE.md` for your project
3. Start using commands like `/feature`, `/review`, `/test`

## Directory Structure

```
.claude/
├── CLAUDE.md              # Project context (customize this!)
├── settings.json          # Hooks, permissions, and MCP config
├── agents/                # 20 specialized agents
├── commands/              # 27+ workflow commands
├── modes/                 # 7 behavioral mode definitions
├── mcp/                   # MCP server configurations
└── skills/                # 38 skills with YAML frontmatter & bundled resources
    ├── api/               # OpenAPI specification patterns
    ├── databases/         # PostgreSQL, MongoDB
    ├── devops/            # Docker, GitHub Actions
    ├── frameworks/        # FastAPI, Django, Next.js, React
    ├── frontend/          # Tailwind CSS, shadcn/ui
    ├── languages/         # Python, TypeScript, JavaScript
    ├── methodology/       # TDD, debugging, planning, review (14 skills)
    ├── optimization/      # Token efficiency patterns
    ├── patterns/          # Error handling, state, logging, caching, auth, API client
    ├── security/          # OWASP security patterns
    └── testing/           # pytest, vitest
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

## Commands

### Development Workflow
```bash
/feature [description]   # Full feature development
/fix [error]            # Debug and fix bugs
/review [file]          # Code review
/test [scope]           # Generate tests
/tdd [feature]          # Test-driven development
```

### Git & Deployment
```bash
/commit [message]       # Smart commit
/ship [message]         # Commit + PR
/pr [title]             # Create pull request
/deploy [env]           # Deploy to environment
```

### Documentation & Planning
```bash
/plan [task]            # Create implementation plan
/plan --detailed [task] # Detailed plan (2-5 min tasks)
/brainstorm [topic]     # Interactive design session
/execute-plan [file]    # Subagent-driven execution
/doc [target]           # Generate documentation
/research [topic]       # Research technology
```

### Security & Quality
```bash
/security-scan          # Scan for vulnerabilities
/api-gen [resource]     # Generate API code
/refactor [file]        # Improve code structure
/optimize [file]        # Performance optimization
```

### Context & Modes (New)
```bash
/mode [name]            # Switch behavioral mode
/index                  # Generate project index
/load [component]       # Load project context
/checkpoint [action]    # Save/restore session state
/spawn [task]           # Launch parallel background task
```

## Skills (38 Total)

Every skill includes YAML frontmatter for reliable triggering, "When to Use" / "When NOT to Use" sections, core patterns with code examples, best practices, common pitfalls, cross-references, and bundled resources (reference docs, templates, scripts).

### Languages
- **Python** — Type hints, async, dataclasses, Pydantic, decorators, pattern matching
- **TypeScript** — Advanced types, generics, Zod, discriminated unions, branded types
- **JavaScript** — ES6+, async patterns, Proxy/Reflect, generators, modules

### Frameworks
- **FastAPI** — Routes, dependency injection, middleware, WebSocket, testing
- **Django** — ORM, views, migrations, DRF, signals, admin
- **Next.js** — App Router, server/client components, caching, middleware
- **React** — Hooks, custom hooks, context, Suspense, error boundaries, performance

### Databases
- **PostgreSQL** — Schema, indexing (B-tree/GIN/GiST), migrations, CTEs, JSONB
- **MongoDB** — Schema design, aggregation pipelines, indexing, transactions

### DevOps
- **Docker** — Multi-stage builds, Compose, security hardening, layer caching
- **GitHub Actions** — CI/CD, matrix strategy, reusable workflows, deployment

### Frontend
- **Tailwind CSS** — Responsive, dark mode, animations, theme customization
- **shadcn/ui** — Components, forms, data tables, theming, toast

### API
- **OpenAPI** — 3.1 spec, pagination, versioning, error schemas, webhooks

### Security
- **OWASP** — Top 10, auth, CORS, CSP, secret management, rate limiting

### Testing
- **pytest** — Fixtures, parametrize, mocking, async, coverage
- **vitest** — React Testing Library, mocking, MSW, snapshots, configuration

### Optimization
- **Token-efficient** — Compressed output modes (30-70% cost savings)

### Developer Patterns (New)
- **error-handling** — Custom errors, retry patterns, Result type, error boundaries
- **state-management** — React state, Zustand, TanStack Query, form state, URL state
- **logging** — Structured logging, log levels, correlation IDs, redaction
- **caching** — Memoization, HTTP cache, Redis, CDN, cache invalidation
- **api-client** — HTTP clients, interceptors, retry, type-safe clients
- **authentication** — JWT, OAuth2, sessions, RBAC, MFA, password hashing

### Methodology (14 Skills)

| Category | Skills |
|----------|--------|
| **Planning** | brainstorming, writing-plans, executing-plans |
| **Testing** | test-driven-development, verification-before-completion, testing-anti-patterns |
| **Debugging** | systematic-debugging, root-cause-tracing, defense-in-depth |
| **Collaboration** | dispatching-parallel-agents, requesting-code-review, receiving-code-review, finishing-development-branch |
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
| **templates/** | Starter files, boilerplate, configs | OpenAPI spec, Dockerfile, CI workflows, conftest.py |
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

```bash
/mode brainstorm              # Switch for session
/feature --mode=implementation # Override per command
```

## Command Flags

All commands support combinable flags:

```bash
# Mode and depth
/plan --mode=brainstorm --depth=5 "feature design"

# Persona-based review
/review --persona=security --format=detailed src/auth/

# Token optimization
/fix --format=concise "error message"

# Save output
/research --save=docs/research.md "auth libraries"
```

### Available Flags

| Flag | Description |
|------|-------------|
| `--mode=[mode]` | Behavioral mode |
| `--depth=[1-5]` | Thoroughness (1=quick, 5=exhaustive) |
| `--format=[fmt]` | Output format (concise/detailed/json) |
| `--persona=[type]` | Expertise focus (security/performance/architecture) |
| `--save=[path]` | Save output to file |
| `--checkpoint` | Create state checkpoint |

## Token Optimization

Reduce costs by 30-70% with compressed output modes:

| Level | Activation | Savings |
|-------|------------|---------|
| Concise | `--format=concise` | 30-40% |
| Ultra | `--format=ultra` | 60-70% |
| Session | `/mode token-efficient` | 30-70% |

## MCP Integrations

MCP servers extend Claude Kit with powerful capabilities. They are **automatically used** when configured.

| Server | Package | Purpose |
|--------|---------|---------|
| Context7 | `@upstash/context7-mcp` | Up-to-date library documentation |
| Sequential | `@modelcontextprotocol/server-sequential-thinking` | Multi-step reasoning |
| Playwright | `@playwright/mcp` | Browser automation (Microsoft) |
| Memory | `@modelcontextprotocol/server-memory` | Persistent knowledge graph |
| Filesystem | `@modelcontextprotocol/server-filesystem` | Secure file operations |

### How MCP Servers Enhance Commands

| Command | MCP Servers Used | Enhancement |
|---------|------------------|-------------|
| `/feature` | Context7, Sequential, Filesystem | Accurate docs, structured planning, safe file ops |
| `/fix` | Sequential, Memory, Playwright | Step-by-step debugging, context recall, browser testing |
| `/test` | Playwright, Filesystem | E2E browser tests, test file management |
| `/plan` | Sequential, Memory | Structured breakdown, remembers decisions |
| `/research` | Context7, Sequential | Real-time docs, thorough analysis |
| `/brainstorm` | Sequential, Memory | Creative exploration, persistent ideas |
| `/index` | Filesystem | Project structure scanning |

### MCP + Mode Combinations

| Mode | Primary MCP | Best For |
|------|-------------|----------|
| `brainstorm` | Sequential + Memory | Design sessions with persistent ideas |
| `deep-research` | Sequential + Context7 | Thorough technical investigation |
| `implementation` | Filesystem + Context7 | Focused coding with accurate docs |
| `review` | Playwright + Memory | UI review with context |
| `orchestration` | All 5 | Complex multi-step parallel work |

### Example: Full Feature Development

```bash
/feature Add user profile with avatar upload
```

1. **Context7** → Fetches latest React/Next.js file upload docs
2. **Sequential** → Plans component structure step-by-step
3. **Memory** → Recalls your UI patterns from previous sessions
4. **Filesystem** → Creates files in correct locations
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

### Adding Custom Commands

Create a new file in `.claude/commands/`:

```markdown
# /my-command

## Purpose
Description of your command.

---

Your prompt content here.

Use $ARGUMENTS for command arguments.
```

### Adding Custom Skills

Create a new skill in `.claude/skills/category/skillname/SKILL.md`:

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

### Feature Development
```
/feature → planner → implement → code-reviewer → tester → git-manager
```

### Bug Fix
```
/fix → debugger → scout → implement → tester → code-reviewer
```

### Ship Code
```
/ship → code-reviewer → tester → security-scan → git-manager
```

### Superpowers Workflow (Detailed)
```
/brainstorm → /plan --detailed → /execute-plan → /ship
```
Uses one-question-at-a-time design, 2-5 min tasks with exact code, subagent execution with code review gates.

### Parallel Research
```
/spawn "research auth" → /spawn "analyze security" → /spawn --collect
```
Launch multiple background tasks, then aggregate results.

### Cost-Optimized Session
```
/mode token-efficient → [work on tasks] → /mode default
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
