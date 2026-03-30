---
name: logging
description: >
  Structured logging patterns for Python and Node.js applications. Use this skill when setting up loggers, choosing log levels, implementing correlation IDs for request tracing, redacting sensitive data from logs, or configuring log aggregation. Trigger whenever code uses console.log, print(), logging module, winston, pino, structlog, or any logging library. Also applies when building observability, debugging production issues, or adding telemetry.
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

## Core Patterns

### 1. Structured Logging Setup

Structured logging outputs machine-parseable JSON instead of free-form strings. This enables searching, filtering, and alerting in log aggregation systems.

#### Python with structlog

```python
# logging_config.py
import logging
import structlog

def configure_logging(log_level: str = "INFO", json_output: bool = True) -> None:
    """Configure structured logging for the application.

    Call this once at application startup, before any loggers are created.
    """
    # Set the stdlib logging level as the baseline filter
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
    )

    # Choose renderers based on environment
    if json_output:
        renderer = structlog.processors.JSONRenderer()
    else:
        # Human-readable output for local development
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            renderer,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
```

```python
# Usage anywhere in the application
import structlog

logger = structlog.get_logger(__name__)

async def create_user(email: str) -> User:
    logger.info("creating_user", email=email)
    user = await user_repo.create(email=email)
    logger.info("user_created", user_id=user.id, email=email)
    return user
```

**Output (JSON mode):**
```json
{"event": "user_created", "user_id": 42, "email": "alice@example.com", "logger": "app.services.user", "level": "info", "timestamp": "2025-06-15T10:30:00.123Z"}
```

#### Node.js with pino

```typescript
// logger.ts
import pino from "pino";

export const logger = pino({
  level: process.env.LOG_LEVEL ?? "info",
  // Use pretty printing only in development
  transport:
    process.env.NODE_ENV === "development"
      ? { target: "pino-pretty", options: { colorize: true } }
      : undefined,
  // Base fields included in every log line
  base: {
    service: process.env.SERVICE_NAME ?? "api",
    version: process.env.APP_VERSION ?? "unknown",
  },
  // Customize serialization
  serializers: {
    err: pino.stdSerializers.err,
    req: pino.stdSerializers.req,
    res: pino.stdSerializers.res,
  },
  // Redact sensitive fields (see Pattern 4)
  redact: ["req.headers.authorization", "req.headers.cookie"],
});

// Create child loggers for specific modules
export function createLogger(module: string): pino.Logger {
  return logger.child({ module });
}
```

```typescript
// Usage in a service
import { createLogger } from "./logger";

const log = createLogger("user-service");

export async function createUser(email: string): Promise<User> {
  log.info({ email }, "creating_user");
  const user = await userRepo.create({ email });
  log.info({ userId: user.id, email }, "user_created");
  return user;
}
```

**Output (JSON):**
```json
{"level":30,"time":1718444400123,"service":"api","module":"user-service","userId":42,"email":"alice@example.com","msg":"user_created"}
```

### 2. Log Levels

Use log levels consistently to control verbosity and enable filtering in production.

| Level | When to Use | Example |
|-------|-------------|---------|
| `DEBUG` | Detailed diagnostic information useful only during development or debugging | Variable values, SQL queries, cache hits/misses |
| `INFO` | Confirmation that things are working as expected | Request received, user created, job completed |
| `WARNING` | Something unexpected happened but the application can continue | Deprecated API called, retry attempt, approaching rate limit |
| `ERROR` | A specific operation failed but the application continues running | Database query failed, external API returned 500, payment declined |
| `CRITICAL` | The application cannot continue or is in an unrecoverable state | Database connection pool exhausted, out of disk space, configuration missing |

#### Python examples

