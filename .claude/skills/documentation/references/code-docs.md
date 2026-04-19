# Code Documentation Patterns

## Python Docstrings (Google Style)

```python
def calculate_discount(price: float, percentage: float) -> float:
    """Calculate discounted price.

    Args:
        price: Original price in dollars.
        percentage: Discount percentage (0-100).

    Returns:
        The discounted price.

    Raises:
        ValueError: If percentage is not between 0 and 100.

    Example:
        >>> calculate_discount(100.0, 20)
        80.0
    """
```

## TypeScript JSDoc

```typescript
/**
 * Calculate discounted price.
 *
 * @param price - Original price in dollars
 * @param percentage - Discount percentage (0-100)
 * @returns The discounted price
 * @throws {RangeError} If percentage is not between 0 and 100
 *
 * @example
 * calculateDiscount(100, 20); // returns 80
 */
```

## When to Add Inline Comments

- Explain **why**, not what — `# Retry 3x because upstream API is flaky`
- Document workarounds — `// Safari doesn't support this API, fallback to...`
- Clarify non-obvious logic — `# O(1) amortized via lazy deletion`
- Mark TODOs with context — `# TODO(#123): remove after migration complete`

## When NOT to Comment

- Restating the code: `i += 1  # increment i by 1`
- Obvious function names: `def get_user_by_id` needs no docstring explaining it gets a user by ID
- Commented-out code — delete it, git has history
