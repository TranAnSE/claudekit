# Logging — TypeScript Patterns (pino)

Reference examples for the [logging skill](./SKILL.md). All patterns use [pino](https://github.com/pinojs/pino).

---

## 1. Structured Logging Setup

Configure pino once and export a factory for child loggers per module.

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

---

## 2. Log Levels

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

---

## 3. Correlation IDs

Correlation IDs tie together all log entries from a single request. Uses Express middleware with `AsyncLocalStorage`.

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

### Propagating to downstream services

When calling other microservices, forward the correlation ID:

```typescript
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

---

## 4. Sensitive Data Redaction

Pino has built-in redaction support for field paths.

```typescript
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

---

## 5. Request/Response Logging

Log every HTTP request and response with method, path, status code, duration, and body size. Uses Express middleware.

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

---

## 6. Error Logging

When logging errors, include the stack trace via pino's `err` serializer and enough context to reproduce the issue.

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

---

## 7. Performance Logging

### Timing wrapper

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