```python
import structlog

logger = structlog.get_logger(__name__)

# DEBUG: Detailed internals for troubleshooting
logger.debug("cache_lookup", key="user:42", hit=True, ttl_remaining=120)

# INFO: Normal business events
logger.info("order_placed", order_id="ORD-123", total=99.99, items=3)

# WARNING: Degraded but functional
logger.warning(
    "rate_limit_approaching",
    current_rate=450,
    limit=500,
    window_seconds=60,
)

# ERROR: Operation failed, needs attention
logger.error(
    "payment_failed",
    order_id="ORD-123",
    provider="stripe",
    error_code="card_declined",
    exc_info=True,  # Include stack trace
)

# CRITICAL: System-level failure
logger.critical(
    "database_pool_exhausted",
    active_connections=100,
    max_connections=100,
    waiting_requests=47,
)
```

#### TypeScript examples

```typescript
import { createLogger } from "./logger";

const log = createLogger("order-service");

// DEBUG: Internal details
log.debug({ key: "user:42", hit: true, ttlRemaining: 120 }, "cache_lookup");

// INFO: Normal events
log.info({ orderId: "ORD-123", total: 99.99, items: 3 }, "order_placed");

// WARNING: Degraded state
log.warn(
  { currentRate: 450, limit: 500, windowSeconds: 60 },
  "rate_limit_approaching"
);

// ERROR: Operation failure
log.error(
  { orderId: "ORD-123", provider: "stripe", errorCode: "card_declined" },
  "payment_failed"
);

// FATAL: Unrecoverable
log.fatal(
  { activeConnections: 100, maxConnections: 100, waitingRequests: 47 },
  "database_pool_exhausted"
);
```

**Level selection rule of thumb:** If you would page someone at 3 AM, it is ERROR or CRITICAL. If it is useful context for investigating an issue, it is INFO. If it is only useful when actively debugging a specific problem, it is DEBUG.

### 3. Correlation IDs

Correlation IDs (also called request IDs or trace IDs) tie together all log entries from a single request as it flows through your system.

#### Python — FastAPI middleware with contextvars

```python
# middleware/correlation.py
import uuid
from contextvars import ContextVar

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Context variable accessible from any async task in the same request
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")

class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Accept an incoming correlation ID or generate a new one
        correlation_id = request.headers.get("X-Correlation-ID", uuid.uuid4().hex)
        correlation_id_var.set(correlation_id)

        # Bind to structlog context so all logs in this request include it
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
```

```python
# Register the middleware
from middleware.correlation import CorrelationIDMiddleware

app.add_middleware(CorrelationIDMiddleware)
```

```python
# Any logger call in any module now includes correlation_id automatically
logger = structlog.get_logger(__name__)

async def get_user(user_id: int) -> User:
    logger.info("fetching_user", user_id=user_id)
    # Output: {"event": "fetching_user", "user_id": 42, "correlation_id": "a1b2c3d4...", ...}
    return await user_repo.get(user_id)
```

#### TypeScript — Express middleware with AsyncLocalStorage

```typescript
// middleware/correlation.ts
import { AsyncLocalStorage } from "node:async_hooks";
import { randomUUID } from "node:crypto";
import type { Request, Response, NextFunction } from "express";
import { logger } from "../logger";

interface RequestContext {
  correlationId: string;
}

export const asyncLocalStorage = new AsyncLocalStorage<RequestContext>();

export function correlationMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  const correlationId =
    (req.headers["x-correlation-id"] as string) ?? randomUUID();

  res.setHeader("X-Correlation-ID", correlationId);

  asyncLocalStorage.run({ correlationId }, () => {
    next();
  });
}
```

```typescript
// logger.ts — augment the logger to include correlation ID
import { asyncLocalStorage } from "./middleware/correlation";

export function getContextLogger(): pino.Logger {
  const store = asyncLocalStorage.getStore();
  if (store) {
    return logger.child({ correlationId: store.correlationId });
  }
  return logger;
}
```

```typescript
// Usage in any module
import { getContextLogger } from "./logger";

export async function getUser(userId: number): Promise<User> {
  const log = getContextLogger();
  log.info({ userId }, "fetching_user");
  // Output includes correlationId automatically
  return await userRepo.findById(userId);
}
```

#### Propagating to downstream services

When calling other microservices, forward the correlation ID:

```python
# Python — httpx client
import httpx
from middleware.correlation import correlation_id_var

async def call_billing_service(user_id: int) -> dict:
    correlation_id = correlation_id_var.get()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://billing-service/api/v1/invoices?user_id={user_id}",
            headers={"X-Correlation-ID": correlation_id},
        )
        return response.json()
```

