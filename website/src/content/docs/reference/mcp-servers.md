---
title: MCP Servers
description: Optional MCP server integrations for enhanced capabilities.
---

# MCP Servers

Claude Kit includes optional [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server configurations that extend Claude's capabilities with external tools.

## How MCP Works

MCP servers give Claude access to tools it doesn't have natively — browser automation, persistent memory, real-time documentation, and structured reasoning. They run as local processes that Claude communicates with during your session.

Server configurations live in `.claude/mcp/`.

---

## Available Servers

### Context7

**Purpose**: Real-time library documentation lookup

Fetches current documentation for any library, framework, or API. Use instead of relying on Claude's training data, which may be outdated.

```
You: "How do I set up middleware in Next.js 15?"

Claude fetches current Next.js 15 docs via Context7
→ Answers with up-to-date API syntax
```

**Best for**: API syntax, configuration, version migration, library-specific debugging.

**Config**: `.claude/mcp/context7.json`

---

### Sequential Thinking

**Purpose**: Structured step-by-step reasoning

Provides a tool for multi-step analysis with explicit thought chains. Used automatically by the sequential-thinking skill for complex problems.

```
Complex debugging scenario:
  Step 1: Observe the error → confidence: 0.9
  Step 2: Form hypothesis → confidence: 0.7
  Step 3: Test hypothesis → confidence: 0.85
  Step 4: Verify fix → confidence: 0.95
```

**Best for**: Complex debugging, architecture decisions, security analysis.

**Config**: `.claude/mcp/sequential.json`

---

### Memory

**Purpose**: Persistent knowledge graph across sessions

Stores entities, relationships, and observations that persist across conversations. Claude can recall project decisions, user preferences, and architectural context.

```
Session 1: "We decided to use PostgreSQL RLS for multi-tenancy"
  → Stored as entity + decision observation

Session 2: "What did we decide about multi-tenancy?"
  → Retrieved from memory graph
```

**Best for**: Long-running projects, team knowledge persistence, decision tracking.

---

### Filesystem

**Purpose**: Secure file operations with access controls

Provides sandboxed file operations with configurable allowed directories. Useful for projects that need restricted file access.

**Best for**: Projects with strict file access requirements.

---

### Playwright

**Purpose**: Browser automation for testing

Enables Claude to control a browser for E2E testing, visual verification, and web scraping. Works with the playwright skill for end-to-end test workflows.

```
You: "Test the login flow in the browser"

Claude launches browser via Playwright MCP:
  → Navigate to /login
  → Fill email and password
  → Click submit
  → Verify redirect to /dashboard
  → Take screenshot for evidence
```

**Best for**: E2E testing, visual regression, browser-based verification.

---

## Setup

### Prerequisites

MCP servers require Node.js installed on your system.

### Enabling a Server

1. Check the config file in `.claude/mcp/` for the server you want
2. Install any required dependencies (noted in the config)
3. Restart Claude Code

### Configuration Format

Each server has a JSON config file:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@package/server-name"],
      "env": {}
    }
  }
}
```

See `.claude/mcp/README.md` for detailed setup instructions.

## Skills That Use MCP

| MCP Server | Skills That Benefit |
|------------|-------------------|
| Context7 | All framework/library skills (frontend, backend-frameworks, databases) |
| Sequential | sequential-thinking, systematic-debugging, brainstorming |
| Memory | session-management, brainstorming (persisting design decisions) |
| Playwright | playwright, verification-before-completion |
