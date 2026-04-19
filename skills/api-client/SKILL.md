---
name: api-client
description: >
  Use when setting up axios, fetch, or httpx clients, implementing request interceptors, adding retry logic, handling authentication tokens, or generating type-safe API clients from OpenAPI specs. Also activate whenever code makes HTTP requests, integrates with external APIs, or needs robust error handling for network calls.
---

# API Client Patterns

## When to Use

- Setting up HTTP clients (httpx, axios, fetch) with base URLs and default headers
- Implementing request/response interceptors for auth tokens, logging, or error transformation
- Adding retry logic with exponential backoff for transient failures
- Generating type-safe API clients from OpenAPI specifications
- Handling authentication tokens (Bearer, API key) in outbound requests
- Building wrapper classes around third-party REST APIs

## When NOT to Use

- Building API servers (use `backend-frameworks`)
- Making simple one-off HTTP calls that don't need a configured client
- GraphQL clients (use Apollo or urql documentation directly)

---

## Quick Reference

| Topic | Reference | Key content |
|-------|-----------|-------------|
| All client patterns | `references/patterns.md` | httpx, axios, fetch wrappers, interceptors, retry, type-safe clients |
| HTTP client recipes | `references/http-client-patterns.md` | Advanced patterns, streaming, file uploads |

---

## Best Practices

1. **Create a single configured client instance.** Don't construct new clients per request. Configure base URL, timeouts, and default headers once.
2. **Set explicit timeouts.** Never use default (infinite) timeouts. Set connect and read timeouts separately.
3. **Use interceptors for cross-cutting concerns.** Auth token injection, request logging, and error transformation belong in interceptors, not in each call site.
4. **Implement retry with exponential backoff and jitter.** Only retry idempotent requests (GET, PUT, DELETE) and transient errors (5xx, network errors).
5. **Respect Retry-After headers.** When the server sends `Retry-After`, honor it instead of using your own backoff schedule.
6. **Generate clients from OpenAPI specs.** Use `openapi-typescript` + `openapi-fetch` (TypeScript) or `openapi-python-client` (Python) for type-safe API consumption.
7. **Handle errors at the boundary.** Transform HTTP errors into domain-specific errors at the client wrapper level.

## Common Pitfalls

1. **No timeout configured** — requests hang indefinitely on unresponsive servers.
2. **Retrying non-idempotent requests** — retrying POST can create duplicates. Use idempotency keys.
3. **Swallowing error details** — wrapping errors without preserving the original status code and message.
4. **Token refresh race conditions** — multiple concurrent requests all try to refresh the token simultaneously. Use a mutex/lock.
5. **Not closing client connections** — httpx AsyncClient and axios instances should be properly closed/disposed.

---

## Related Skills

- `error-handling` — Error transformation and retry patterns
- `authentication` — Token management for API calls
- `backend-frameworks` — Building the APIs these clients consume
