# Claude Kit

The development-workflow plugin for Claude Code. Opinionated skills and agents that teach Claude how to think, plan, review, and ship — so you don't spend your context window reinventing process.

## Features

- **35 Skills** organized around a 6-phase workflow: Think → Review → Build → Ship → Maintain → Setup
- **13 user-invocable spine skills** — typed directly as `/claudekit:<name>`, the rest auto-trigger by context
- **24 Specialized Agents** — planners, reviewers, implementers, and 4 plan-dimension reviewers
- **Interactive Setup Wizard** — `/claudekit:init` scaffolds rules, modes, hooks, and MCP configs
- **7 Behavioral Modes** — task-specific response optimization (installed via init)
- **MCP Integrations** — Context7, Sequential Thinking, Playwright, Memory, Filesystem (configured via init)

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
├── skills/                    # 35 skills (auto-triggered; 13 user-invocable)
│   ├── init/                  # Setup wizard (/claudekit:init)
│   │   ├── SKILL.md
│   │   └── templates/         # Rules, modes, hooks, MCP templates
│   ├── brainstorming/
│   ├── systematic-debugging/
│   └── ...
├── agents/                    # 24 specialized agents
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

### Plan Review
| Agent | Description |
|-------|-------------|
| `claudekit:ceo-reviewer` | Strategic/scope review of a written plan (ambition, problem clarity, wedge focus, demand reality, future-fit) |
| `claudekit:eng-reviewer` | Architecture review (data flow, failure modes, edge cases, test matrix, rollback) |
| `claudekit:design-reviewer` | UX/visual plan review (hierarchy, consistency, states, accessibility, AI-slop avoidance) |
| `claudekit:devex-reviewer` | Developer-experience review (TTHW, ergonomics, error copy, docs structure, magical moments) |

## Skills

Claude Kit is organized around a **6-phase development workflow**. Each phase has a small set of spine skills you invoke directly (`/claudekit:<name>`); supporting skills auto-trigger behind the scenes when relevant.

### 🧠 Think — explore ideas, produce a spec

| Skill | Description |
|-------|-------------|
| **brainstorming** | Interactive idea exploration, one question at a time. Includes Startup Mode (6 forcing questions) for new product ideas |
| **writing-plans** | Break a spec into bite-sized tasks with exact code, file paths, and test commands |

### 🔍 Review — pressure-test the plan before coding

| Skill | Description |
|-------|-------------|
| **autoplan** | Run all 4 plan-review dimensions in parallel, consolidate into one fix gate |
| **plan-ceo-review** | Strategy review — ambition, problem clarity, wedge focus, demand reality, future-fit |
| **plan-eng-review** | Architecture review — data flow, failure modes, edge cases, test matrix, rollback |
| **plan-design-review** | UX review — information hierarchy, visual consistency, state coverage, accessibility |
| **plan-devex-review** | Developer experience review — TTHW, API/CLI ergonomics, error copy, docs, magical moments |

Each plan-review skill dispatches a dimension-specific reviewer agent, scores 0-10 on 5 sub-dimensions, proposes concrete fixes, and applies user-selected fixes to the plan.

### 🔨 Build — implement with discipline

| Skill | Description |
|-------|-------------|
| **feature-workflow** | End-to-end orchestrator: requirements → plan → review → implement → test → review |
| **test-driven-development** | Red-green-refactor cycle — no production code without a failing test first |
| **systematic-debugging** | 4-phase root-cause investigation — gather, hypothesize, test, prove |
| **verification-before-completion** | Mandatory pre-completion gate — evidence before assertions |

### 🎛️ Session & Setup

| Skill | Description |
|-------|-------------|
| **mode-switching** | Switch behavioral modes (brainstorm, token-efficient, deep-research, implementation, review) |
| **init** | Interactive wizard — scaffolds rules, modes, hooks, and MCP configs into your project |

### Also Included — 22 supporting skills (auto-trigger, non-user-invocable)

These activate silently when Claude detects a matching context. You don't invoke them directly, but they shape how Claude works.

| Category | Skills |
|----------|--------|
| **Execution & Parallelism** | executing-plans, subagent-driven-development, using-git-worktrees, finishing-a-development-branch, dispatching-parallel-agents, condition-based-waiting |
| **Testing Discipline** | testing, playwright, testing-anti-patterns |
| **Debug Techniques** | root-cause-tracing, defense-in-depth |
| **Review Etiquette** | requesting-code-review, receiving-code-review |
| **Reasoning & Meta** | sequential-thinking, writing-concisely, writing-skills, refactoring |
| **Operations** | devops, git-workflows, performance-optimization, session-management |
| **Security** | owasp |

### Bundled Resources

Spine and supporting skills include progressive-disclosure resources loaded on demand:

| Resource Type | Purpose |
|---------------|---------|
| **references/** | Cheat sheets, decision trees, pattern catalogs |
| **templates/** | Starter files, boilerplate, configs |
| **scripts/** | Executable helpers for deterministic tasks |

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
brainstorming -> writing-plans -> autoplan -> feature-workflow -> requesting-code-review -> git-workflows
```

> `autoplan` pressure-tests the plan on strategy, architecture, design, and DX before implementation begins — optional but recommended for non-trivial features.

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
