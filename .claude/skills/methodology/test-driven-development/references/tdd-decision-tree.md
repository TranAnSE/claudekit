# TDD Decision Tree

Quick reference for deciding when and how to apply Test-Driven Development.

---

## Decision: Should I Use TDD Here?

```
Is this code...
│
├─ Business logic or data transformation?
│  └─ YES: Always TDD. No exceptions.
│
├─ An API endpoint (REST, GraphQL, RPC)?
│  └─ YES: Always TDD. Write request/response tests first.
│
├─ A bug fix?
│  └─ YES: Always TDD. Write a failing test that reproduces the bug first.
│
├─ A utility function or helper?
│  └─ YES: Always TDD. These are the easiest to TDD — pure input/output.
│
├─ A database query or repository method?
│  └─ YES: Always TDD. Test the query behavior, not the SQL syntax.
│
├─ A state machine or workflow?
│  └─ YES: Always TDD. Test each transition.
│
├─ UI layout or styling (CSS, Tailwind, visual positioning)?
│  └─ TDD optional. Visual output is hard to assert meaningfully.
│     Use snapshot tests or visual regression tools instead.
│
├─ Configuration or environment setup?
│  └─ TDD optional. Test that config loads correctly, but don't
│     TDD every config value. Integration tests are more useful.
│
├─ A database migration?
│  └─ TDD optional. Test that migration runs forward and backward.
│     Don't TDD the migration SQL itself.
│
├─ A prototype or spike?
│  └─ TDD optional. Spikes are throwaway. But if the spike becomes
│     real code, stop and add tests before continuing.
│
├─ Third-party integration glue code?
│  └─ TDD the contract, not the integration. Write tests against
│     the interface you expect, mock the external service.
│
└─ Generated code (scaffolding, boilerplate)?
   └─ TDD optional. Test the generator if you wrote it.
      Don't TDD the generated output.
```

---

## Decision Factors

When the tree above doesn't give a clear answer, weigh these factors:

| Factor | Favors TDD | Favors Test-After |
|--------|-----------|-------------------|
| **Testability** | Clear inputs/outputs, deterministic | Heavy side effects, UI rendering |
| **Complexity** | Multiple branches, edge cases | Straightforward single-path logic |
| **Risk** | Failure is costly (data loss, security) | Failure is cosmetic or low-impact |
| **Stability** | Requirements are clear and stable | Requirements are still changing |
| **Team convention** | Team expects TDD | Team doesn't practice TDD |
| **Confidence** | You're unsure how to implement it | You've built this exact thing before |

**Rule of thumb:** If you're unsure, use TDD. The cost of writing a test first is low. The cost of a bug in untested code is high.

---

## The TDD Cycle

```
1. RED    — Write a failing test that defines the desired behavior
2. GREEN  — Write the minimum code to make the test pass
3. REFACTOR — Clean up without changing behavior (tests still pass)
4. REPEAT — Next behavior
```

### Common Mistakes

- **Writing too much test at once** — Test one behavior per cycle
- **Writing implementation before the test fails** — The failing test is the spec
- **Skipping refactor** — Technical debt accumulates in GREEN if you don't clean up
- **Testing implementation details** — Test what it does, not how it does it

---

## Handling Legacy Code Without Tests

Legacy code (code without tests) requires a different entry point into TDD.

### Step 1: Characterization Tests

Before changing anything, write tests that capture current behavior:

```python
# Characterization test — documents what the code DOES, not what it SHOULD do
def test_calculate_total_current_behavior():
    result = calculate_total(items=[{"price": 10, "qty": 2}])
    assert result == 20  # Observed behavior, may or may not be correct
```

### Step 2: Identify the Change Boundary

What's the smallest piece of code you need to change? Draw a boundary around it.

### Step 3: Add Seams

If the code is untestable (hard dependencies, global state), add seams:
- Extract method
- Inject dependencies
- Wrap external calls

### Step 4: TDD the Change

Now that you have characterization tests protecting existing behavior and seams allowing isolation, use the normal RED-GREEN-REFACTOR cycle for your change.

### Step 5: Decide What to Keep

After the change, decide which characterization tests to keep:
- **Keep** tests that document important behavior
- **Replace** tests that covered the code you changed (your TDD tests are better)
- **Remove** tests that only existed to enable your refactoring

---

## TDD by Test Type

| Test Type | TDD Approach |
|-----------|-------------|
| **Unit tests** | Standard RED-GREEN-REFACTOR. One behavior per cycle. |
| **Integration tests** | Write the test against the integration boundary first. May need stubs for external services during RED phase. |
| **API tests** | Define the request and expected response first. Implement handler to make it pass. |
| **E2E tests** | Not typically TDD'd per-cycle. Write E2E tests for critical paths after unit/integration TDD. |

---

## Quick Checklist

Before claiming a task is done with TDD:

- [ ] Every production function has at least one test that was written before the function
- [ ] No test was written after the code it tests (except characterization tests for legacy code)
- [ ] All tests pass
- [ ] Code has been refactored after going GREEN
- [ ] Tests verify behavior, not implementation
