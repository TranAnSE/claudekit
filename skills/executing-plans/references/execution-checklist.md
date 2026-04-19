# Plan Execution Checklist

Step-by-step checklist for executing implementation plans. Follow this sequence for each plan to ensure consistent, high-quality delivery.

---

## Phase 1: Pre-Execution

Complete all items before writing any code.

- [ ] **Read the full plan end-to-end** — Understand the complete scope before starting any task. Do not start task 1 without knowing what task N requires.
- [ ] **Identify the dependency graph** — Which tasks depend on others? Which can run in parallel? Mark the critical path.
- [ ] **Check external dependencies** — API keys available? Services running? Permissions granted? Third-party accounts set up?
- [ ] **Verify the environment**
  - [ ] Correct branch checked out (or worktree created)
  - [ ] Dependencies installed and up to date
  - [ ] Existing tests pass before any changes
  - [ ] Build succeeds from clean state
- [ ] **Clarify ambiguities** — If any task description is unclear, resolve it now. Do not guess during implementation.
- [ ] **Estimate total effort** — Does the sum of task estimates feel realistic given what you know? Flag concerns early.

---

## Phase 2: Per-Task Execution

Repeat for each task in plan order (respecting dependencies).

### Before Starting the Task

- [ ] **Read the task spec completely** — Including files to modify, changes, tests, and verification steps
- [ ] **Confirm dependencies are met** — All prerequisite tasks marked complete and verified
- [ ] **Check current state** — Run tests, confirm the codebase is in a good state before making changes

### During the Task

- [ ] **Write tests first** — If the plan includes tests for this task, write them before the implementation. They should fail initially.
- [ ] **Implement the changes** — Follow the spec. If you need to deviate, document why.
- [ ] **Run the task's specific tests** — All tests for this task must pass
- [ ] **Run the full test suite** — Ensure no regressions from your changes
- [ ] **Complete the task's verification steps** — Every verification item in the plan must be checked

### After Completing the Task

- [ ] **Mark the task complete** — Update the plan document
- [ ] **Check for side effects** — Did anything unexpected break? Are there warnings?
- [ ] **Commit the work** — One commit per task with a clear message referencing the plan
  ```
  feat(scope): task description

  Plan: [plan-name], Task N
  ```
- [ ] **Update the plan if needed** — If you discovered something that affects later tasks, note it now

---

## Phase 3: Post-Execution

Complete after all tasks are done.

### Verification

- [ ] **Run the full test suite** — All tests pass, not just the ones you added
  ```bash
  # Python
  pytest -v --cov=src

  # TypeScript
  pnpm test
  ```
- [ ] **Run the build** — Confirm the project builds without errors
  ```bash
  pnpm build  # or equivalent
  ```
- [ ] **Run linters and type checks** — No new warnings or errors
- [ ] **Manual verification** — Walk through the acceptance criteria in the plan's Verification Plan section
- [ ] **Check for leftover artifacts**
  - [ ] No TODO comments left unresolved
  - [ ] No commented-out code
  - [ ] No debug logging left in place
  - [ ] No temporary files committed

### Review

- [ ] **Self-review the diff** — Read your own changes as if reviewing someone else's PR
  ```bash
  git diff main...HEAD
  ```
- [ ] **Check test quality** — Do tests verify behavior, not implementation? Are edge cases covered?
- [ ] **Check documentation** — If the plan required doc updates, are they done?
- [ ] **Verify acceptance criteria** — Every criterion in the plan marked as met

### Completion

- [ ] **Update plan status** — Mark as "Complete"
- [ ] **Summarize deviations** — Document any changes from the original plan and why
- [ ] **Create PR or merge** — Follow the project's git workflow
- [ ] **Clean up** — Remove worktree if used, close related issues

---

## Quick Reference: Common Failure Points

| Failure | Prevention |
|---------|-----------|
| Skipping plan review, then discovering blockers mid-task | Always complete Phase 1 fully |
| Tests pass in isolation but fail together | Run full suite after every task |
| Deviation from plan without updating it | Document changes as you make them |
| "It works on my machine" | Verify in clean environment |
| Forgetting to commit per-task | Commit immediately after verification |
| Side effects in later tasks | Check for regressions after each task |
