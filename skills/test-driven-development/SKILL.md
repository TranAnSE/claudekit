---
name: test-driven-development
description: >
  Use when writing new features, fixing bugs, or changing any behavior in production code. Activate for keywords like "implement", "add feature", "fix bug", "write code", "build", "create endpoint", "add functionality", or any task that will result in production code changes. Also trigger when the user asks to refactor existing code, when tests need to be written, or when someone says "TDD". This skill should be the default for ALL implementation work -- no production code without a failing test first.
---

# Test-Driven Development (TDD)

## When to Use

- New feature development
- Bug fixes (write test that reproduces bug first)
- Refactoring (ensure tests exist before changing)
- Any behavior change

## When NOT to Use

- Prototyping or throwaway code with explicit user approval to skip tests
- Configuration-only changes (e.g., environment variables, CI config, linter rules)
- Documentation updates that do not affect runtime behavior

---

## The Red-Green-Refactor Cycle

### 1. RED: Write Failing Test

Write a minimal test demonstrating the desired behavior:

```typescript
describe('calculateTotal', () => {
  it('should sum item prices', () => {
    const items = [{ price: 10 }, { price: 20 }];
    expect(calculateTotal(items)).toBe(30);
  });
});
```

**Python equivalent:**

```python
# tests/test_cart.py
def test_calculate_total_sums_item_prices():
    items = [{"price": 10}, {"price": 20}]
    assert calculate_total(items) == 30
```

### 2. VERIFY RED: Confirm Test Fails

Run the test and confirm it fails **for the right reason**:

```bash
# TypeScript
npm test -- --grep "sum item prices"
# Expected: FAIL — calculateTotal is not defined

# Python
pytest tests/test_cart.py -v
# Expected: FAIL — NameError: name 'calculate_total' is not defined
```

**Critical**: The failure should be because the feature doesn't exist, not because of typos or syntax errors.

### 3. GREEN: Write Minimal Code

Write the simplest code that makes the test pass:

```typescript
function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}
```

```python
# src/services/cart.py
def calculate_total(items: list[dict]) -> int:
    return sum(item["price"] for item in items)
```

**Don't over-engineer**. If the test passes with simple code, stop.

### 4. VERIFY GREEN: Confirm Test Passes

Run the test and confirm it passes:

```bash
# TypeScript
npm test -- --grep "sum item prices"
# Expected: PASS

# Python
pytest tests/test_cart.py -v
# Expected: PASS
```

### 5. REFACTOR: Clean Up

With green tests, refactor safely:
- Extract functions
- Rename variables
- Remove duplication
- Run tests after each change

---

## The Non-Negotiable Rule

**NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST**

This is not a guideline. It's a rule.

### What If I Already Wrote Code?

Delete it. Completely.

```
WRONG: "I'll keep this code as reference while writing tests"
RIGHT: Delete the code, write test, rewrite implementation
```

### Why So Strict?

- Code written before tests wasn't driven by tests
- Keeping it as reference leads to rationalization
- Tests written after code often just verify what was written
- True TDD produces different (usually better) designs

---

## Test Quality Standards

### One Behavior Per Test

```typescript
// BAD: Multiple behaviors
it('should validate and save user', () => {
  expect(validateUser(user)).toBe(true);
  expect(saveUser(user)).toBe(1);
});

// GOOD: Single behavior
it('should validate user email format', () => {
  expect(validateUser({ email: 'test@example.com' })).toBe(true);
});

it('should save valid user', () => {
  const user = createValidUser();
  expect(saveUser(user)).toBe(1);
});
```

### Clear Naming

Test names should describe the behavior:

```typescript
// BAD
it('test1', () => {});
it('calculateTotal', () => {});

// GOOD
it('should return 0 for empty cart', () => {});
it('should apply discount when coupon is valid', () => {});
```

### Real Code Over Mocks

Use real implementations when possible:

```typescript
// PREFER: Real database (test container)
const db = await startTestDatabase();
const result = await userRepo.save(user);

// AVOID: Excessive mocking
const mockDb = { save: jest.fn().mockResolvedValue(1) };
```

```python
# PREFER: Real database (test fixture)
@pytest.fixture
async def db_session(async_engine):
    async with AsyncSession(async_engine) as session:
        yield session

async def test_save_user(db_session):
    user = User(email="test@example.com", name="Test")
    db_session.add(user)
    await db_session.commit()
    assert user.id is not None

# AVOID: Excessive mocking
def test_save_user_mocked():
    mock_db = MagicMock()
    mock_db.add.return_value = None  # proves nothing
```

