# Claudekit Plugin

The development-workflow plugin for Claude Code. 35 skills organized around a 6-phase workflow spine (Think → Review → Build → Ship → Maintain → Setup), plus 24 specialized agents and an interactive setup wizard.

## Plugin Structure

- `skills/` — 35 skills (13 user-invocable spine + 22 auto-trigger supporting)
- `agents/` — 24 specialized agents (invoked as `claudekit:<name>`)
- `scripts/` — Hook scripts installed via `/claudekit:init`
- `skills/init/templates/` — Templates for rules, modes, hooks, and MCP configs

## Setup

After installing the plugin, run `/claudekit:init` to scaffold project-level configuration (rules, modes, hooks, MCP servers) into your project's `.claude/` directory.

## Skills — 6-phase spine

13 user-invocable spine skills, typed as `/claudekit:<name>`:

- **Think** — brainstorming, writing-plans
- **Review** — autoplan, plan-ceo-review, plan-eng-review, plan-design-review, plan-devex-review
- **Build** — feature-workflow, test-driven-development, systematic-debugging, verification-before-completion
- **Session** — mode-switching
- **Setup** — init

22 supporting skills auto-trigger by context: execution & parallelism (executing-plans, subagent-driven-development, using-git-worktrees, finishing-a-development-branch, dispatching-parallel-agents, condition-based-waiting), testing (testing, playwright, testing-anti-patterns), debug (root-cause-tracing, defense-in-depth), review (requesting-code-review, receiving-code-review), meta (sequential-thinking, writing-concisely, writing-skills, refactoring), ops (devops, git-workflows, performance-optimization, session-management), security (owasp).

## Conventions

- Skills use YAML frontmatter with `name`, `description`, and optional `user-invocable`, `argument-hint`, `disable-model-invocation`
- Agents use markdown frontmatter with `name`, `description`, `model`, `tools`, `disallowedTools`
- Hook scripts follow "fail open" pattern — errors never block work
- Templates in `skills/init/templates/` are copied to the user's project, not loaded as plugin context
