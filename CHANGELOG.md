# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.1.0] - 2026-04-24

### Added
- **Planning pipeline** — 5 new skills to pressure-test a written implementation plan before coding:
  - `plan-ceo-review` — Strategic/scope review (ambition, problem clarity, wedge focus, demand reality, future-fit)
  - `plan-eng-review` — Architecture review (data flow, failure modes, edge cases, test matrix, rollback)
  - `plan-design-review` — UX/visual review (hierarchy, consistency, states, accessibility, AI-slop avoidance)
  - `plan-devex-review` — Developer-experience review (TTHW, ergonomics, error copy, docs, magical moments)
  - `autoplan` — Parallel fan-out of all 4 above, consolidated single fix-gate
- **4 new reviewer agents** dispatched by the plan-review skills: `ceo-reviewer`, `eng-reviewer`, `design-reviewer`, `devex-reviewer` (each read-only; fix application happens in the skill's main context)
- **Startup Mode** in `brainstorming` skill — 6 forcing questions (demand reality, status quo, desperate specificity, narrowest wedge, observation, future-fit) with traffic-light gate, activated when the user is exploring a new product idea
- **Save-path conventions** for `brainstorming` (`docs/claudekit/specs/`) and `writing-plans` (`docs/claudekit/plans/`) — previously silent
- Review artifacts saved to `docs/claudekit/reviews/<plan-basename>-<dim>-YYYY-MM-DD.md`

### Changed
- **Reorganized around a 6-phase development-workflow spine** (Think → Review → Build → Ship → Maintain → Setup). README and website docs now front-door 13 user-invocable spine skills; 22 supporting skills auto-trigger silently behind the scenes.
- **Set `user-invocable: true` on 13 spine skills** (previously only `brainstorming` and `init` were typeable): writing-plans, autoplan, plan-ceo-review, plan-eng-review, plan-design-review, plan-devex-review, feature-workflow, test-driven-development, systematic-debugging, verification-before-completion, mode-switching.
- `writing-plans`, `feature-workflow`, and the `planner` agent now reference `autoplan` as the recommended review gate between planning and implementation.
- Totals: **35 skills** (was 49), **24 agents** (unchanged) — updated across README, website docs, plugin manifest, marketplace manifest, and CLAUDE.md.

### Removed
- **14 knowledge skills** dropped to refocus claudekit on workflow/methodology (Claude's base knowledge already covers these domains). Users with strong stack opinions can re-add opinionated knowledge skills in their project's `.claude/skills/`.
  - `api-client`, `authentication`, `backend-frameworks`, `background-jobs`, `caching`, `databases`, `documentation`, `error-handling`, `frontend`, `frontend-styling`, `languages`, `logging`, `openapi`, `state-management`

## [3.0.0] - 2026-04-19

### Changed
- Migrated from clone-and-copy `.claude/` directory to Claude Code plugin format
- Skills moved from `.claude/skills/` to `skills/` at repo root (namespaced as `/claudekit:<name>`)
- Agents moved from `.claude/agents/` to `agents/` at repo root (namespaced as `claudekit:<name>`)
- Hook scripts moved from `.claude/hooks/` to `scripts/` (opt-in via init wizard)
- Rules and modes converted to templates scaffolded by `/claudekit:init`
- MCP server configs now opt-in via `/claudekit:init` with platform auto-detection
- Fixed command injection vulnerabilities in auto-format and notify hook scripts

### Added
- `/claudekit:init` setup wizard — interactive scaffolding for rules, modes, hooks, and MCP servers
- `--all` flag for `/claudekit:init` to skip prompts and install everything
- `.claude-plugin/plugin.json` manifest for plugin distribution
- `.claude-plugin/marketplace.json` for local development testing
- Platform-aware MCP configs (win32 and posix variants)
- `MARKETPLACE.md` with instructions for creating the distribution marketplace
- `CHANGELOG.md`, `LICENSE`, `CLAUDE.md`

### Removed
- `.claude/CLAUDE.md` (project-specific, not distributed with plugin)
- `.claude/settings.json` (too project-specific for plugin distribution)
- Root `.mcp.json` (replaced by opt-in setup via init wizard)

## [2.0.0] - 2026-04-18

### Changed
- Migrated 27 slash commands to skills with YAML frontmatter
- Restructured all skills to flat directory layout with router pattern

### Added
- YAML frontmatter parameters on all 43 skills
- Bundled resources (references/, templates/, scripts/) per skill
- 7 behavioral modes
- 5 rules with path-based activation

## [1.0.0] - 2026-04-17

### Added
- Initial release with 20 agents, 43 skills
- MCP server integrations (Context7, Sequential, Playwright, Memory, Filesystem)
- 3 hooks (auto-format, block-dangerous-commands, notify)
