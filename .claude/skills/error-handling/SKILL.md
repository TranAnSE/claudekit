---
name: error-handling
description: >
  Use when writing try/catch blocks, creating custom error classes, implementing retry logic, designing error boundaries in React, building API error responses, or handling failures gracefully. Also activate for any code dealing with exceptions, error propagation, graceful degradation, or fault tolerance.
---

# Error Handling Patterns

## When to Use

- Building API endpoints that must return consistent error responses
- Creating custom exception hierarchies for a domain model
- Implementing retry logic for unreliable network calls or external services
- Designing React error boundaries for component-level fault isolation
- Wrapping third-party libraries that throw unpredictable errors
- Converting between error representations at architectural boundaries (e.g., domain errors to HTTP errors)
- Adopting the Result pattern to avoid exceptions for expected failure paths

## When NOT to Use

- Simple one-off scripts or throwaway prototypes where unhandled crashes are acceptable
- Configuration files, static data, or declarative markup with no runtime logic
- Pure data transformation functions where invalid input should be prevented by types, not caught at runtime

---

## Quick Reference

| Pattern | Description |
|---------|-------------|
| Custom Error Classes | Domain-specific error hierarchy with error codes, messages, and detail metadata |
| Error Boundaries (React) | Component-level fault isolation using `react-error-boundary` or class-based boundaries |
| Retry with Backoff | Exponential backoff + jitter decorator/wrapper for transient failures |
| Circuit Breaker | Short-circuit calls to unhealthy dependencies, fall back to degraded state |
| Feature-Flag Degradation | Graceful UI/service degradation controlled by feature flags |
| API Error Responses | Consistent RFC 7807 Problem Details payloads with global exception handlers |
| Error Logging | Structured context (request ID, error code, stack trace) for observability |
| Result Pattern | Discriminated union / Result type for expected failure paths without exceptions |

## Language References

See `references/python-patterns.md` for Python examples.

See `references/typescript-patterns.md` for TypeScript/React examples.

---

## Best Practices

1. **Catch specific exceptions, not bare `except` or `catch`.** A catch-all hides bugs. Catch only the errors you know how to handle and let everything else propagate.

2. **Translate errors at architectural boundaries.** A database `IntegrityError` should become a domain `DuplicateEntryError` at the repository layer, then an HTTP 409 at the API layer. Each layer speaks its own error language.

3. **Preserve the original cause.** Always chain the original exception (`raise X from original` in Python, `{ cause }` in TypeScript) so the root cause is visible in logs and debuggers.

4. **Fail fast, recover high.** Detect errors as early as possible (validate inputs at the boundary) but handle them at the highest level that has enough context to decide what to do (e.g., return an HTTP response, show a fallback UI).

5. **Never swallow errors silently.** An empty `except: pass` or `catch {}` is almost always a bug. At minimum, log the error. If you intentionally ignore it, leave a comment explaining why.

6. **Use the Result pattern for expected failures.** When a function can legitimately fail (parsing, validation, lookups), return a Result instead of throwing. Reserve exceptions for truly unexpected situations.

7. **Make errors actionable.** Every error message should help the reader fix the problem. Include what happened, what was expected, and what the caller can do about it. `"User not found"` is worse than `"User with id '123' not found. Verify the id and check that the user has not been deleted."`.

8. **Test the error paths.** Write explicit tests for every error branch. Verify the error type, message, and status code. Error paths that are never tested are error paths that will break in production.

---

## Common Pitfalls

1. **Catching too broadly.** Using `except Exception` or `catch (e: any)` silences programming errors like `TypeError` or `ReferenceError` that should crash loudly during development.

2. **Logging and re-throwing without deduplication.** If every layer logs the same error, you get five log entries for one failure. Log at the outermost handler and let inner layers propagate.

3. **Returning error data in the wrong shape.** Mixing `{ error: "..." }`, `{ message: "..." }`, and `{ errors: [...] }` across endpoints forces every client to handle multiple formats. Pick one shape and enforce it globally.

4. **Leaking internal details to clients.** Stack traces, database table names, and file paths in API responses are a security risk. Sanitize errors before they leave the server.

5. **Retrying non-idempotent operations.** Retrying a `POST /orders` that partially succeeded can create duplicate orders. Only retry operations that are safe to repeat, or use idempotency keys.

6. **Ignoring async error boundaries.** In React, error boundaries do not catch errors inside event handlers or async callbacks. Use try/catch inside `onClick`, `useEffect` cleanup, and promise chains separately.

---

## Related Skills

- `logging` - Structured logging setup and conventions
- `api-client` - HTTP client wrappers with built-in error handling
- `owasp` - Preventing information leakage through error messages
- `python` - Python exception syntax and idioms
- `typescript` - TypeScript error types and narrowing