```typescript
// TypeScript — fetch with correlation ID
import { asyncLocalStorage } from "./middleware/correlation";

export async function callBillingService(userId: number): Promise<Invoice[]> {
  const store = asyncLocalStorage.getStore();
  const response = await fetch(
    `http://billing-service/api/v1/invoices?user_id=${userId}`,
    {
      headers: {
        "X-Correlation-ID": store?.correlationId ?? "",
      },
    }
  );
  return response.json();
}
```

### 4. Sensitive Data Redaction

Never log passwords, API keys, tokens, credit card numbers, or personally identifiable information (PII). Build redaction into the logging pipeline so developers cannot accidentally leak secrets.

#### Python — structlog processor

```python
# processors/redact.py
import re
from typing import Any

# Patterns for sensitive field names (case-insensitive matching)
SENSITIVE_KEYS = re.compile(
    r"(password|passwd|secret|token|api_key|apikey|authorization|"
    r"credit_card|card_number|cvv|ssn|social_security)",
    re.IGNORECASE,
)

# Pattern for credit card numbers in string values
CREDIT_CARD_PATTERN = re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b")

# Pattern for bearer tokens in string values
BEARER_PATTERN = re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE)


def redact_sensitive_data(
    logger: Any, method_name: str, event_dict: dict
) -> dict:
    """Structlog processor that masks sensitive values."""
    return _redact_dict(event_dict)


def _redact_dict(data: dict) -> dict:
    result = {}
    for key, value in data.items():
        if SENSITIVE_KEYS.search(key):
            result[key] = "***REDACTED***"
        elif isinstance(value, dict):
            result[key] = _redact_dict(value)
        elif isinstance(value, str):
            result[key] = _redact_string(value)
        elif isinstance(value, list):
            result[key] = [
                _redact_dict(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value
    return result


def _redact_string(value: str) -> str:
    value = CREDIT_CARD_PATTERN.sub("****-****-****-****", value)
    value = BEARER_PATTERN.sub("Bearer ***REDACTED***", value)
    return value
```

```python
# Add the processor to structlog configuration
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        redact_sensitive_data,  # Add before the renderer
        structlog.processors.JSONRenderer(),
    ],
    # ...
)
```

#### TypeScript — pino redaction

```typescript
// pino has built-in redaction support
import pino from "pino";

export const logger = pino({
  level: "info",
  redact: {
    paths: [
      "password",
      "secret",
      "token",
      "apiKey",
      "authorization",
      "creditCard",
      "req.headers.authorization",
      "req.headers.cookie",
      "body.password",
      "body.creditCardNumber",
      "*.password",
      "*.secret",
    ],
    censor: "***REDACTED***",
  },
});
```

For more complex redaction (regex-based), use a custom serializer:

```typescript
// redact.ts
const CREDIT_CARD_RE = /\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b/g;
const BEARER_RE = /Bearer\s+[A-Za-z0-9\-._~+/]+=*/gi;

export function redactValue(value: unknown): unknown {
  if (typeof value === "string") {
    let result = value.replace(CREDIT_CARD_RE, "****-****-****-****");
    result = result.replace(BEARER_RE, "Bearer ***REDACTED***");
    return result;
  }
  if (typeof value === "object" && value !== null) {
    return redactObject(value as Record<string, unknown>);
  }
  return value;
}

const SENSITIVE_KEYS =
  /^(password|passwd|secret|token|api_?key|authorization|credit_?card|cvv|ssn)$/i;

