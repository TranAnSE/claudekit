# Error Handling — Python Patterns

## 1. Custom Error Classes

Define a hierarchy of domain-specific errors so callers can catch at the right granularity.

```python
from enum import Enum


class ErrorCode(str, Enum):
    """Central registry of machine-readable error codes."""
    NOT_FOUND = "NOT_FOUND"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"
    UNAUTHORIZED = "UNAUTHORIZED"
    RATE_LIMITED = "RATE_LIMITED"
    EXTERNAL_SERVICE = "EXTERNAL_SERVICE"
    INTERNAL = "INTERNAL"


class AppError(Exception):
    """Base error for the entire application.

    All domain errors inherit from this so a single except clause
    can catch everything the application intentionally raises.
    """

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.INTERNAL,
        *,
        details: dict | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}
        if cause:
            self.__cause__ = cause

    def to_dict(self) -> dict:
        return {
            "error": self.code.value,
            "message": str(self),
            "details": self.details,
        }


class NotFoundError(AppError):
    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            f"{resource} with id '{identifier}' not found",
            code=ErrorCode.NOT_FOUND,
            details={"resource": resource, "id": identifier},
        )


class ValidationError(AppError):
    def __init__(self, field: str, reason: str) -> None:
        super().__init__(
            f"Validation failed for '{field}': {reason}",
            code=ErrorCode.VALIDATION_FAILED,
            details={"field": field, "reason": reason},
        )


class ExternalServiceError(AppError):
    def __init__(self, service: str, cause: Exception) -> None:
        super().__init__(
            f"External service '{service}' failed: {cause}",
            code=ErrorCode.EXTERNAL_SERVICE,
            cause=cause,
            details={"service": service},
        )
```

## 2. Retry Pattern

Retry transient failures with exponential backoff and jitter to avoid thundering herd.

```python
import asyncio
import random
import logging
from functools import wraps
from typing import TypeVar, Callable, Awaitable

logger = logging.getLogger(__name__)

T = TypeVar("T")


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    retryable: tuple[type[Exception], ...] = (Exception,),
) -> Callable:
    """Retry decorator with exponential backoff and full jitter.

    Args:
        max_attempts: Total number of attempts including the first call.
        base_delay: Initial delay in seconds before the first retry.
        max_delay: Upper bound on the computed delay.
        retryable: Exception types eligible for retry.
    """

    def decorator(fn: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(fn)
        async def wrapper(*args, **kwargs) -> T:
            last_exc: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await fn(*args, **kwargs)
                except retryable as exc:
                    last_exc = exc
                    if attempt == max_attempts:
                        break
                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    jitter = random.uniform(0, delay)
                    logger.warning(
                        "Attempt %d/%d failed (%s), retrying in %.2fs",
                        attempt,
                        max_attempts,
                        exc,
                        jitter,
                    )
                    await asyncio.sleep(jitter)
            raise last_exc  # type: ignore[misc]

        return wrapper

    return decorator


# Usage
@retry(max_attempts=3, base_delay=0.5, retryable=(ConnectionError, TimeoutError))
async def fetch_remote_config(url: str) -> dict:
    async with httpx.AsyncClient(timeout=5) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()
```

## 3. Graceful Degradation — Circuit Breaker

When a dependency fails, fall back to a degraded but functional state instead of crashing.

```python
import time
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"      # normal operation
    OPEN = "open"          # failing, reject immediately
    HALF_OPEN = "half_open"  # testing recovery


class CircuitBreaker:
    """Prevents cascading failures by short-circuiting calls to an unhealthy dependency."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0

    def _trip(self) -> None:
        self.state = CircuitState.OPEN
        self.last_failure_time = time.monotonic()

    def _reset(self) -> None:
        self.state = CircuitState.CLOSED
        self.failure_count = 0

    async def call(self, fn, *args, fallback=None, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.monotonic() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                if fallback is not None:
                    return fallback() if callable(fallback) else fallback
                raise ExternalServiceError("circuit-breaker", RuntimeError("Circuit open"))

        try:
            result = await fn(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self._reset()
            return result
        except Exception as exc:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self._trip()
            raise


# Usage
recommendations_circuit = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

async def get_recommendations(user_id: str) -> list[dict]:
    return await recommendations_circuit.call(
        recommendation_service.fetch,
        user_id,
        fallback=lambda: [],  # empty list when service is down
    )
```

