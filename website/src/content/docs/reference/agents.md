---
title: Agents Reference
description: All 20 specialized subagents in Claude Kit.
---

# Agents Reference

Agents are specialized subagents that Claude can dispatch for focused tasks. Each agent has access to specific tools and expertise, making it more effective than a general-purpose prompt for its domain.

## How Agents Work

Agents are defined as markdown files in `.claude/agents/`. When Claude dispatches a subagent, it starts a fresh context focused entirely on the task at hand:

```
You: "Review this code for security issues"

Claude dispatches → security-auditor agent
  → Focused security review
  → Returns findings with severity ratings
```

Agents run independently and return results to the main conversation. They can be dispatched in parallel for independent tasks.

---

## Planning & Research

| Agent | Description | Use When |
|-------|-------------|----------|
| **planner** | Designs implementation plans, identifies critical files, considers trade-offs | Planning complex features or migrations |
| **brainstormer** | Explores solutions, evaluates architectures, debates technical decisions | Evaluating options before implementation |
| **researcher** | Comprehensive research on technologies, libraries, and best practices | Need in-depth comparison or analysis |

## Code Quality

| Agent | Description | Use When |
|-------|-------------|----------|
| **code-reviewer** | Reviews code for quality, security, performance, and maintainability | After implementing features, before PRs |
| **tester** | Runs test suites, analyzes coverage, validates error handling, verifies builds | After code changes, checking coverage |
| **debugger** | Investigates issues, analyzes system behavior, traces root causes | Debugging test failures or production bugs |

## Security

| Agent | Description | Use When |
|-------|-------------|----------|
| **security-auditor** | Security audits, OWASP compliance, code vulnerability review | Before production release, security review |
| **vulnerability-scanner** | Automated dependency scanning for known CVEs | Checking for dependency vulnerabilities |

## Infrastructure & Data

| Agent | Description | Use When |
|-------|-------------|----------|
| **database-admin** | Schema design, migrations, query optimization, data modeling | Database work for PostgreSQL or MongoDB |
| **cicd-manager** | CI/CD pipeline management, deployment automation | Setting up or fixing CI pipelines |
| **pipeline-architect** | Pipeline architecture design and build optimization | Redesigning slow CI/CD pipelines |

## Content & Documentation

| Agent | Description | Use When |
|-------|-------------|----------|
| **docs-manager** | API docs, READMEs, code comments, technical specifications | Documentation needs updating |
| **copywriter** | Marketing copy, release notes, changelogs, product descriptions | User-facing content creation |
| **journal-writer** | Development journals, decision logs, incident documentation | Recording failures or key decisions |

## Design & UI

| Agent | Description | Use When |
|-------|-------------|----------|
| **ui-ux-designer** | Design mockups to code, UI components, responsive/accessible layouts | Building or fixing UI components |
| **api-designer** | RESTful/GraphQL API design, OpenAPI specifications | Designing new APIs |

## Project Management

| Agent | Description | Use When |
|-------|-------------|----------|
| **project-manager** | Progress tracking, roadmaps, task monitoring, status reports | Checking project progress |
| **git-manager** | Stage, commit, push with conventional commits | Git operations |

## Exploration

| Agent | Description | Use When |
|-------|-------------|----------|
| **scout** | Rapidly maps internal codebase — files, patterns, dependencies | Finding code locations, understanding structure |
| **scout-external** | Explores external resources, APIs, open-source projects | Researching external APIs or libraries |

---

## Dispatching Agents

Claude dispatches agents automatically when appropriate. You can also request it explicitly:

```
"Have the security-auditor review the auth module"
"Ask the database-admin to optimize this query"
"Get the code-reviewer to check my changes"
```

### Parallel Dispatch

For independent tasks, agents run in parallel:

```
You: "Review security, check test coverage, and audit the database schema"

Claude dispatches simultaneously:
  → security-auditor (auth module)
  → tester (coverage analysis)
  → database-admin (schema review)
```

### Agent vs. Skill

| | Skills | Agents |
|---|--------|--------|
| **How** | Auto-trigger by keywords | Dispatched for focused tasks |
| **Context** | Same conversation | Fresh, isolated context |
| **Best for** | Patterns and methodology | Focused independent work |
| **Parallelism** | Sequential | Can run in parallel |
