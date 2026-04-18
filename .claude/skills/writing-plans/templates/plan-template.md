# [Feature Name] Implementation Plan

> **Author:** [name]
> **Date:** [date]
> **Status:** Draft | In Review | Approved | In Progress | Complete
> **Estimated Total:** [X hours/days]

---

## Context

### Problem Statement
[One paragraph describing what problem this solves and why it matters now.]

### Background
[Any relevant context: prior decisions, related features, technical debt involved.]

### Goals
- [Primary goal]
- [Secondary goal]

### Non-Goals
- [What this plan explicitly does NOT address]

---

## Tasks

### Task 1: [Name] (estimated: Xmin)

**Description:** [What this task accomplishes and why it's needed.]

**Files to modify:**
- `path/to/file.ts` — [what changes]
- `path/to/other.py` — [what changes]

**New files:**
- `path/to/new-file.ts` — [purpose]

**Changes:**
1. [Specific change with enough detail to implement without ambiguity]
2. [Next change]

**Tests:**
- [ ] [Test description — what behavior is verified]
- [ ] [Edge case test]

**Verification:**
- [ ] [How to verify this task is complete — command to run, behavior to observe]

---

### Task 2: [Name] (estimated: Xmin)

**Description:** [What this task accomplishes.]

**Dependencies:** Task 1 (requires [specific output])

**Files to modify:**
- `path/to/file.ts` — [what changes]

**Changes:**
1. [Specific change]
2. [Next change]

**Tests:**
- [ ] [Test description]

**Verification:**
- [ ] [Verification step]

---

### Task 3: [Name] (estimated: Xmin)

[Repeat the same structure. Add as many tasks as needed.]

---

## Dependencies

### Internal Dependencies
| Task | Depends On | Reason |
|------|-----------|--------|
| Task 2 | Task 1 | [Why] |

### External Dependencies
- [ ] [External service, API key, environment setup, etc.]
- [ ] [Approval or decision needed from someone]

### Parallel Work
[Which tasks can be done simultaneously? Group them.]

- **Group A (independent):** Task 1, Task 3
- **Group B (requires Group A):** Task 2, Task 4

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [What could go wrong] | Low/Med/High | Low/Med/High | [How to prevent or handle it] |

---

## Verification Plan

### Automated Checks
```bash
# Run full test suite
[test command]

# Run type checks
[type check command]

# Run linter
[lint command]
```

### Manual Checks
- [ ] [Specific scenario to test manually]
- [ ] [Edge case to verify by hand]

### Acceptance Criteria
- [ ] [Criterion 1 — ties back to Goals section]
- [ ] [Criterion 2]

---

## Notes

[Any additional context, open questions, or decisions to revisit.]

---

## Usage Instructions

**To use this template:**

1. Copy this file and rename it: `plan-[feature-name].md`
2. Fill in all sections. If a section doesn't apply, write "N/A" rather than deleting it
3. For **standard plans**: tasks should be 15-60 minutes each
4. For **detailed plans** (`--detailed`): tasks should be 2-5 minutes with exact code snippets
5. Every task must have at least one verification step
6. Every task must list the specific files it touches
7. Remove these usage instructions from your copy
