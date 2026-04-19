# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
