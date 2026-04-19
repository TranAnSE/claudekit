---
title: Introduction
description: Learn what Claude Kit is and how it accelerates your development workflow.
---

# Introduction to Claude Kit

Claude Kit is an open-source toolkit that transforms Claude Code into a production-ready AI development team. It provides auto-triggered skills, specialized agents, and intelligent modes that accelerate your development workflow.

## What is Claude Kit?

Claude Kit is a `.claude` folder you add to your project containing:

- **43 Skills** — Knowledge modules that auto-trigger based on what you're doing (debugging, planning, testing, etc.)
- **20 Agents** — Specialized subagents for focused tasks (code review, security audit, database design, etc.)
- **7 Modes** — Behavioral configurations that optimize Claude for specific task types

Skills activate automatically based on keywords in your conversation. No commands to memorize — just describe what you want to do.

## Why Claude Kit?

### The Problem with Raw Claude Code

| Problem | Symptom |
|---------|---------|
| **Context Spirals** | Token budgets run out, Claude loses track of what it was doing |
| **Inconsistent Output** | Quality varies wildly between sessions |
| **No Structure** | Every session starts from scratch |
| **Missing Expertise** | Claude doesn't know your team's patterns and standards |

### How Claude Kit Helps

1. **Auto-Triggered Skills** — Say "fix this bug" and systematic-debugging activates. Say "plan this" and brainstorming kicks in.
2. **Specialized Agents** — Dispatch focused subagents for code review, testing, security audits, and more.
3. **Consistent Quality** — Built-in TDD enforcement, verification before completion, and code review workflows.
4. **Full Customization** — Add your own skills, agents, and modes.

## How Skills Work

Skills are the core of Claude Kit. They trigger automatically based on keywords:

```
You: "I need to add user authentication to our app"
     ↓ triggers: brainstorming, authentication, backend-frameworks

You: "There's a TypeError in the UserService"
     ↓ triggers: systematic-debugging, root-cause-tracing

You: "Let's write tests for the API endpoints"
     ↓ triggers: testing, test-driven-development
```

No slash commands needed — Claude reads your intent and activates the right skills.

## Who is Claude Kit For?

- **Solo developers** who want to ship faster
- **Small teams (1-3 developers)** working on multi-stack projects
- **Anyone using Claude Code** who wants more structure and consistency

## Next Steps

1. [Install Claude Kit](/claudekit/getting-started/installation/) — Add it to your project
2. [Configuration](/claudekit/getting-started/configuration/) — Customize for your project
3. [Skills Reference](/claudekit/reference/skills/) — Browse all 43 skills
