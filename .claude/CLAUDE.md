# Claude Kit - Project Context Template

## Overview

This is a comprehensive Claude Kit for Claude Code, designed to accelerate development workflows for small teams (1-3 developers) working with Python and JavaScript/TypeScript multi-stack projects.

## Quick Reference

### Key Skills (auto-triggered)

| Skill | Triggers on |
|-------|------------|
| `feature-workflow` | "feature", "implement", "build", "add functionality" |
| `systematic-debugging` | "bug", "error", "failing", "broken", stack traces |
| `git-workflows` | "commit", "PR", "ship", "changelog" |
| `writing-plans` | "plan", "break down", "implementation steps" |
| `brainstorming` | "brainstorm", "design", "explore", "trade-offs" |
| `documentation` | "document", "docstring", "README", "API docs" |
| `refactoring` | "refactor", "clean up", "extract", "simplify" |
| `performance-optimization` | "slow", "performance", "profiling", "N+1" |
| `mode-switching` | "mode", "switch mode", "token-efficient" |
| `session-management` | "checkpoint", "index", "load context", "status" |

## Tech Stack

<!-- CUSTOMIZATION POINT: Update for your project -->
- **Languages**: Python, TypeScript, JavaScript
- **Backend Frameworks**: FastAPI, Django, NestJS, Express
- **Frontend Frameworks**: Next.js, React
- **Databases**: PostgreSQL, MongoDB
- **Testing**: pytest, vitest, Jest, Playwright
- **DevOps**: Docker, GitHub Actions, Cloudflare

## Architecture

<!-- CUSTOMIZATION POINT: Describe your project architecture -->
```
src/
├── api/          # API endpoints
├── services/     # Business logic
├── models/       # Data models
├── utils/        # Utilities
└── tests/        # Test files
```

## Code Conventions

### Naming Conventions

| Type | Python | TypeScript/JavaScript |
|------|--------|----------------------|
| Files | `snake_case.py` | `kebab-case.ts` |
| Functions | `snake_case` | `camelCase` |
| Classes | `PascalCase` | `PascalCase` |
| Constants | `UPPER_SNAKE` | `UPPER_SNAKE` |
| Components | N/A | `PascalCase.tsx` |

### Code Style

- **Python**: Follow PEP 8, use type hints, docstrings for public APIs
- **TypeScript**: Strict mode enabled, no `any` types, use interfaces
- **JavaScript**: ESLint + Prettier, prefer `const` over `let`

### File Organization

- One component/class per file
- Group related files in feature directories
- Keep test files adjacent to source files or in `tests/` directory

## Testing Standards

### Coverage Requirements
- Minimum coverage: 80%
- Critical paths: 95%

### Test Naming
- **Python**: `test_[function]_[scenario]_[expected]`
- **TypeScript**: `describe('[Component]', () => { it('should [behavior]') })`

### Test Types
1. **Unit tests**: All business logic functions
2. **Integration tests**: API endpoints, database operations
3. **E2E tests**: Critical user flows

## Security Standards

### Forbidden Patterns
- No hardcoded secrets or API keys
- No `eval()` or dynamic code execution
- No SQL string concatenation (use parameterized queries)
- No `any` types in TypeScript
- No disabled security headers

### Required Practices
- Input validation on all user inputs
- Output encoding for all rendered content
- Authentication on all protected endpoints
- Rate limiting on public APIs
- Secrets via environment variables only

## Git Conventions

### Branch Naming
- `feature/[ticket]-[description]`
- `fix/[ticket]-[description]`
- `hotfix/[description]`
- `chore/[description]`

