---
name: error-handling
description: >
  Comprehensive error handling patterns for Python and TypeScript applications. Use this skill whenever writing try/catch blocks, creating custom error classes, implementing retry logic, designing error boundaries in React, building API error responses, or handling failures gracefully. Trigger for any code dealing with exceptions, error propagation, graceful degradation, or fault tolerance.
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

## Core Patterns

### 1. Custom Error Classes

Define a hierarchy of domain-specific errors so callers can catch at the right granularity.

**Python**

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

**TypeScript**

```typescript
// error-codes.ts
export const ErrorCode = {
  NOT_FOUND: "NOT_FOUND",
  VALIDATION_FAILED: "VALIDATION_FAILED",
  DUPLICATE_ENTRY: "DUPLICATE_ENTRY",
  UNAUTHORIZED: "UNAUTHORIZED",
  RATE_LIMITED: "RATE_LIMITED",
  EXTERNAL_SERVICE: "EXTERNAL_SERVICE",
  INTERNAL: "INTERNAL",
} as const;

export type ErrorCode = (typeof ErrorCode)[keyof typeof ErrorCode];

// app-error.ts
export class AppError extends Error {
  public readonly code: ErrorCode;
  public readonly details: Record<string, unknown>;

  constructor(
    message: string,
    code: ErrorCode = ErrorCode.INTERNAL,
    details: Record<string, unknown> = {},
    options?: ErrorOptions
  ) {
    super(message, options);
    this.name = "AppError";
    this.code = code;
    this.details = details;
  }

  toJSON() {
    return {
      error: this.code,
      message: this.message,
      details: this.details,
    };
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} with id '${id}' not found`, ErrorCode.NOT_FOUND, {
      resource,
      id,
    });
    this.name = "NotFoundError";
  }
}

export class ValidationError extends AppError {
  constructor(field: string, reason: string) {
    super(
      `Validation failed for '${field}': ${reason}`,
      ErrorCode.VALIDATION_FAILED,
      { field, reason }
    );
    this.name = "ValidationError";
  }
}

export class ExternalServiceError extends AppError {
  constructor(service: string, cause: Error) {
    super(
      `External service '${service}' failed: ${cause.message}`,
      ErrorCode.EXTERNAL_SERVICE,
      { service },
      { cause }
    );
    this.name = "ExternalServiceError";
  }
}
```

---

### 2. Error Boundaries (React)

Isolate component failures so a single broken widget does not take down the whole page.

**Using react-error-boundary (recommended)**

```typescript
import {
  ErrorBoundary,
  type FallbackProps,
} from "react-error-boundary";

function ErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div role="alert" className="rounded border border-red-300 bg-red-50 p-4">
      <h2 className="font-semibold text-red-800">Something went wrong</h2>
      <pre className="mt-2 text-sm text-red-700">{error.message}</pre>
      <button
        onClick={resetErrorBoundary}
        className="mt-3 rounded bg-red-600 px-3 py-1 text-white"
      >
        Try again
      </button>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onError={(error, info) => {
        // Send to error tracking service
        reportError({ error, componentStack: info.componentStack });
      }}
      onReset={() => {
        // Clear any stale state before retry
        queryClient.clear();
      }}
    >
      <Dashboard />
    </ErrorBoundary>
  );
}
```

**Granular boundaries per feature**

```typescript
function DashboardPage() {
  return (
    <div className="grid grid-cols-3 gap-4">
      {/* Each widget fails independently */}
      <ErrorBoundary FallbackComponent={WidgetErrorFallback}>
        <RevenueChart />
      </ErrorBoundary>
      <ErrorBoundary FallbackComponent={WidgetErrorFallback}>
        <UserActivityFeed />
      </ErrorBoundary>
      <ErrorBoundary FallbackComponent={WidgetErrorFallback}>
        <SystemHealthPanel />
      </ErrorBoundary>
    </div>
  );
}

function WidgetErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded border border-dashed border-gray-300 p-6 text-gray-500">
      <p>This widget failed to load.</p>
      <button onClick={resetErrorBoundary} className="mt-2 underline">
        Retry
      </button>
    </div>
  );
}
```

**Class-based error boundary (when you need full control)**

```typescript
import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ManualErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("ErrorBoundary caught:", error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? <p>Something went wrong.</p>;
    }
    return this.props.children;
  }
}
```

---

### 3. Retry Patterns

Retry transient failures with exponential backoff and jitter to avoid thundering herd.

**Python - Retry decorator with exponential backoff**

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

**TypeScript - Retry wrapper**

```typescript
interface RetryOptions {
  maxAttempts?: number;
  baseDelayMs?: number;
  maxDelayMs?: number;
  isRetryable?: (error: unknown) => boolean;
}

async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const {
    maxAttempts = 3,
    baseDelayMs = 1000,
    maxDelayMs = 30_000,
    isRetryable = () => true,
  } = options;

  let lastError: unknown;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      if (attempt === maxAttempts || !isRetryable(error)) {
        throw error;
      }

      const exponential = baseDelayMs * 2 ** (attempt - 1);
      const capped = Math.min(exponential, maxDelayMs);
      const jitter = Math.random() * capped;

      console.warn(
        `Attempt ${attempt}/${maxAttempts} failed, retrying in ${jitter.toFixed(0)}ms`
      );
      await new Promise((resolve) => setTimeout(resolve, jitter));
    }
  }

  throw lastError;
}

