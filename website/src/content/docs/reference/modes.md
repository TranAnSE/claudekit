---
title: Modes Reference
description: All 7 behavioral modes in Claude Kit.
---

# Modes Reference

Modes change how Claude communicates and solves problems. Each mode optimizes behavior for a specific type of task.

## How Modes Work

Switch modes naturally in conversation:

```
"switch to brainstorm mode"
"use implementation mode"
"go into review mode"
```

Modes are installed into your project's `.claude/modes/` via `/claudekit:init`. Each defines communication style, output format, and problem-solving approach.

---

## Available Modes

### Default

The standard balanced mode for general tasks.

- **Communication**: Clear, helpful, balanced detail
- **Output**: Mix of explanation and code
- **Best for**: General development tasks, questions, exploration

---

### Brainstorm

Creative exploration for design and ideation.

- **Communication**: Asks lots of questions, explores alternatives
- **Output**: Options with trade-offs, diagrams, decision matrices
- **Best for**: Feature design, architecture decisions, requirement exploration

**Example**:
```
You: "switch to brainstorm mode"
You: "I need to add search to our product catalog"

Claude asks one question at a time:
  "What search complexity do you need?
   a) Simple text matching (LIKE queries)
   b) Full-text search (PostgreSQL tsvector)
   c) Dedicated search engine (Elasticsearch/Meilisearch)"
```

---

### Implementation

Code-focused execution with minimal prose.

- **Communication**: Terse, action-oriented
- **Output**: Mostly code, minimal explanation
- **Best for**: Executing known tasks, coding from clear specs

**Example**:
```
You: "switch to implementation mode"
You: "add a PATCH /api/users/:id endpoint"

Claude writes code immediately with minimal commentary.
```

---

### Review

Critical analysis for code review and quality assurance.

- **Communication**: Critical, thorough, finds issues
- **Output**: Issue lists with severity, suggestions, security flags
- **Best for**: Code review, QA, pre-merge checks

**Example**:
```
You: "switch to review mode"
You: "review the auth middleware"

Claude examines code critically:
  "CRITICAL: Token expiry not checked after decode (line 42)
   IMPORTANT: Missing rate limiting on login endpoint
   MINOR: Inconsistent error response format"
```

---

### Token-Efficient

Compressed output for high-volume work and cost optimization.

- **Communication**: Minimal prose, maximum density
- **Output**: Code-only when possible, compressed explanations
- **Best for**: Long sessions, repetitive tasks, cost-conscious work
- **Savings**: 30-70% token reduction

**Levels**:

| Level | How to Activate | Savings |
|-------|----------------|---------|
| Concise | "be concise" | 30-40% |
| Ultra | "code only" | 60-70% |
| Session | "switch to token-efficient mode" | 30-70% |

---

### Deep Research

Thorough investigation with evidence and citations.

- **Communication**: Detailed analysis, cites sources
- **Output**: Structured reports, evidence-backed conclusions
- **Best for**: Technology evaluation, incident investigation, audits

**Example**:
```
You: "switch to deep research mode"
You: "analyze our authentication flow for security issues"

Claude produces a structured report:
  "## Findings
   ### 1. Session Token Storage (High Risk)
   Current: localStorage (vulnerable to XSS)
   Recommended: httpOnly cookie
   Evidence: OWASP Session Management Cheat Sheet..."
```

---

### Orchestration

Multi-agent coordination for complex parallel work.

- **Communication**: Status-oriented, progress tracking
- **Output**: Agent dispatch summaries, consolidated results
- **Best for**: Large tasks requiring multiple agents working in parallel

**Example**:
```
You: "switch to orchestration mode"
You: "audit the entire API layer"

Claude coordinates multiple agents:
  "Dispatching 3 agents in parallel:
   → security-auditor: reviewing auth endpoints
   → code-reviewer: reviewing business logic
   → tester: checking coverage gaps
   
   Results consolidated in ~2 minutes..."
```

---

## Mode Comparison

| Mode | Verbosity | Focus | Output Style |
|------|-----------|-------|-------------|
| Default | Medium | Balanced | Explanation + code |
| Brainstorm | High | Exploration | Questions + options |
| Implementation | Low | Execution | Code-first |
| Review | Medium | Quality | Issue lists |
| Token-Efficient | Minimal | Density | Compressed |
| Deep Research | High | Analysis | Reports |
| Orchestration | Medium | Coordination | Status + results |

## Customizing Modes

After running `/claudekit:init`, mode files are markdown in `.claude/modes/`. You can edit the installed modes or create new ones. See [Creating Agents & Modes](/claudekit/customization/creating-agents-and-modes/) for details.
