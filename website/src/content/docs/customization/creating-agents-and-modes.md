---
title: Creating Agents & Modes
description: How to create custom agents and behavioral modes for Claude Kit.
---

# Creating Agents & Modes

Beyond skills, you can create specialized agents for focused tasks and behavioral modes for different work contexts.

---

## Creating Agents

Agents are specialized subagents that Claude dispatches for independent, focused work. Each agent gets a fresh context and specific tool access.

### Agent Structure

Plugin agents live in the `agents/` directory at the plugin root. For project-specific agents, create them in `.claude/agents/`:

```
.claude/agents/
├── my-custom-agent.md
```

### Agent File Format

```markdown
---
name: my-agent
description: One-line description of what this agent does and when to use it.
tools: [Read, Write, Edit, Bash, Grep, Glob]
model: sonnet
---

# My Agent

## Role
[What this agent specializes in]

## Approach
[How it should work through problems]

## Output Format
[What it should return]

## Examples
[Example inputs and expected outputs]
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Agent identifier |
| `description` | Yes | When to dispatch this agent |
| `tools` | No | Tools the agent can use (defaults to all) |
| `model` | No | Model override (sonnet, opus, haiku) |

### Example: Custom Agent

```markdown
---
name: migration-checker
description: Use when running database migrations to verify safety.
  Check for destructive operations, missing rollbacks, and data loss risks.
tools: [Read, Grep, Glob, Bash]
model: sonnet
---

# Migration Checker

## Role
Review database migration files for safety before execution.

## Checklist
1. Check for destructive operations (DROP TABLE, DROP COLUMN)
2. Verify rollback/down migration exists
3. Check for data loss risks (column type changes, NOT NULL without default)
4. Estimate lock duration on large tables
5. Verify migration is idempotent

## Output Format
Return a safety report:
- SAFE: No issues found
- WARNING: Issues that need review (list them)
- BLOCKED: Destructive changes that need approval
```

### When to Create an Agent vs. a Skill

| Use an Agent when... | Use a Skill when... |
|---------------------|---------------------|
| Task needs isolated context | Knowledge should be in main conversation |
| Work can run independently | Patterns apply inline to current work |
| Multiple tasks can parallelize | Guidance is sequential/conversational |
| Fresh perspective needed | Context from conversation matters |

---

## Creating Modes

Modes change Claude's communication style, output format, and problem-solving approach for the duration of a session.

### Mode Structure

After running `/claudekit:init`, built-in modes are installed to `.claude/modes/`. You can add custom modes alongside them:

```
.claude/modes/
├── brainstorm.md          # Installed by /claudekit:init
├── implementation.md      # Installed by /claudekit:init
└── my-custom-mode.md      # Your custom mode
```

### Mode File Format

```markdown
---
name: my-mode
description: One-line description of this mode's behavior.
---

# My Mode

## Communication Style
[How Claude should communicate in this mode]

## Output Format
[What outputs should look like]

## Problem-Solving Approach
[How Claude should approach tasks]

## When to Use
[Best scenarios for this mode]
```

### Example: Custom Mode

```markdown
---
name: pair-programming
description: Interactive pair programming mode with frequent check-ins.
---

# Pair Programming Mode

## Communication Style
- Think out loud — explain reasoning as you code
- Ask before making non-obvious decisions
- Suggest alternatives when multiple approaches exist
- Keep explanations conversational, not formal

## Output Format
- Show code in small chunks (10-20 lines)
- Pause after each chunk for feedback
- Use comments to explain "why", not "what"

## Problem-Solving Approach
- Start with the simplest approach
- Refactor only when the user agrees
- Test each change before moving on
- Never make large changes without discussion

## When to Use
- Learning a new codebase together
- Complex features where design decisions need discussion
- Mentoring or teaching scenarios
```

### Example: Compliance Mode

```markdown
---
name: compliance
description: Strict compliance mode for regulated industries.
---

# Compliance Mode

## Communication Style
- Formal, precise language
- Reference specific regulations when relevant
- Flag compliance risks proactively

## Output Format
- Include audit trail comments in code
- Document all security decisions
- Generate compliance checklists

## Problem-Solving Approach
- Security and compliance over convenience
- Prefer established patterns over novel solutions
- Require explicit approval for any data handling changes
```

## Activating Custom Modes

Once created, switch to your mode naturally:

```
"switch to pair-programming mode"
"use compliance mode"
```

Or reference the mode-switching skill keywords.

## Related Pages

- [Agents Reference](/claudekit/reference/agents/) — All 24 built-in agents
- [Modes Reference](/claudekit/reference/modes/) — All 7 built-in modes
- [Creating Skills](/claudekit/customization/creating-skills/) — Custom skill creation
