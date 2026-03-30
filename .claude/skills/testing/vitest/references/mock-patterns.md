# Vitest Mock Patterns

Catalog of mocking patterns for common testing scenarios.

## 1. Module Mock (Full)

Replace an entire module with mock implementations.

```typescript
import { describe, it, expect, vi } from "vitest";

// Mock the entire module BEFORE importing code that uses it.
vi.mock("@/services/payment", () => ({
  chargeCard: vi.fn().mockResolvedValue({
    transactionId: "txn-123",
    status: "succeeded",
  }),
  refundCharge: vi.fn().mockResolvedValue({
    refundId: "ref-456",
    status: "refunded",
  }),
}));

import { chargeCard } from "@/services/payment";
import { checkout } from "@/services/checkout";

describe("checkout", () => {
  it("should charge the card and return success", async () => {
    const result = await checkout({ amount: 42, cardToken: "tok_test" });

    expect(chargeCard).toHaveBeenCalledWith({
      amount: 42,
      token: "tok_test",
    });
    expect(result.status).toBe("succeeded");
  });
});
```

## 2. Partial Module Mock

Mock only specific exports; keep the rest real.

```typescript
import { describe, it, expect, vi } from "vitest";

vi.mock("@/utils/config", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/utils/config")>();
  return {
    ...actual,
    // Override only this one export
    getFeatureFlag: vi.fn().mockReturnValue(true),
  };
});

import { getFeatureFlag, parseConfig } from "@/utils/config";

describe("with feature flag enabled", () => {
  it("should use the new algorithm", () => {
    // getFeatureFlag is mocked, parseConfig is real
    expect(getFeatureFlag("new-algo")).toBe(true);
  });
});
```

## 3. Manual Mock Reset / Per-Test Overrides

```typescript
import { describe, it, expect, vi, beforeEach } from "vitest";
import { fetchUser } from "@/api/users";

vi.mock("@/api/users");

// Type the mock for autocomplete
const mockFetchUser = vi.mocked(fetchUser);

beforeEach(() => {
  vi.resetAllMocks(); // Clear call history AND implementations
});

describe("user profile", () => {
  it("shows user data on success", async () => {
    mockFetchUser.mockResolvedValueOnce({ id: "1", name: "Alice" });
    // ...test
  });

  it("shows error on failure", async () => {
    mockFetchUser.mockRejectedValueOnce(new Error("Network error"));
    // ...test
  });
});
```

## 4. API Mock with MSW (Mock Service Worker)

Best for integration tests that should exercise real fetch/axios code.

```typescript
// test/mocks/handlers.ts
import { http, HttpResponse } from "msw";

export const handlers = [
  http.get("/api/users/:id", ({ params }) => {
    return HttpResponse.json({ id: params.id, name: "Alice", email: "alice@example.com" });
  }),
  http.post("/api/users", async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: "new-1", ...body }, { status: 201 });
  }),
];
```

```typescript
// test/mocks/server.ts
import { setupServer } from "msw/node";
import { handlers } from "./handlers";

export const server = setupServer(...handlers);
```

```typescript
// test/setup.ts (referenced in vitest.config.ts setupFiles)
import { afterAll, afterEach, beforeAll } from "vitest";
import { server } from "./mocks/server";

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

```typescript
// Usage in tests -- override handlers per test
import { http, HttpResponse } from "msw";
import { server } from "../mocks/server";

it("handles server error", async () => {
  server.use(
    http.get("/api/users/:id", () => {
      return HttpResponse.json({ error: "Not found" }, { status: 404 });
    }),
  );
  // ...test error handling
});
```

## 5. Timer Mocks

Control `setTimeout`, `setInterval`, `Date.now`.

```typescript
beforeEach(() => vi.useFakeTimers());
afterEach(() => vi.useRealTimers());

it("should call the function after the delay", () => {
  const fn = vi.fn();
  const debounced = debounce(fn, 300);

  debounced();
  expect(fn).not.toHaveBeenCalled();

  vi.advanceTimersByTime(300);
  expect(fn).toHaveBeenCalledOnce();
});

// Fake date: vi.setSystemTime(new Date("2025-01-15T12:00:00Z"))
```

## 6. Spy Patterns

Observe calls without replacing implementation.

```typescript
import { describe, it, expect, vi } from "vitest";

describe("logging", () => {
  it("should log errors to console", () => {
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    logError("something went wrong");

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining("something went wrong"),
    );
    consoleSpy.mockRestore();
  });
});

// Spy on object method without changing behavior
it("should call save", () => {
  const repo = new UserRepository();
  const saveSpy = vi.spyOn(repo, "save");

  repo.createUser({ name: "Alice" });

  expect(saveSpy).toHaveBeenCalledOnce();
  expect(saveSpy).toHaveBeenCalledWith(expect.objectContaining({ name: "Alice" }));
});
```

## 7. Global / Window Mocks

```typescript
// Mock window.location
vi.spyOn(window, "location", "get").mockReturnValue({ ...window.location, pathname: "/dashboard" });

// Mock localStorage
const storage: Record<string, string> = {};
vi.spyOn(Storage.prototype, "getItem").mockImplementation((key) => storage[key] ?? null);
vi.spyOn(Storage.prototype, "setItem").mockImplementation((key, val) => { storage[key] = val; });

// Mock fetch (when not using MSW)
global.fetch = vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve({ data: "test" }) });
```

## 8. Class Mock

```typescript
vi.mock("@/services/analytics", () => ({
  AnalyticsClient: vi.fn().mockImplementation(() => ({
    track: vi.fn(),
    identify: vi.fn(),
    flush: vi.fn().mockResolvedValue(undefined),
  })),
}));
```

## Quick Reference: Mock Functions

| Method | Purpose |
|--------|---------|
| `vi.fn()` | Create a standalone mock function |
| `vi.fn().mockReturnValue(x)` | Always return `x` |
| `vi.fn().mockReturnValueOnce(x)` | Return `x` once, then default |
| `vi.fn().mockResolvedValue(x)` | Return `Promise.resolve(x)` |
| `vi.fn().mockRejectedValue(e)` | Return `Promise.reject(e)` |
| `vi.fn().mockImplementation(fn)` | Use custom implementation |
| `vi.spyOn(obj, "method")` | Spy on existing method |
| `vi.mocked(fn)` | Type helper for mocked function |
| `vi.mock("module")` | Auto-mock all exports |
| `vi.resetAllMocks()` | Reset history and implementations |
| `vi.restoreAllMocks()` | Restore original implementations |
| `vi.clearAllMocks()` | Clear call history only |