### Test Observable Behavior

Test what the code does, not how it does it:

```typescript
// BAD: Testing implementation
it('should call helper function', () => {
  calculateTotal(items);
  expect(helperFn).toHaveBeenCalled();
});

// GOOD: Testing behavior
it('should return correct total', () => {
  expect(calculateTotal(items)).toBe(30);
});
```

---

## Common Rationalizations (Reject These)

### "I'll write tests after"

Tests written after code verify what was written, not what should happen. The test can't prove the code is correct if it was shaped to match existing code.

### "Manual testing is enough"

Ad-hoc testing is not systematic. It misses edge cases, isn't repeatable, and doesn't prevent regressions.

### "This code is too simple to test"

Simple code breaks too. A test takes seconds and provides permanent verification.

### "I don't have time"

TDD is faster in the medium term. Debugging time saved far exceeds test-writing time.

### "I already wrote it, might as well keep it"

Sunk cost fallacy. Delete and rewrite properly.

---

## Edge Cases to Test

Always include tests for:

- Empty inputs
- Null/undefined values
- Boundary conditions
- Error scenarios
- Large inputs
- Invalid inputs

```typescript
describe('calculateTotal', () => {
  it('should return 0 for empty array', () => {
    expect(calculateTotal([])).toBe(0);
  });

  it('should handle null items array', () => {
    expect(() => calculateTotal(null)).toThrow();
  });

  it('should handle negative prices', () => {
    const items = [{ price: -10 }, { price: 20 }];
    expect(calculateTotal(items)).toBe(10);
  });
});
```

```python
def test_calculate_total_empty_list():
    assert calculate_total([]) == 0

def test_calculate_total_none_raises():
    with pytest.raises(TypeError):
        calculate_total(None)

def test_calculate_total_negative_prices():
    items = [{"price": -10}, {"price": 20}]
    assert calculate_total(items) == 10
```

---

## Framework-Specific TDD Patterns

### FastAPI endpoint TDD

Write the test with `httpx.AsyncClient` first, then implement the route:

```python
# 1. RED — test first
import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_create_order_returns_201(client: AsyncClient):
    response = await client.post("/api/orders", json={"item": "widget", "quantity": 2})
    assert response.status_code == 201
    assert response.json()["item"] == "widget"

# 2. GREEN — implement route
from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter(prefix="/api/orders")

class CreateOrderRequest(BaseModel):
    item: str
    quantity: int

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_order(body: CreateOrderRequest):
    return {"id": "ord_1", "item": body.item, "quantity": body.quantity}
```

### NestJS endpoint TDD

Write the test with `supertest` first, then implement the controller:

```typescript
// 1. RED — test first
it('POST /orders — creates order', () =>
  request(app.getHttpServer())
    .post('/orders')
    .send({ item: 'widget', quantity: 2 })
    .expect(201)
    .expect((res) => {
      expect(res.body.item).toBe('widget');
    }));

// 2. GREEN — implement controller
@Post()
@HttpCode(HttpStatus.CREATED)
create(@Body() dto: CreateOrderDto) {
  return this.ordersService.create(dto);
}
```

### React component TDD

Write the test with Testing Library first, then implement the component:

```typescript
// 1. RED — test first
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

it('should call onSubmit with form data', async () => {
  const onSubmit = vi.fn();
  render(<OrderForm onSubmit={onSubmit} />);

  await userEvent.type(screen.getByLabelText('Item'), 'widget');
  await userEvent.click(screen.getByRole('button', { name: /submit/i }));

  expect(onSubmit).toHaveBeenCalledWith(expect.objectContaining({ item: 'widget' }));
});

// 2. GREEN — implement component
export function OrderForm({ onSubmit }: { onSubmit: (data: OrderData) => void }) {
  // minimal implementation to pass the test
}
```

---

## TDD Catches Bugs

The methodology catches bugs before commit:
- Writing test first forces you to think about edge cases
- Seeing test fail proves it can catch failures
- Green bar confirms the fix works
- Test prevents regression forever

This is faster than:
1. Write code
2. Manual test (miss edge case)
3. Ship
4. Bug reported
5. Debug
6. Fix
7. Ship again

---

## Related Skills

- `verification-before-completion` -- Ensures tests are actually run and passing before claiming work is done
- `testing-anti-patterns` -- Avoid common testing mistakes that undermine TDD effectiveness
- `pytest` -- Python-specific testing patterns and best practices for TDD
- `vitest` -- TypeScript/JavaScript-specific testing patterns and best practices for TDD
- `writing-plans` — Planning implementation tasks for TDD workflow
