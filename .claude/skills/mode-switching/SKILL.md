---
name: mode-switching
argument-hint: "[mode name]"
description: >
  Use when the user wants to switch behavioral modes for the session — adjusting communication style, output format, and problem-solving approach. Trigger for keywords like "mode", "switch mode", "brainstorm mode", "token-efficient", "deep-research mode", "implementation mode", "review mode", "orchestration mode", or any request to change how Claude responds for the remainder of the session.
---

# Mode Switching

## When to Use

- User wants to change response style for the session
- Switching between exploration and execution phases
- Optimizing for token efficiency during high-volume work
- Entering focused review or deep-research mode

## When NOT to Use

- One-off format requests ("give me a shorter answer") — just comply directly
- Switching tools or skills — modes affect style, not capabilities

---

## Available Modes

| Mode | Description | Best For |
|------|-------------|----------|
| `default` | Balanced responses, mix of explanation and code | General tasks |
| `brainstorm` | More questions, multiple alternatives, explore trade-offs | Design, ideation |
| `token-efficient` | Minimal explanations, code-only where possible | High-volume, cost savings |
| `deep-research` | Thorough analysis, citations, confidence levels | Investigation, audits |
| `implementation` | Jump straight to code, progress indicators | Executing plans |
| `review` | Look for issues first, severity levels, actionable feedback | Code review, QA |
| `orchestration` | Task breakdown, parallel execution, result aggregation | Complex parallel work |

## Mode Activation

```
/mode brainstorm              # Switch for session
/mode                         # Show current mode
/mode default                 # Reset
```

## Per-Command Override

Modes can be overridden for a single command without changing the session mode:

```
/feature --mode=implementation "add user profiles"
/review --mode=deep-research src/auth/
/plan --mode=brainstorm "design payment flow"
```

## Recommended Workflows

### Feature Development

```
brainstorm → implementation → review → default
```

### Bug Investigation

```
deep-research → implementation → default
```

### Cost-Conscious Session

```
token-efficient → [work on tasks] → default
```

---

## Mode Files

Mode definitions: `.claude/modes/`

Customize modes by editing these files. Each mode adjusts:
- Communication style and verbosity
- Output format preferences
- Problem-solving approach
- When to ask questions vs proceed

---

## Related Skills

- `writing-concisely` — The token-efficient mode activates this skill's patterns
- `brainstorming` — The brainstorm mode uses this skill's questioning approach