function redactObject(obj: Record<string, unknown>): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(obj)) {
    if (SENSITIVE_KEYS.test(key)) {
      result[key] = "***REDACTED***";
    } else {
      result[key] = redactValue(value);
    }
  }
  return result;
}
```

### 5. Request/Response Logging

Log every HTTP request and response with method, path, status code, duration, and body size. This is the single most valuable log line for production debugging.

#### Python — FastAPI middleware

```python
# middleware/request_logging.py
import time
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = structlog.get_logger("http")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        # Log request
        logger.info(
            "http_request_started",
            method=request.method,
            path=request.url.path,
            query=str(request.url.query) or None,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "http_request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration_ms, 2),
                exc_info=True,
            )
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000
        content_length = response.headers.get("content-length")

        # Choose log level based on status code
        log_method = logger.info
        if response.status_code >= 500:
            log_method = logger.error
        elif response.status_code >= 400:
            log_method = logger.warning

        log_method(
            "http_request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            content_length=int(content_length) if content_length else None,
        )

        return response
```

#### TypeScript — Express middleware

```typescript
// middleware/request-logging.ts
import type { Request, Response, NextFunction } from "express";
import { getContextLogger } from "../logger";

export function requestLogging(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  const start = process.hrtime.bigint();
  const log = getContextLogger();

  log.info(
    {
      method: req.method,
      path: req.originalUrl,
      clientIp: req.ip,
      userAgent: req.get("user-agent"),
    },
    "http_request_started"
  );

  // Hook into the response finish event
  res.on("finish", () => {
    const durationMs =
      Number(process.hrtime.bigint() - start) / 1_000_000;

    const logFn =
      res.statusCode >= 500
        ? log.error.bind(log)
        : res.statusCode >= 400
          ? log.warn.bind(log)
          : log.info.bind(log);

    logFn(
      {
        method: req.method,
        path: req.originalUrl,
        statusCode: res.statusCode,
        durationMs: Math.round(durationMs * 100) / 100,
        contentLength: res.get("content-length")
          ? parseInt(res.get("content-length")!, 10)
          : undefined,
      },
      "http_request_completed"
    );
  });

  next();
}
```

```typescript
// Register middleware (order matters)
app.use(correlationMiddleware);
app.use(requestLogging);
```

### 6. Error Logging

When logging errors, always include the stack trace, relevant context, and enough information to reproduce the issue without accessing the production environment.

#### Python — exception logging with context

```python
import structlog

logger = structlog.get_logger(__name__)

async def process_order(order_id: str) -> Order:
    logger.info("processing_order", order_id=order_id)

    try:
        order = await order_repo.get(order_id)
        if not order:
            logger.error("order_not_found", order_id=order_id)
            raise OrderNotFoundError(order_id)

        payment = await payment_service.charge(
            amount=order.total,
            currency=order.currency,
            customer_id=order.customer_id,
        )
        logger.info(
            "payment_processed",
            order_id=order_id,
            payment_id=payment.id,
            amount=order.total,
        )

    except PaymentError as exc:
        # Log the error with full context for debugging
        logger.error(
            "payment_failed",
            order_id=order_id,
            customer_id=order.customer_id,
            amount=order.total,
            error_code=exc.code,
            error_message=str(exc),
            exc_info=True,  # Includes full stack trace
        )
        raise

    except Exception as exc:
        # Catch-all for unexpected errors
        logger.exception(
            "order_processing_unexpected_error",
            order_id=order_id,
            error_type=type(exc).__name__,
        )
        raise
```

#### TypeScript — error logging with breadcrumbs

```typescript
import { getContextLogger } from "./logger";

const log = getContextLogger();

export async function processOrder(orderId: string): Promise<Order> {
  log.info({ orderId }, "processing_order");

  try {
    const order = await orderRepo.findById(orderId);
    if (!order) {
      log.error({ orderId }, "order_not_found");
      throw new OrderNotFoundError(orderId);
    }

    const payment = await paymentService.charge({
      amount: order.total,
      currency: order.currency,
      customerId: order.customerId,
    });

    log.info(
      { orderId, paymentId: payment.id, amount: order.total },
      "payment_processed"
    );
    return order;
  } catch (err) {
    if (err instanceof PaymentError) {
      log.error(
        {
          orderId,
          errorCode: err.code,
          errorMessage: err.message,
          err, // pino serializes Error objects with stack traces
        },
        "payment_failed"
      );
    } else {
      log.error(
        {
          orderId,
          err,
          errorType: (err as Error).constructor.name,
        },
        "order_processing_unexpected_error"
      );
    }
    throw err;
  }
}
```

**Key principle:** Log at the point where you have the most context, not at every layer. A single error log with full context is more useful than five partial logs scattered across the call stack.

### 7. Performance Logging

Track operation durations to identify slow endpoints, queries, and external calls.

#### Python — timing decorator

```python
import functools
import time
from typing import Callable, TypeVar

