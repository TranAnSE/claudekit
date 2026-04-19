---
title: Configuration
description: How to customize Claude Kit for your project.
---

# Configuration

Claude Kit works out of the box, but customizing it for your project makes it significantly more effective.

## CLAUDE.md

The main configuration file is `.claude/CLAUDE.md`. This tells Claude about your project so skills can provide relevant guidance.

### Key Sections

#### Tech Stack

```markdown
## Tech Stack
- **Languages**: Python 3.11, TypeScript 5.0
- **Backend Framework**: FastAPI with SQLAlchemy
- **Frontend Framework**: Next.js 14 with App Router
- **Database**: PostgreSQL 15
- **Testing**: pytest, vitest, Playwright
- **Deployment**: Docker, GitHub Actions
```

#### Code Conventions

```markdown
## Code Conventions

### Naming
| Type | Python | TypeScript |
|------|--------|------------|
| Files | `snake_case.py` | `kebab-case.ts` |
| Functions | `snake_case` | `camelCase` |
| Classes | `PascalCase` | `PascalCase` |
| Constants | `UPPER_SNAKE` | `UPPER_SNAKE` |
```

#### Security Standards

```markdown
## Security Standards

### Forbidden
- No hardcoded secrets
- No `eval()` or dynamic code execution
- No SQL string concatenation
- No `any` types in TypeScript

### Required
- Input validation on all user inputs
- Authentication on protected endpoints
- Secrets via environment variables only
```

#### Git Conventions

```markdown
## Git Conventions

### Branch Naming
- `feature/[ticket]-[description]`
- `fix/[ticket]-[description]`
- `hotfix/[description]`

### Commit Messages
Format: `type(scope): subject`
Types: feat, fix, docs, style, refactor, test, chore
```

## settings.json

The `.claude/settings.json` file controls Claude Code permissions and hooks:

```json
{
  "permissions": {
    "allow": [
      "git status", "git diff", "git log",
      "npm test", "npm run lint",
      "pytest", "ruff check"
    ]
  }
}
```

### Auto-Linting Hooks

Claude Kit includes PostToolUse hooks that auto-lint files after edits:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "ruff check --fix $FILE",
            "match_files": "*.py"
          }
        ]
      }
    ]
  }
}
```

## Agent Behavior Overrides

Customize how specialized agents behave in your CLAUDE.md:

```markdown
## Agent Behavior Overrides

### Planner Agent
- Break tasks into 15-60 minute chunks
- Always identify testing requirements

### Code-Reviewer Agent
- Enforce strict typing
- Security-first reviews
- Check for test coverage

### Tester Agent
- Use pytest for Python, vitest for TypeScript
- Generate edge case tests
```

## Modes

Set default modes or customize their behavior. Mode files live in `.claude/modes/`:

| Mode | Best For |
|------|----------|
| `default` | General tasks |
| `brainstorm` | Design, ideation |
| `implementation` | Code-focused, minimal prose |
| `review` | Critical analysis |
| `token-efficient` | High-volume work, cost savings |
| `deep-research` | Investigation, audits |
| `orchestration` | Multi-agent coordination |

Switch modes naturally: "switch to brainstorm mode" or "use implementation mode".

## Example Complete Configuration

```markdown
# My SaaS Project

## Overview
A B2B SaaS platform for project management.

## Tech Stack
- **Backend**: FastAPI + PostgreSQL
- **Frontend**: Next.js 14 + Tailwind
- **Auth**: Clerk
- **Payments**: Stripe

## Architecture
src/
├── api/        # FastAPI routes
├── services/   # Business logic
├── models/     # SQLAlchemy models
├── frontend/   # Next.js app
└── tests/      # Test files

## Code Conventions
- Python: PEP 8, type hints required
- TypeScript: Strict mode, Zod for validation

## Security
- All inputs validated with Pydantic/Zod
- SQL via SQLAlchemy ORM only
- Secrets in environment variables

## Testing
- Python: pytest with 80% coverage minimum
- Frontend: vitest + Playwright

## Git
- Branches: feature/*, fix/*, hotfix/*
- Commits: conventional commits format
```

## Next Steps

- [Workflows](/claudekit/workflows/planning-and-building/) — See how skills work together
- [Skills Reference](/claudekit/reference/skills/) — Browse all 43 skills
- [Creating Skills](/claudekit/customization/creating-skills/) — Build your own
