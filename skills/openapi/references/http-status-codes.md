# HTTP Status Codes for REST APIs

Quick reference for selecting the correct HTTP status code in REST API responses.

---

## 2xx Success

| Code | Name | When to Use |
|------|------|-------------|
| `200` | OK | General success. GET returns data, PUT/PATCH returns updated resource. |
| `201` | Created | POST successfully created a resource. Include `Location` header. |
| `202` | Accepted | Request accepted for async processing. Return a job/task ID. |
| `204` | No Content | DELETE success or PUT/PATCH with no response body needed. |

**Guidelines:**
- `200` is the default success response for GET, PUT, PATCH
- `201` must be used when a new resource is created (POST)
- `204` is preferred for DELETE (no body to return)
- `202` signals "we got it, processing later" -- return a status URL

```json
// 201 Created response
{
  "id": "usr_abc123",
  "name": "Jane Doe",
  "createdAt": "2026-01-15T10:30:00Z"
}
// Header: Location: /v1/users/usr_abc123
```

---

## 3xx Redirection

| Code | Name | When to Use |
|------|------|-------------|
| `301` | Moved Permanently | Resource URL changed permanently. Clients should update bookmarks. |
| `302` | Found | Temporary redirect. Original URL still valid. |
| `304` | Not Modified | Conditional GET -- resource unchanged since `If-None-Match`/`If-Modified-Since`. |
| `307` | Temporary Redirect | Like 302 but preserves HTTP method. Use for API redirects. |
| `308` | Permanent Redirect | Like 301 but preserves HTTP method. |

**Guidelines:**
- Prefer `307`/`308` over `302`/`301` in APIs (method preservation)
- `304` reduces bandwidth when clients cache responses
- Always include `Location` header with redirect responses

---

## 4xx Client Errors

| Code | Name | When to Use |
|------|------|-------------|
| `400` | Bad Request | Malformed syntax, invalid JSON, failed validation. |
| `401` | Unauthorized | Missing or invalid authentication credentials. |
| `403` | Forbidden | Authenticated but lacks permission for this resource. |
| `404` | Not Found | Resource does not exist at this URL. |
| `405` | Method Not Allowed | HTTP method not supported on this endpoint. |
| `409` | Conflict | Request conflicts with current state (duplicate, version mismatch). |
| `410` | Gone | Resource existed but has been permanently deleted. |
| `415` | Unsupported Media Type | Content-Type header not supported. |
| `422` | Unprocessable Entity | Valid JSON but semantically invalid (business rule violation). |
| `429` | Too Many Requests | Rate limit exceeded. Include `Retry-After` header. |

**Guidelines:**
- `400` for **structural** issues (bad JSON, missing required field, wrong type) — caught by the parser/validator.
- `422` for **semantic** failures (email already taken, invalid state transition, quota exceeded) — caught by application logic.
- `401` means "who are you?" — `403` means "I know who you are, but no".
- `409` for optimistic-locking failures and unique-constraint violations.
- `412` for `If-Match` / `If-Unmodified-Since` precondition failures (ETag concurrency).
- `429` must include `Retry-After` with seconds until retry.

**400 vs 422 decision rule:** If the request body failed to parse or a required field is missing, return `400`. If the body parsed fine and every field has the right type but the combination violates a business rule, return `422`.

All error bodies use `application/problem+json` per **RFC 9457**.

```json
// 422 Unprocessable Entity
// Content-Type: application/problem+json
{
  "type":   "https://api.example.com/problems/validation-error",
  "title":  "Validation failed",
  "status": 422,
  "detail": "Request validation failed.",
  "errors": [
    { "field": "email", "message": "Email already registered", "code": "conflict" },
    { "field": "age",   "message": "Must be 18 or older",      "code": "outOfRange" }
  ]
}
```

```json
// 429 Too Many Requests
// Headers: Retry-After: 60
// Content-Type: application/problem+json
{
  "type":   "https://api.example.com/problems/rate-limited",
  "title":  "Too many requests",
  "status": 429,
  "detail": "Rate limit exceeded. Retry after 60s."
}
```

---

## 5xx Server Errors

| Code | Name | When to Use |
|------|------|-------------|
| `500` | Internal Server Error | Unhandled exception. Generic server failure. |
| `501` | Not Implemented | Endpoint exists but functionality not built yet. |
| `502` | Bad Gateway | Upstream service returned invalid response. |
| `503` | Service Unavailable | Server overloaded or in maintenance. Include `Retry-After`. |
| `504` | Gateway Timeout | Upstream service did not respond in time. |

**Guidelines:**
- `500` should never expose stack traces in production
- `503` should include `Retry-After` header and a maintenance message
- Log all 5xx errors with request context for debugging
- Return a consistent error body format for all 5xx responses

```json
// 500 Internal Server Error (production)
// Content-Type: application/problem+json
{
  "type":     "https://api.example.com/problems/internal-error",
  "title":    "Internal server error",
  "status":   500,
  "detail":   "An unexpected error occurred. Please try again.",
  "instance": "/v1/users/usr_abc123",
  "requestId": "req_7f3a9b2c"
}
```

Extension members (`requestId`, `traceId`, etc.) are encouraged by RFC 9457 — include anything that helps the caller report the bug.

---

## Decision Flowchart

```
Request received
  |
  +-- Is it valid syntax? -- NO --> 400 Bad Request
  |
  +-- Is caller authenticated? -- NO --> 401 Unauthorized
  |
  +-- Is caller authorized? -- NO --> 403 Forbidden
  |
  +-- Does resource exist? -- NO --> 404 Not Found
  |
  +-- Is it rate-limited? -- YES --> 429 Too Many Requests
  |
  +-- If-Match / If-Unmodified-Since fails? -- YES --> 412 Precondition Failed
  |
  +-- Does it pass business rules? -- NO --> 422 Unprocessable Entity
  |
  +-- Any conflicts? -- YES --> 409 Conflict
  |
  +-- Server error? -- YES --> 500 Internal Server Error
  |
  +-- Success!
       GET    --> 200 OK
       POST   --> 201 Created
       PUT    --> 200 OK
       PATCH  --> 200 OK
       DELETE --> 204 No Content
```

---

## Standard Error Response Format — RFC 9457 Problem Details

Every error response uses the `application/problem+json` media type with this shape:

```json
{
  "type":     "https://api.example.com/problems/<problem-slug>",
  "title":    "Short human-readable summary",
  "status":   422,
  "detail":   "Human-readable explanation for this occurrence.",
  "instance": "/v1/users/usr_abc123",
  "errors":    [ /* optional: field-level validation breakdown */ ],
  "requestId": "req_..."
}
```

Required fields: `type`, `title`, `status`. Everything else is optional but strongly recommended. The `type` URI should resolve to a real documentation page — that is the core benefit of RFC 9457 over ad-hoc envelopes.

*Reference: [RFC 9110 — HTTP Semantics](https://httpwg.org/specs/rfc9110.html), [RFC 9457 — Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457)*
