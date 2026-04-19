# Refactoring Patterns

## Extract Function

Pull cohesive logic into a named function.

```python
# Before
def process_order(order):
    # validate
    if not order.items:
        raise ValueError("Empty order")
    if order.total < 0:
        raise ValueError("Negative total")
    # ... 50 more lines

# After
def validate_order(order):
    if not order.items:
        raise ValueError("Empty order")
    if order.total < 0:
        raise ValueError("Negative total")

def process_order(order):
    validate_order(order)
    # ... rest of processing
```

## Introduce Parameter Object

Group 4+ related parameters into a single object.

```typescript
// Before
function createUser(name: string, email: string, age: number, role: string) { ... }

// After
interface CreateUserInput {
  name: string;
  email: string;
  age: number;
  role: string;
}
function createUser(input: CreateUserInput) { ... }
```

## Replace Conditional with Polymorphism

```typescript
// Before
function getPrice(type: string, base: number): number {
  if (type === 'premium') return base * 0.8;
  if (type === 'bulk') return base * 0.7;
  return base;
}

// After
const pricingStrategies: Record<string, (base: number) => number> = {
  premium: (base) => base * 0.8,
  bulk: (base) => base * 0.7,
  standard: (base) => base,
};
function getPrice(type: string, base: number): number {
  return (pricingStrategies[type] ?? pricingStrategies.standard)(base);
}
```

## Decompose Conditional

```python
# Before
if age > 18 and not banned and verified and subscription_active:
    grant_access()

# After
def is_eligible(user):
    return user.age > 18 and not user.banned and user.verified and user.subscription_active

if is_eligible(user):
    grant_access()
```

## Extract Variable

```typescript
// Before
if (order.total > 100 && order.items.length > 5 && !order.hasDiscount) { ... }

// After
const isLargeOrder = order.total > 100 && order.items.length > 5;
const qualifiesForDiscount = isLargeOrder && !order.hasDiscount;
if (qualifiesForDiscount) { ... }
```
