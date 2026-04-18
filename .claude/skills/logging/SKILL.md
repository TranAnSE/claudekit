---
name: logging
description: >
  Use when setting up loggers, choosing log levels, implementing correlation IDs for request tracing, redacting sensitive data from logs, or configuring log aggregation. Also activate whenever code uses console.log, print(), logging module, winston, pino, structlog, or any logging library. Applies when building observability, debugging production issues, or adding telemetry.
---

# Logging

## When to Use

- Setting up structured logging in a new application or service
- Replacing `console.log` or `print()` with proper logging infrastructure
- Adding request tracing with correlation IDs across microservices
- Redacting sensitive data (passwords, tokens, PII) from log output
- Building observability pipelines with log aggregation (ELK, Datadog, CloudWatch)

## When NOT to Use

- Static analysis or linting tasks that do not involve runtime output
- Pure computation functions where logging would add unnecessary noise
- Test assertions — use testing frameworks' built-in assertion messages, not log output

---

## Quick Reference

| # | Pattern | Description |
|---|---------|-------------|
| 1 | Structured Logging Setup | Configure JSON-based structured logging at application startup with environment-aware renderers |
| 2 | Log Levels | Use DEBUG/INFO/WARNING/ERROR/CRITICAL consistently to control verbosity and enable filtering |
| 3 | Correlation IDs | Generate a unique request ID at the entry point and propagate it through all downstream calls |
| 4 | Sensitive Data Redaction | Build redaction into the logging pipeline so secrets and PII are never written to logs |
| 5 | Request/Response Logging | Log every HTTP request/response with method, path, status, duration, and body size |
| 6 | Error Logging | Include stack traces, relevant IDs, and enough context to reproduce without production access |
| 7 | Performance Logging | Track operation durations to identify slow endpoints, queries, and external calls |

---

## Log Levels

| Level | When to Use | Example |
|-------|-------------|---------|
| `DEBUG` | Detailed diagnostic information useful only during development or debugging | Variable values, SQL queries, cache hits/misses |
| `INFO` | Confirmation that things are working as expected | Request received, user created, job completed |
| `WARNING` | Something unexpected happened but the application can continue | Deprecated API called, retry attempt, approaching rate limit |
| `ERROR` | A specific operation failed but the application continues running | Database query failed, external API returned 500, payment declined |
| `CRITICAL` | The application cannot continue or is in an unrecoverable state | Database connection pool exhausted, out of disk space, configuration missing |

**Level selection rule of thumb:** If you would page someone at 3 AM, it is ERROR or CRITICAL. If it is useful context for investigating an issue, it is INFO. If it is only useful when actively debugging a specific problem, it is DEBUG.

---

## Language References

See `references/python-patterns.md` for Python/structlog examples.

See `references/typescript-patterns.md` for TypeScript/pino examples.

---

## Best Practices

1. **Use structured logging from day one** — start with JSON output and key-value pairs instead of formatted strings. Switching from `f"User {user_id} created"` to `logger.info("user_created", user_id=user_id)` costs nothing upfront but saves hours when debugging in production.

2. **Log events, not sentences** — use snake_case event names (`order_placed`, `payment_failed`) rather than prose messages (`"An order was placed by the user"`). Event names are searchable, filterable, and easy to aggregate.

3. **Include the right context at the right level** — every log line should include enough context to be useful in isolation: relevant IDs (user, order, request), operation name, and outcome. Avoid logging the same error at every layer of the call stack.

4. **Set log levels per environment** — use DEBUG in development, INFO in staging, and INFO or WARNING in production. Never leave DEBUG enabled in production — it generates excessive volume and may expose sensitive internals.

5. **Centralize logging configuration** — configure loggers once at application startup, not in individual modules. Every module should call `get_logger(__name__)` and inherit the shared configuration.

6. **Always redact sensitive data** — build redaction into the logging pipeline as a processor or serializer. Do not rely on developers remembering to exclude passwords or tokens from log calls.

7. **Use correlation IDs for every request** — generate a unique ID at the entry point and propagate it through all downstream calls. This is the single most important pattern for debugging distributed systems.

8. **Set up log rotation and retention policies** — configure maximum file sizes, rotation intervals, and retention periods. Production logs without rotation will fill disks. Use log aggregation services (ELK, Datadog, CloudWatch) rather than relying on local files.

---

## Common Pitfalls

1. **Logging sensitive data** — passwords, API keys, JWTs, credit card numbers, and PII end up in logs more often than expected. Once written, they persist in log storage and backups. Build redaction into the pipeline rather than relying on code review to catch every instance.

2. **Using print() or console.log in production** — `print()` in Python and `console.log` in Node.js write to stdout without timestamps, levels, or structure. They cannot be filtered, aggregated, or searched. Replace them with a proper logger before deploying.

3. **Logging too much at high levels** — setting every log call to INFO or ERROR creates alert fatigue and obscures real problems. Use DEBUG for diagnostic details and reserve ERROR for situations that require action.

4. **Missing stack traces on errors** — logging `str(exception)` loses the stack trace. In Python, use `exc_info=True` or `logger.exception()`. In pino, pass the error as `{ err }` to get the full stack serialized.

5. **Not testing log output** — logging code is code. If your redaction processor has a bug, secrets leak. Write unit tests that capture log output and assert on structure, redacted fields, and expected context.

6. **Synchronous logging in async applications** — writing to files or network sinks synchronously from an async event loop blocks request processing. Use async-compatible transports (pino's worker thread, structlog with stdlib async handlers) or write to stdout and let the infrastructure handle routing.

---

## Related Skills

- `error-handling` — Exception handling patterns that complement error logging
- `api-client` — HTTP client patterns including logging outbound requests
- `fastapi` — FastAPI middleware setup for request logging and correlation IDs
- `docker` — Container logging drivers and log aggregation in Docker environments
- `postgresql` — Logging database queries and slow query detection
- `mongodb` — Logging database operations and aggregation pipelines