import structlog

logger = structlog.get_logger("performance")

F = TypeVar("F", bound=Callable)

def log_duration(operation: str, slow_threshold_ms: float = 1000.0):
    """Decorator that logs the duration of a function call.

    Args:
        operation: A descriptive name for the operation.
        slow_threshold_ms: Threshold in milliseconds above which
            the log level escalates to WARNING.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.perf_counter() - start) * 1000
                log_fn = (
                    logger.warning
                    if duration_ms > slow_threshold_ms
                    else logger.debug
                )
                log_fn(
                    "operation_duration",
                    operation=operation,
                    duration_ms=round(duration_ms, 2),
                    slow=duration_ms > slow_threshold_ms,
                )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.perf_counter() - start) * 1000
                log_fn = (
                    logger.warning
                    if duration_ms > slow_threshold_ms
                    else logger.debug
                )
                log_fn(
                    "operation_duration",
                    operation=operation,
                    duration_ms=round(duration_ms, 2),
                    slow=duration_ms > slow_threshold_ms,
                )

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


# Usage
@log_duration("fetch_user_profile", slow_threshold_ms=200)
async def get_user_profile(user_id: int) -> UserProfile:
    return await user_repo.get_with_preferences(user_id)
```

#### Python — context manager for ad-hoc timing

```python
import time
from contextlib import contextmanager

import structlog

logger = structlog.get_logger("performance")

@contextmanager
def log_timing(operation: str, **extra_fields):
    """Context manager for timing arbitrary code blocks."""
    start = time.perf_counter()
    yield
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "operation_duration",
        operation=operation,
        duration_ms=round(duration_ms, 2),
        **extra_fields,
    )

# Usage
async def rebuild_search_index():
    with log_timing("rebuild_search_index", index="products"):
        products = await product_repo.get_all()
        await search_service.reindex(products)
```

#### TypeScript — timing wrapper

```typescript
import { createLogger } from "./logger";

const perfLog = createLogger("performance");

export async function withTiming<T>(
  operation: string,
  fn: () => Promise<T>,
  slowThresholdMs = 1000
): Promise<T> {
  const start = performance.now();
  try {
    const result = await fn();
    return result;
  } finally {
    const durationMs = performance.now() - start;
    const logFn = durationMs > slowThresholdMs ? perfLog.warn : perfLog.debug;
    logFn(
      {
        operation,
        durationMs: Math.round(durationMs * 100) / 100,
        slow: durationMs > slowThresholdMs,
      },
      "operation_duration"
    );
  }
}

// Usage
const profile = await withTiming("fetch_user_profile", () =>
  userRepo.getWithPreferences(userId)
);
```

#### Slow query logging

```python
# Python — SQLAlchemy event listener for slow queries
from sqlalchemy import event
from sqlalchemy.engine import Engine

import structlog

logger = structlog.get_logger("database")

SLOW_QUERY_THRESHOLD_MS = 500

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault("query_start_time", []).append(time.perf_counter())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total_ms = (time.perf_counter() - conn.info["query_start_time"].pop()) * 1000
    if total_ms > SLOW_QUERY_THRESHOLD_MS:
        logger.warning(
            "slow_query",
            duration_ms=round(total_ms, 2),
            statement=statement[:500],  # Truncate long queries
            parameters=str(parameters)[:200],
        )
```

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

- `patterns/error-handling` — Exception handling patterns that complement error logging
- `patterns/api-client` — HTTP client patterns including logging outbound requests
- `frameworks/fastapi` — FastAPI middleware setup for request logging and correlation IDs
- `devops/docker` — Container logging drivers and log aggregation in Docker environments
- `databases/postgresql` — Logging database queries and slow query detection
- `databases/mongodb` — Logging database operations and aggregation pipelines
