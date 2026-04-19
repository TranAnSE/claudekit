---
name: testing
description: >
  Use when writing, debugging, or configuring unit or integration tests with pytest, Vitest, or Jest. Also activate for fixtures, mocking, coverage, parametrization, jest.mock, vi.mock, jest.fn, vi.fn, conftest.py, vitest.config.ts, jest.config, Testing Library, @jest/globals, or any test configuration.
---

# Testing

## When to Use

- Writing Python tests with pytest (fixtures, parametrize, markers, coverage)
- Testing JavaScript/TypeScript with Vitest (React components, mocking, workspace)
- NestJS or existing projects using Jest
- Debugging test configuration, ESM issues, or flaky tests
- Setting up coverage, CI integration, or test infrastructure

## When NOT to Use

- E2E browser testing — use `playwright`
- Testing anti-patterns and methodology — use `testing-anti-patterns`
- TDD workflow — use `test-driven-development`

---

## Quick Reference

| Framework | Reference | Key features |
|-----------|-----------|-------------|
| pytest | `references/pytest.md` | Fixtures, parametrize, conftest, markers, coverage, async tests |
| Vitest | `references/vitest.md` | vi.mock, vi.fn, Testing Library, MSW, workspace, coverage |
| Jest | `references/jest.md` | jest.mock, jest.fn, @jest/globals, NestJS testing, migration to Vitest |

---

## Best Practices

1. **Name tests descriptively.** `test_[function]_[scenario]_[expected]` (Python) or `it('should [behavior]')` (JS/TS).
2. **Keep tests independent.** Never rely on execution order. Each test sets up its own state.
3. **One assertion focus per test.** Multiple asserts OK if verifying the same behavior.
4. **Mock at the boundary, not in the middle.** Mock external services, databases, and network calls. Don't mock internal functions.
5. **Clear/restore mocks between tests.** `vi.clearAllMocks()` in `beforeEach` or `jest.restoreAllMocks()` in `afterEach`.
6. **Use `userEvent` over `fireEvent`** for React component testing (simulates real user behavior).
7. **Query by role and label, not test IDs** (`getByRole`, `getByLabelText` over `getByTestId`).
8. **Run the full suite in CI with branch coverage.** Local development can use `-x` for fast feedback.

## Common Pitfalls

1. **Forgetting to `await` in async tests.** Omitting `await` makes tests pass vacuously.
2. **Mock hoisting confusion.** `vi.mock()`/`jest.mock()` calls are hoisted — variables referenced in mock implementations may be undefined.
3. **Shared mutable fixtures.** A module-scoped fixture returning a mutable object gets modified by one test and breaks another.
4. **Patching the wrong import path.** Patch where the import is looked up, not where it's defined.
5. **Snapshot overuse.** Developers update snapshots without reviewing diffs. Prefer explicit assertions.
6. **Not cleaning up fake timers.** Forgetting `vi.useRealTimers()` in `afterEach` breaks subsequent tests.
7. **Testing implementation, not behavior.** Assert on outcomes, not internal method calls.
8. **Running Jest where Vitest fits.** For new Vite/React/Next.js projects, Vitest is strictly better.

---

## Related Skills

- `testing-anti-patterns` — Common testing mistakes to avoid
- `test-driven-development` — TDD workflow
- `playwright` — End-to-end browser testing
- `languages` — Language-specific test idioms
