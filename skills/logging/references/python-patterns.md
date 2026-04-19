# Logging — Python Patterns (structlog)

Reference examples for the [logging skill](./SKILL.md). All patterns use [structlog](https://www.structlog.org/) with stdlib integration.

---

## 1. Structured Logging Setup

Configure structured logging once at application startup. All modules then use `structlog.get_logger(__name__)`.

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

---

## 2. Log Levels

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

---

## 3. Correlation IDs

Correlation IDs tie together all log entries from a single request. Uses FastAPI middleware with `contextvars`.

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

### Propagating to downstream services

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

---

## 4. Sensitive Data Redaction

Build redaction into the logging pipeline as a structlog processor so developers cannot accidentally leak secrets.

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

---

## 5. Request/Response Logging

Log every HTTP request and response with method, path, status code, duration, and body size. Uses FastAPI middleware.

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

---

## 6. Error Logging

When logging errors, include the stack trace, relevant context, and enough information to reproduce the issue.

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

---

## 7. Performance Logging

### Timing decorator

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

### Context manager for ad-hoc timing

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

### Slow query logging (SQLAlchemy)

```python
# SQLAlchemy event listener for slow queries
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
