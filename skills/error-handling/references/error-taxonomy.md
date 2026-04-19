# Error Taxonomy Quick Reference

## Two Fundamental Categories

### Operational Errors (Expected, Recoverable)

Errors that occur in correctly written programs due to external conditions.

**Response**: Handle gracefully. Log, retry, return error to user.

| Category | Description | HTTP Status | Example |
|----------|-------------|-------------|---------|
| Validation | Invalid input data | `400` | Missing required field, wrong format |
| Authentication | Identity not established | `401` | Missing/expired/invalid token |
| Authorization | Insufficient permissions | `403` | User lacks role for this action |
| Not Found | Resource does not exist | `404` | Item with given ID not in DB |
| Conflict | State conflict | `409` | Duplicate email, concurrent edit |
| Rate Limit | Too many requests | `429` | API quota exceeded |
| Payload Too Large | Request body too big | `413` | File upload exceeds limit |
| Unprocessable | Valid syntax, invalid semantics | `422` | Transfer amount exceeds balance |
| External Dependency | Third-party service failed | `502` / `503` | Payment gateway timeout |
| Service Unavailable | System overloaded or in maintenance | `503` | DB connection pool exhausted |

### Programmer Errors (Bugs, Fix the Code)

Errors caused by mistakes in the code itself.

**Response**: Fix the code. Do NOT catch and continue. Crash, log, alert.

| Category | Example | Fix |
|----------|---------|-----|
| TypeError | Calling method on undefined | Add null check or fix data flow |
| ReferenceError | Using undeclared variable | Fix variable name/scope |
| Assertion failure | Invariant violated | Fix logic that broke invariant |
| Wrong argument type | Passing string where number expected | Fix caller or add validation |
| Missing error handling | Unhandled promise rejection | Add try/catch or .catch() |
| Off-by-one | Array index out of bounds | Fix loop/index logic |

---

## Error Handling by Category

### Validation Errors (400)

```python
# Python/FastAPI
from pydantic import BaseModel, validator

class CreateUser(BaseModel):
    email: str
    age: int

    @validator("age")
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError("Age must be between 0 and 150")
        return v
```

```typescript
// TypeScript
class ValidationError extends AppError {
  constructor(public fields: Record<string, string>) {
    super("Validation failed", 400);
  }
}
```

### Authentication Errors (401)

| Scenario | Response | Action |
|----------|----------|--------|
| No token provided | 401 + `WWW-Authenticate` header | Client should authenticate |
| Token expired | 401 + error code `token_expired` | Client should refresh token |
| Token invalid | 401 + error code `invalid_token` | Client should re-authenticate |

### Not Found (404)

| Scenario | Use 404? |
|----------|----------|
| Resource by ID doesn't exist | Yes |
| Search returns no results | **No** -- return empty list with 200 |
| Resource soft-deleted | Depends on visibility rules |
| User lacks access to resource | Consider 403, or 404 to hide existence |

### Conflict (409)

| Scenario | Resolution |
|----------|------------|
| Duplicate unique field | Return which field conflicts |
| Optimistic locking failure | Return current version, client retries |
| State transition invalid | Return current state and valid transitions |

### External Dependency (502/503)

| Strategy | When |
|----------|------|
| Retry with backoff | Transient failures (timeouts, 503) |
| Circuit breaker | Repeated failures from same service |
| Fallback / degraded mode | Non-critical dependency |
| Queue for later | Async-compatible operations |

---

## Error Response Format

### Standard Error Response (JSON)

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      { "field": "email", "message": "Invalid email format" },
      { "field": "age", "message": "Must be a positive number" }
    ],
    "request_id": "req_abc123"
  }
}
```

### Error Code Convention

| Code Pattern | Meaning |
|-------------|---------|
| `VALIDATION_ERROR` | Input validation failed |
| `AUTH_TOKEN_EXPIRED` | Token needs refresh |
| `RESOURCE_NOT_FOUND` | Entity doesn't exist |
| `RATE_LIMIT_EXCEEDED` | Throttled |
| `CONFLICT_DUPLICATE` | Uniqueness violation |
| `INTERNAL_ERROR` | Unexpected server error (hide details) |

---

## Decision Guide

```
Error occurred
  |
  +--> Can the program continue safely?
  |      |
  |      +--> YES (operational error)
  |      |      |
  |      |      +--> Is it the client's fault? --> 4xx
  |      |      +--> Is it our fault?          --> 5xx
  |      |      +--> Is it a dependency?       --> 502/503
  |      |
  |      +--> NO (programmer error)
  |             |
  |             +--> Log full stack trace
  |             +--> Return generic 500 to client
  |             +--> Alert on-call
  |             +--> Fix the code
  |
  +--> Should the client see details?
         |
         +--> 4xx: Yes, help them fix their request
         +--> 5xx: No, generic message + request_id for support
```

## Anti-Patterns

| Anti-Pattern | Why It's Bad | Instead |
|-------------|-------------|---------|
| Catch-all silently | Hides bugs | Catch specific errors, rethrow unknown |
| Return 200 with error body | Breaks HTTP semantics | Use proper status codes |
| Expose stack traces in prod | Security risk | Log internally, return request_id |
| String error matching | Fragile, breaks on message change | Use error codes/classes |
| Catch and log only | Request hangs or returns wrong data | Handle or propagate |
