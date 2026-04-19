# Testing Anti-Pattern Catalog

Quick reference of common testing anti-patterns. Each entry includes: what it looks like, why it's a problem, and how to fix it.

---

## 1. The Ice Cream Cone

**Symptom:** Most tests are E2E or integration tests. Few or no unit tests. The test pyramid is inverted.

**Root cause:** Tests were written after the feature, following user flows instead of testing isolated logic. Or the code is tightly coupled, making unit tests hard to write.

**Impact:** Test suite is slow, brittle, and expensive to maintain. Failures are hard to diagnose because tests cover too much at once.

**Fix:** Refactor toward the test pyramid. Extract business logic into pure functions and unit test them. Reserve E2E tests for critical user flows only. Target ratio: 70% unit, 20% integration, 10% E2E.

---

## 2. The Mockery

**Symptom:** Tests mock so aggressively that they're testing the mocks, not the actual code. The thing under test has all its dependencies replaced.

**Root cause:** Code has too many dependencies, or the developer equates "isolated" with "mock everything."

**Impact:** Tests pass even when the real code is broken. Refactoring breaks every test because mocks are coupled to implementation details.

**Fix:** Only mock external boundaries (network, database, filesystem, clock). Use real implementations for internal collaborators. If you need too many mocks, the code has too many dependencies — refactor first.

---

## 3. The Slow Suite

**Symptom:** Test suite takes more than a few minutes to run. Developers skip tests locally and only run them in CI.

**Root cause:** Too many integration/E2E tests, tests that hit real databases or network, no test parallelization, expensive setup/teardown.

**Impact:** Developers stop running tests, bugs slip through, CI becomes a bottleneck.

**Fix:**
- Profile the suite to find the slowest tests
- Replace slow integration tests with fast unit tests where possible
- Use in-memory databases for integration tests
- Parallelize test execution
- Target: unit suite under 30 seconds, full suite under 5 minutes

---

## 4. The Flaky Test

**Symptom:** Test passes most of the time but fails unpredictably. Re-running usually makes it pass.

**Root cause:** Race conditions, time-dependent logic, shared mutable state between tests, reliance on external services, non-deterministic ordering.

**Impact:** Team loses trust in tests. "Oh that one's flaky" becomes an excuse to ignore real failures. CI results become meaningless.

**Fix:**
- Isolate the flaky test and run it 100 times to confirm flakiness
- Check for: shared state, date/time usage, async timing, test ordering
- Fix the root cause (don't just add retries)
- Quarantine truly unfixable flaky tests while investigating

---

## 5. The Assertion-Free Test

**Symptom:** Test runs code but doesn't assert anything meaningful. It only checks that no exception was thrown.

```python
# Bad — this tests nothing useful
def test_process_data():
    process_data(sample_input)  # No assertion
```

**Root cause:** Test was written to hit a coverage target rather than verify behavior.

**Impact:** False sense of security. Code "has tests" but bugs go undetected.

**Fix:** Every test must assert on the outcome. Ask: "What behavior am I verifying?" If you can't answer, the test isn't testing anything.

```python
# Good — asserts the actual behavior
def test_process_data_calculates_total():
    result = process_data(sample_input)
    assert result.total == 42.0
```

---

## 6. The Copy-Paste Test

**Symptom:** Test file has blocks of nearly identical code repeated with minor variations. Tests are long and look like each other.

**Root cause:** Developer tested a new case by copying an existing test and tweaking values instead of extracting a pattern.

**Impact:** Maintenance nightmare. A change to the interface requires updating dozens of near-identical tests. Easy to introduce subtle bugs in copies.

**Fix:** Use parameterized tests for variations on the same behavior:

```python
# Python — pytest.mark.parametrize
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("", ""),
    ("123", "123"),
])
def test_to_upper(input, expected):
    assert to_upper(input) == expected
```

```typescript
// TypeScript — test.each (vitest/jest)
test.each([
  ["hello", "HELLO"],
  ["", ""],
  ["123", "123"],
])("to_upper(%s) returns %s", (input, expected) => {
  expect(toUpper(input)).toBe(expected);
});
```

---

## 7. The Time Bomb

**Symptom:** Test passes today but will fail on a future date, or fails on certain days/times (new year, month boundary, DST change, leap year).

**Root cause:** Test uses `Date.now()`, `new Date()`, or similar without controlling the clock. Assertions are hardcoded to specific dates.

**Impact:** Sudden failures on specific dates. CI breaks on January 1, or during DST transitions.

**Fix:** Always inject or mock the clock:

```python
# Python — freeze time
from freezegun import freeze_time

@freeze_time("2025-06-15T12:00:00Z")
def test_expiry_check():
    assert is_expired(created_at="2025-06-14T12:00:00Z", ttl_hours=23)
```

```typescript
// TypeScript — vitest fake timers
vi.useFakeTimers();
vi.setSystemTime(new Date("2025-06-15T12:00:00Z"));
expect(isExpired(createdAt, 23)).toBe(true);
vi.useRealTimers();
```

---

## 8. The Hidden Dependency

**Symptom:** Test passes locally but fails in CI, or fails when run in isolation but passes as part of the full suite.

**Root cause:** Test depends on external state that isn't set up by the test itself: a running database, a file on disk, an environment variable, output from a previous test, or global state modified by another test.

**Impact:** Tests are order-dependent, environment-dependent, and unreliable. Debugging failures requires understanding the entire test suite's execution order.

**Fix:**
- Each test must set up and tear down its own state
- Use fixtures (pytest fixtures, beforeEach/afterEach) for shared setup
- Run tests in random order to catch hidden dependencies
  ```bash
  pytest -p randomly    # Python
  vitest --sequence.shuffle  # vitest
  ```
- Never rely on test execution order

---

## Quick Decision Table

| Symptom | Likely Anti-Pattern | First Action |
|---------|-------------------|--------------|
| Tests are slow | Ice Cream Cone or Slow Suite | Profile, find the slowest tests |
| Tests break on refactor | The Mockery | Reduce mocks, test behavior not implementation |
| Tests fail randomly | Flaky Test | Isolate and run 100x |
| High coverage but bugs slip through | Assertion-Free Test | Audit assertions in coverage-targeted tests |
| Tests are hard to maintain | Copy-Paste Test | Extract parameterized tests |
| Tests fail on certain dates | Time Bomb | Inject/mock the clock |
| Tests fail in CI only | Hidden Dependency | Run locally in random order |
| Tests pass but code is clearly broken | The Mockery or Assertion-Free | Check what's actually being asserted |
