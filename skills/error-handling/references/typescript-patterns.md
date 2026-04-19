# Error Handling — TypeScript Patterns

## 1. Custom Error Classes

Define a hierarchy of domain-specific errors so callers can catch at the right granularity.

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

## 2. Error Boundaries (React)

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

## 3. Retry Pattern

Retry transient failures with exponential backoff and jitter to avoid thundering herd.

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

## 4. Graceful Degradation — Feature-Flag Degraded Mode

When a dependency fails, fall back to a degraded but functional state instead of crashing.

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

## 5. API Error Responses (Express)

Return consistent, machine-readable error payloads following RFC 7807 Problem Details.

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

## 6. Error Logging Integration

Attach structured context to errors so they are searchable and actionable in observability tools.

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

## 7. Result Pattern

Use a Result type for operations where failure is an expected outcome. Avoids exception overhead and makes the failure path explicit in the type signature.

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