## 4. API Error Responses (FastAPI)

Return consistent, machine-readable error payloads following RFC 7807 Problem Details.

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

app = FastAPI()

# Map domain error codes to HTTP status codes
STATUS_MAP: dict[ErrorCode, int] = {
    ErrorCode.NOT_FOUND: HTTP_404_NOT_FOUND,
    ErrorCode.VALIDATION_FAILED: HTTP_400_BAD_REQUEST,
    ErrorCode.DUPLICATE_ENTRY: 409,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.RATE_LIMITED: HTTP_429_TOO_MANY_REQUESTS,
    ErrorCode.EXTERNAL_SERVICE: 502,
    ErrorCode.INTERNAL: HTTP_500_INTERNAL_SERVER_ERROR,
}


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    status = STATUS_MAP.get(exc.code, 500)
    return JSONResponse(
        status_code=status,
        content={
            "type": f"https://docs.example.com/errors/{exc.code.value.lower()}",
            "title": exc.code.value.replace("_", " ").title(),
            "status": status,
            "detail": str(exc),
            **exc.details,
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    # Never leak internal details to the client
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "type": "https://docs.example.com/errors/internal",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred.",
        },
    )
```

## 5. Error Logging Integration

Attach structured context to errors so they are searchable and actionable in observability tools.

```python
import logging
import traceback
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="unknown")


class StructuredErrorLogger:
    """Wraps the standard logger to attach error context automatically."""

    def __init__(self, name: str) -> None:
        self.logger = logging.getLogger(name)

    def error(
        self,
        msg: str,
        *,
        exc: Exception | None = None,
        extra: dict | None = None,
    ) -> None:
        context = {
            "request_id": request_id_var.get(),
            **(extra or {}),
        }

        if exc is not None:
            context["error_type"] = type(exc).__name__
            context["error_message"] = str(exc)
            context["stacktrace"] = traceback.format_exception(exc)

            if isinstance(exc, AppError):
                context["error_code"] = exc.code.value
                context["error_details"] = exc.details

        self.logger.error(msg, extra={"structured": context}, exc_info=exc)


# Usage in a FastAPI middleware
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

log = StructuredErrorLogger(__name__)


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        rid = request.headers.get("x-request-id", str(uuid.uuid4()))
        request_id_var.set(rid)
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            log.error(
                "Request failed",
                exc=exc,
                extra={"method": request.method, "path": request.url.path},
            )
            raise
```

## 6. Result Pattern

Use a Result type for operations where failure is an expected outcome. Avoids exception overhead and makes the failure path explicit in the type signature.

```python
# pip install result
from result import Ok, Err, Result


def parse_age(value: str) -> Result[int, str]:
    """Parse a string to a valid age. Returns Err for invalid input."""
    try:
        age = int(value)
    except ValueError:
        return Err(f"'{value}' is not a number")

    if age < 0 or age > 150:
        return Err(f"Age {age} is out of valid range (0-150)")

    return Ok(age)


def validate_registration(data: dict) -> Result[dict, list[str]]:
    """Validate all fields, collecting every error instead of failing on the first."""
    errors: list[str] = []

    match parse_age(data.get("age", "")):
        case Ok(age):
            data["age"] = age
        case Err(msg):
            errors.append(msg)

    name = data.get("name", "").strip()
    if not name:
        errors.append("Name is required")
    if len(name) > 100:
        errors.append("Name must be 100 characters or fewer")

    if errors:
        return Err(errors)
    return Ok(data)


# Caller handles both paths explicitly
match validate_registration(form_data):
    case Ok(valid):
        user = create_user(valid)
    case Err(errs):
        return {"errors": errs}, 400
```