// Usage
const data = await withRetry(
  () => fetch("/api/config").then((r) => r.json()),
  {
    maxAttempts: 3,
    baseDelayMs: 500,
    isRetryable: (err) =>
      err instanceof TypeError || (err as Response)?.status >= 500,
  }
);
```

---

### 4. Graceful Degradation

When a dependency fails, fall back to a degraded but functional state instead of crashing.

**Circuit breaker pattern (Python)**

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

**Feature-flag degraded mode (TypeScript)**

```typescript
interface FeatureFlags {
  enableRecommendations: boolean;
  enableRealTimeUpdates: boolean;
  enableAdvancedSearch: boolean;
}

const defaultFlags: FeatureFlags = {
  enableRecommendations: true,
  enableRealTimeUpdates: true,
  enableAdvancedSearch: true,
};

async function getFlags(): Promise<FeatureFlags> {
  try {
    const resp = await fetch("/api/feature-flags");
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch {
    // Fall back to safe defaults when flag service is unavailable
    console.warn("Feature flag service unavailable, using defaults");
    return defaultFlags;
  }
}

// Component that degrades gracefully
function SearchPage() {
  const flags = useFeatureFlags();

  return (
    <div>
      <BasicSearch />
      {flags.enableAdvancedSearch ? (
        <AdvancedFilters />
      ) : (
        <p className="text-sm text-gray-500">
          Advanced search is temporarily unavailable.
        </p>
      )}
    </div>
  );
}
```

---

### 5. API Error Responses

Return consistent, machine-readable error payloads following RFC 7807 Problem Details.

**Python (FastAPI)**

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

**TypeScript (Express middleware)**

```typescript
import type { Request, Response, NextFunction } from "express";

const STATUS_MAP: Record<ErrorCode, number> = {
  NOT_FOUND: 404,
  VALIDATION_FAILED: 400,
  DUPLICATE_ENTRY: 409,
  UNAUTHORIZED: 401,
  RATE_LIMITED: 429,
  EXTERNAL_SERVICE: 502,
  INTERNAL: 500,
};

function errorHandler(
  err: Error,
  _req: Request,
  res: Response,
  _next: NextFunction
) {
  if (err instanceof AppError) {
    const status = STATUS_MAP[err.code] ?? 500;
    res.status(status).json({
      type: `https://docs.example.com/errors/${err.code.toLowerCase()}`,
      title: err.code.replace(/_/g, " ").toLowerCase(),
      status,
      detail: err.message,
      ...err.details,
    });
    return;
  }

  // Unhandled errors - log full details, return generic message
  console.error("Unhandled error:", err);
  res.status(500).json({
    type: "https://docs.example.com/errors/internal",
    title: "Internal Server Error",
    status: 500,
    detail: "An unexpected error occurred.",
  });
}

// Register as the last middleware
app.use(errorHandler);
```

---

### 6. Error Logging Integration

Attach structured context to errors so they are searchable and actionable in observability tools.

**Python - Structured error logging**

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

**TypeScript - Error context enrichment**

```typescript
interface ErrorContext {
  requestId?: string;
  userId?: string;
  operation?: string;
  [key: string]: unknown;
}

function logError(
  message: string,
  error: unknown,
  context: ErrorContext = {}
): void {
  const payload: Record<string, unknown> = {
    message,
    timestamp: new Date().toISOString(),
    ...context,
  };

  if (error instanceof AppError) {
    payload.errorCode = error.code;
    payload.errorMessage = error.message;
    payload.errorDetails = error.details;
  } else if (error instanceof Error) {
    payload.errorType = error.name;
    payload.errorMessage = error.message;
    payload.stack = error.stack;
  } else {
    payload.errorRaw = String(error);
  }

  // Structured JSON log for ingestion by Datadog, CloudWatch, etc.
  console.error(JSON.stringify(payload));
}

// Usage
try {
  await processOrder(orderId);
} catch (error) {
  logError("Order processing failed", error, {
    requestId: req.headers["x-request-id"],
    operation: "processOrder",
    orderId,
  });
  throw error;
}
```

---

### 7. Result Pattern

Use a Result type for operations where failure is an expected outcome. Avoids exception overhead and makes the failure path explicit in the type signature.

**Python - Using the `result` library**

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

**TypeScript - Discriminated union Result**

```typescript
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

function ok<T>(value: T): Result<T, never> {
  return { ok: true, value };
}

function err<E>(error: E): Result<never, E> {
  return { ok: false, error };
}

// Usage
function parseAge(input: string): Result<number, string> {
  const age = Number(input);
  if (Number.isNaN(age)) return err(`'${input}' is not a number`);
  if (age < 0 || age > 150) return err(`Age ${age} out of range (0-150)`);
  return ok(age);
}

function validateRegistration(
  data: Record<string, string>
): Result<{ name: string; age: number }, string[]> {
  const errors: string[] = [];

  const ageResult = parseAge(data.age ?? "");
  if (!ageResult.ok) errors.push(ageResult.error);

  const name = data.name?.trim() ?? "";
  if (!name) errors.push("Name is required");
  if (name.length > 100) errors.push("Name must be 100 characters or fewer");

  if (errors.length > 0) return err(errors);
  return ok({ name, age: (ageResult as { ok: true; value: number }).value });
}

// Caller
const result = validateRegistration(formData);
if (!result.ok) {
  return res.status(400).json({ errors: result.error });
}
const user = await createUser(result.value);
```

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

- `patterns/logging` - Structured logging setup and conventions
- `patterns/api-client` - HTTP client wrappers with built-in error handling
- `security/owasp` - Preventing information leakage through error messages
- `languages/python` - Python exception syntax and idioms
- `languages/typescript` - TypeScript error types and narrowing
