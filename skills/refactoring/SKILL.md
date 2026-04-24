---
name: refactoring
argument-hint: "[file or function]"
description: >
  Use when improving code structure, readability, or maintainability without changing behavior. Trigger for keywords like "refactor", "clean up", "extract", "simplify", "rename", "restructure", "code smell", "technical debt", "DRY", or any request to improve code quality without adding features. Also activate when code reviews identify structural issues, when functions are too long, or when duplication needs elimination.
---

# Refactoring

## When to Use

- Improving code structure without changing behavior
- Extracting reusable functions or components
- Eliminating code duplication
- Reducing complexity (long functions, deep nesting)
- Renaming for clarity
- Addressing code review feedback about structure

## When NOT to Use

- Adding new features — use `feature-workflow`
- Fixing bugs — use `systematic-debugging` (behavior change, not refactoring)
- Performance optimization — use `performance-optimization`

---

## Quick Reference

| Topic | Reference | Key content |
|-------|-----------|-------------|
| Refactoring patterns | `references/patterns.md` | Extract, inline, rename, move, decompose, introduce parameter object |
| Code smells | `references/code-smells.md` | Detection signals and recommended refactorings |

---

## Safe Refactoring Workflow

1. **Ensure tests pass** before any change
2. **Make one small, behavior-preserving change** at a time
3. **Run tests after each change**
4. **Commit each successful step** independently
5. **Use type checkers** (mypy/tsc) as a secondary safety net
6. **Never mix refactoring with feature/bug changes** in the same commit

---

## Core Patterns

| Pattern | When | Example |
|---------|------|---------|
| Extract function | Long function, repeated logic | Pull 10-line block into named function |
| Inline function | Trivial wrapper adding no clarity | Remove `getAge()` that just returns `this.age` |
| Rename symbol | Name doesn't reveal intent | `x` → `userCount` |
| Introduce parameter object | 4+ related parameters | `(name, email, age)` → `UserInput` |
| Replace conditional with polymorphism | Long if/else or switch chains | Strategy pattern or subclass dispatch |
| Decompose conditional | Complex boolean expression | `isEligible()` instead of `age > 18 && !banned && verified` |
| Extract variable | Complex expression | `const isOverBudget = total > limit * 1.1` |

---

## Code Smell Signals

- **Long function** (>20-30 lines)
- **Long parameter list** (>3-4 params)
- **Duplicated logic** across multiple locations
- **Deep nesting** (>3 levels)
- **Feature envy** — function uses another class's data more than its own
- **Shotgun surgery** — one change requires edits in many files
- **Primitive obsession** — raw strings/dicts instead of typed objects
- **Dead code** — unreachable or unused functions/imports

---

## Python-Specific

- Convert `dict` bags to **dataclasses** or **TypedDict**
- Add **type hints** progressively
- Replace loops with **comprehensions** where clearer
- Use **`@property`** instead of get/set methods
- Use **`Enum`** instead of string constants

## TypeScript-Specific

- Use **discriminated unions** instead of class hierarchies
- Replace `any` with **generics** or **`unknown`** + narrowing
- Replace enums with **`as const`** objects for tree-shaking
- Extract **utility types** (`Pick`, `Omit`, `Partial`)

---

## Best Practices

1. **Rule of three** — extract on the third duplication, not the first.
2. **Tests are the safety net** — never refactor without them.
3. **Small steps** — one rename is better than a big-bang rewrite.
4. **Preserve interfaces** — change internals, not public APIs (unless that's the goal).
5. **Use IDE tooling** — automated rename/move updates all references.

## Common Pitfalls

1. **Refactoring without tests** — no safety net to catch regressions.
2. **Mixing refactoring with features** — makes it impossible to identify behavior changes.
3. **Premature abstraction** — extracting patterns before duplication exists.
4. **Too-large refactors** — big-bang rewrites instead of incremental steps.
5. **Breaking public interfaces** — changing signatures without updating callers.

---

## Related Skills

- `testing` — Ensure test coverage before refactoring
- `writing-concisely` — Refactoring responses can be terse (show before/after)
