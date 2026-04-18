---
name: writing-concisely
description: >
  Use this skill when optimizing token usage, reducing response verbosity, or working in high-volume development sessions. Trigger for any mention of token savings, cost optimization, concise output, compressed responses, or the --format=concise/ultra flags. Also applies during repetitive tasks, quick iterations, simple clear requests, or when the user activates token-efficient mode. This is a cross-cutting optimization that applies to all other skills.
---

# Token Optimization

## When to Use

- High-volume development sessions
- Repetitive tasks
- Simple, clear requests
- Cost-sensitive projects
- Quick iterations

## When NOT to Use

- Learning or educational contexts where verbose explanations help the user understand concepts
- Debugging complex issues where detailed analysis and step-by-step reasoning matter
- Security reviews or architecture discussions where thoroughness is more important than brevity

---

## Compression Levels

### Level 1: Concise (30-40% savings)
- Remove conversational filler
- Skip obvious explanations
- Use bullet points
- Shorter variable names in examples

### Level 2: Compact (50-60% savings)
- Code-only responses
- No surrounding prose
- Abbreviated comments
- Reference docs instead of explaining

### Level 3: Ultra (60-70% savings)
- Minimal viable response
- Essential code only
- No comments
- Diff format for changes

---

## Compression Techniques

### Remove Preambles

```markdown
❌ VERBOSE:
"I'll help you with that. Let me analyze the code and provide
a solution. Based on what I see, the issue is..."

✅ CONCISE:
"Issue: null check missing at line 42. Fix:"
```

### Code-Only Responses

```markdown
❌ VERBOSE:
"Here's the implementation. I've added proper error handling
and made sure to follow the existing patterns in your codebase.
The function now validates input and returns early if invalid."

[large code block]

"This should fix the issue. Let me know if you have questions."

✅ CONCISE:
[code block]
```

### Reference Over Explain

```markdown
❌ VERBOSE:
"React's useEffect hook runs after render. The dependency array
controls when it re-runs. Empty array means run once on mount..."

✅ CONCISE:
"Add `userId` to deps array. See: https://react.dev/reference/react/useEffect"
```

### Diff Format for Changes

```markdown
❌ VERBOSE:
"I've updated the file. Here's the complete new version:"
[entire file]

✅ CONCISE:
```diff
- const user = getUser();
+ const user = getUser() ?? defaultUser;
```
Line 42 in user-service.ts
```

---

## Output Templates

### Bug Fix
```
Fix: [brief description]
File: [path:line]
[code or diff]
Verify: [test command]
```

### Feature Addition
```
Added: [feature]
Files: [list]
[code blocks]
Test: [command]
```

### Refactor
```
Refactor: [what]
[diff format changes]
No behavior change.
```

---

## When NOT to Compress

| Situation | Why |
|-----------|-----|
| Complex architecture | Need full context |
| Security issues | Must explain risks |
| Code reviews | Thoroughness required |
| Teaching/explaining | Clarity matters |
| Debugging complex issues | Details help |
| First-time patterns | Context needed |

---

## Activation

### Via Mode
```
Use mode: token-efficient
```

### Via Flag
```
/command --format=concise
/command --format=ultra
```

### Session-Wide
```
For this session, use token-efficient mode.
```

---

## Best Practices

1. **Match compression to task complexity**
   - Simple task → High compression
   - Complex task → Lower compression

2. **Preserve essential information**
   - File paths always included
   - Test commands always included
   - Error context when relevant

3. **Use progressive disclosure**
   - Start concise
   - Expand if asked

4. **Know when to stop compressing**
   - User confusion → Add context
   - Errors occurring → Add detail
   - Review needed → Full output

---

## Related Skills

- All skills — this is a cross-cutting optimization that can be combined with any other skill to reduce token usage while maintaining response quality
