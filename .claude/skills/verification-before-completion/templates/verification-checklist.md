# Verification Checklist

Use this checklist before claiming any work is complete. Copy it into your task, PR, or plan and fill in the specifics. Every box must be checked with evidence — not assumptions.

---

## Core Verification

### Tests

- [ ] **All existing tests pass**
  - Command: `___`
  - Output: [paste summary or confirm "all N tests passed"]

- [ ] **New tests added for new behavior**
  - Test files: `___`
  - Coverage of changed code: `___`%

- [ ] **Edge cases tested**
  - [ ] Empty/null inputs
  - [ ] Boundary values
  - [ ] Error conditions
  - [ ] Concurrent access (if applicable)

### Build

- [ ] **Build succeeds with no errors**
  - Command: `___`
  - Output: [confirm clean build]

- [ ] **No new warnings introduced**
  - Linter: `___`
  - Type checker: `___`

### Manual Verification

- [ ] **The specific change works as intended**
  - What I did: [exact steps taken]
  - What I observed: [exact result]
  - What was expected: [matches requirement]

- [ ] **Related functionality still works**
  - Checked: [list related features tested]

---

## Safety Checks

### No Unintended Side Effects

- [ ] **Reviewed the full diff** — No accidental changes to unrelated files
  ```bash
  git diff --stat
  ```

- [ ] **No debug code left in place** — No `console.log`, `print()`, `debugger`, `TODO: remove`

- [ ] **No commented-out code** — Either the code is needed or it isn't

### Error Handling

- [ ] **Errors produce clear messages** — Not generic "something went wrong"
- [ ] **Errors don't leak sensitive information** — No stack traces, internal paths, or credentials in user-facing errors
- [ ] **Failure modes are graceful** — The system degrades rather than crashes

### Security

- [ ] **No hardcoded secrets** — API keys, passwords, tokens are in environment variables
- [ ] **Input is validated** — User input is checked before processing
- [ ] **Output is encoded** — Rendered content is escaped appropriately
- [ ] **No new `eval()` or dynamic code execution**
- [ ] **Dependencies are from trusted sources** — No typosquatting, pinned versions

---

## Documentation

- [ ] **Code is self-documenting** — Clear names, obvious structure
- [ ] **Complex logic has comments** — Explaining WHY, not WHAT
- [ ] **Public API changes are documented** — Updated docstrings, OpenAPI specs, README
- [ ] **Breaking changes are called out** — In commit message, PR description, or changelog

---

## Completion Criteria

- [ ] **All acceptance criteria from the plan/ticket are met**
  - [ ] Criterion 1: ___
  - [ ] Criterion 2: ___

- [ ] **The change has been verified with actual commands, not just code reading**

- [ ] **Confidence level:** High / Medium / Low
  - If Medium or Low, explain what additional verification would increase confidence: ___

---

## Evidence Summary

Record the key evidence here for reviewers:

| Check | Evidence |
|-------|---------|
| Tests pass | [command + result] |
| Build clean | [command + result] |
| Manual test | [steps + result] |
| No regressions | [how verified] |

---

## Usage Notes

- **Do not check boxes without evidence.** "I think it works" is not verification.
- **Run commands and observe output.** Paste or summarize actual results.
- **N/A is acceptable** for items that genuinely don't apply, but add a note explaining why.
- **If confidence is low**, list what would increase it and discuss with the team before marking complete.