### Commit Messages
```
type(scope): subject

body (optional)

footer (optional)
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### PR Requirements
- Descriptive title and description
- Linked to issue/ticket
- All tests passing
- Code review approved
- No merge conflicts

## Agent Behavior Overrides

<!-- CUSTOMIZATION POINT: Override default agent behaviors -->

### Planner Agent
- Break tasks into chunks of 15-60 minutes
- Always identify testing requirements
- Flag external dependencies

### Code-Reviewer Agent
- Enforce strict typing
- Security-first reviews
- Check for test coverage

### Tester Agent
- Prefer pytest for Python, vitest for TypeScript
- Generate edge case tests
- Include error scenario tests

### Debugger Agent
- Check logs first
- Reproduce before fixing
- Add regression tests

## Behavioral Modes

<!-- CUSTOMIZATION POINT: Configure default mode -->

Modes adjust communication style, output format, and problem-solving approach.

| Mode | Description | Best For |
|------|-------------|----------|
| `default` | Balanced standard behavior | General tasks |
| `brainstorm` | Creative exploration, questions | Design, ideation |
| `writing-concisely` | Compressed, concise output | High-volume, cost savings |
| `deep-research` | Thorough analysis, citations | Investigation, audits |
| `implementation` | Code-focused, minimal prose | Executing plans |
| `review` | Critical analysis, finding issues | Code review, QA |
| `orchestration` | Multi-task coordination | Complex parallel work |

### Mode Activation

Ask Claude to switch modes naturally:
- "switch to brainstorm mode" → creative exploration
- "use implementation mode" → code-focused, minimal prose
- "switch to token-efficient mode" → compressed output (30-70% savings)

Mode files: `.claude/modes/`

## Token Optimization

<!-- CUSTOMIZATION POINT: Set default output mode -->

Control output verbosity for cost optimization.

| Level | Activation | Savings | Description |
|-------|-----------|---------|-------------|
| Standard | (default) | 0% | Full explanations |
| Concise | "be concise" | 30-40% | Reduced explanations |
| Ultra | "code only" | 60-70% | Code-only responses |
| Session | "switch to token-efficient mode" | 30-70% | Compressed for session |

Reference: `.claude/skills/writing-concisely/SKILL.md`

## Context Management

These features are provided by the `session-management` skill:

- **Project Indexing** — "generate a project index" → scans and creates PROJECT_INDEX.md
- **Context Loading** — "load the API context" → reads relevant files into context
- **Checkpoints** — "save checkpoint feature-x" → git stash + metadata for session recovery
- **Status** — "what's the project status?" → git state, tasks, recent commits

## MCP Integrations

<!-- CUSTOMIZATION POINT: Enable/disable MCP servers -->

Optional MCP servers for extended capabilities.

| Server | Purpose | Status |
|--------|---------|--------|
| Context7 | Library documentation lookup | Optional |
| Sequential | Multi-step reasoning tools | Optional |
| Playwright | Browser automation (Microsoft) | Optional |
| Memory | Persistent knowledge graph | Optional |
| Filesystem | Secure file operations | Optional |

Setup: See `.claude/mcp/README.md`

## Methodology Settings

<!-- CUSTOMIZATION POINT: Configure superpowers methodology -->

Settings to control the integrated superpowers development methodology.

### Planning Granularity

| Mode | Task Size | Use Case |
|------|-----------|----------|
| `standard` | 15-60 min | Quick planning, experienced team |
| `detailed` | 2-5 min | Thorough plans with exact code |

To use detailed mode: "plan this in detail" or "break this into 2-5 min tasks"

### Brainstorming Style

| Style | Description |
|-------|-------------|
| `standard` | All questions at once |
| `interactive` | One question per message with validation |

To use interactive mode: "let's brainstorm [topic]"

### Execution Mode

| Mode | Description |
|------|-------------|
| `manual` | Developer executes tasks from plan |
| `subagent` | Automated execution with code review gates |

To use subagent mode: "execute the plan" or "run the plan with subagents"

### TDD Strictness

For strict TDD enforcement (no production code without failing test):
- Auto-triggers on implementation tasks
- Reference: `.claude/skills/test-driven-development/SKILL.md`

### Verification Requirements

Enable mandatory verification before completion claims:
- Reference: `.claude/skills/verification-before-completion/SKILL.md`

### Available Skills

| Category | Skills |
|----------|--------|
| **Languages** | languages (Python, TypeScript, JavaScript) |
| **Backend** | backend-frameworks (FastAPI, Django, NestJS, Express) |
| **Frontend** | frontend (React, Next.js, shadcn/ui), frontend-styling (Tailwind, accessibility) |
| **Databases** | databases (PostgreSQL, MongoDB, Redis, migrations) |
| **DevOps** | devops (Docker, GitHub Actions, Cloudflare Workers) |
| **Security** | owasp |
| **API** | openapi |
| **Testing** | testing (pytest, vitest, Jest), playwright |
| **Optimization** | writing-concisely, performance-optimization |
| **Developer Patterns** | error-handling, state-management, logging, caching, api-client, authentication, background-jobs |
| **Workflows** | feature-workflow, git-workflows, documentation, refactoring |
| **Session** | mode-switching, session-management |
| **Methodology - Planning** | brainstorming, writing-plans, executing-plans, writing-skills |
| **Methodology - Testing** | test-driven-development, verification-before-completion, testing-anti-patterns |
| **Methodology - Debugging** | systematic-debugging, root-cause-tracing, defense-in-depth |
| **Methodology - Collaboration** | dispatching-parallel-agents, requesting-code-review, receiving-code-review, finishing-a-development-branch |
| **Methodology - Execution** | subagent-driven-development, using-git-worktrees, condition-based-waiting |
| **Methodology - Reasoning** | sequential-thinking |

Skills location: `.claude/skills/`

Each skill includes:
- YAML frontmatter with trigger description
- "When to Use" / "When NOT to Use" sections
- Core patterns with code examples
- Best practices and common pitfalls
- Bundled reference docs, templates, and scripts

### Sequential Thinking

For complex problems requiring step-by-step analysis:
- Reference: `.claude/skills/sequential-thinking/SKILL.md`
- Activation: auto-triggers on complex reasoning tasks, or use deep-research mode

## Environment Configuration

<!-- CUSTOMIZATION POINT: Update for your environments -->

### Development
```bash
# Python
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Node.js
pnpm install
pnpm dev
```

### Testing
```bash
# Python
pytest -v --cov=src

# Node.js
pnpm test
pnpm test:coverage
```

### Deployment
```bash
# Build
pnpm build

# Deploy
pnpm deploy:staging
pnpm deploy:production
```

## External Integrations

<!-- CUSTOMIZATION POINT: Add your integrations -->

### APIs
- GitHub API for issue tracking
- Slack for notifications (optional)

### Services
- Database: PostgreSQL / MongoDB
- Cache: Redis (optional)
- Storage: S3 / Cloudflare R2

## Documentation Standards

### Code Documentation
- Public functions: Docstrings required
- Complex logic: Inline comments
- APIs: OpenAPI/Swagger specs

### Project Documentation
- README.md: Quick start guide
- CONTRIBUTING.md: Contribution guidelines
- CHANGELOG.md: Version history

## Troubleshooting

### Common Issues

**Python import errors**
```bash
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

**Node modules issues**
```bash
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

**Database connection**
- Check `.env` file for correct credentials
- Ensure database service is running

---

## Kit Version

- **Claude Kit Version**: 3.0.0
- **Last Updated**: 2026-04-18
- **Compatible with**: Claude Code 1.0+
- **Total Skills**: 43 (with YAML frontmatter, bundled resources)
- **Total Agents**: 20
- **Behavioral Modes**: 7
