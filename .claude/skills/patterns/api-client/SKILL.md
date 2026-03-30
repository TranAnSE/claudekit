---
name: api-client
description: >
  HTTP client patterns for consuming REST APIs in Python and TypeScript. Use this skill when setting up axios, fetch, or httpx clients, implementing request interceptors, adding retry logic, handling authentication tokens, or generating type-safe API clients from OpenAPI specs. Trigger whenever code makes HTTP requests, integrates with external APIs, or needs robust error handling for network calls.
---

# API Client Patterns

## When to Use

- Setting up HTTP clients (axios, fetch, httpx) for consuming external REST APIs
- Adding request/response interceptors for logging, auth tokens, or error transformation
- Implementing retry logic with exponential backoff for transient failures
- Generating type-safe API clients from OpenAPI or Swagger specifications
- Managing authentication tokens (Bearer injection, auto-refresh on 401)

## When NOT to Use

- Internal function calls or in-process service communication that does not cross a network boundary
- Database queries -- use an ORM or database driver instead
- WebSocket or real-time streaming connections -- use dedicated WebSocket client patterns
- GraphQL clients -- use a GraphQL-specific library such as Apollo or urql

---

## Core Patterns

### 1. HTTP Client Setup

Create a single, pre-configured client instance per external service. Never scatter raw `fetch()` or `requests.get()` calls throughout the codebase.

**Python -- httpx (async)**

```python
# BAD - creating a new client on every call, no shared config
import httpx

async def get_user(user_id: int):
    response = httpx.get(f"https://api.example.com/users/{user_id}")  # no timeout, no auth
    return response.json()

# GOOD - shared async client with base URL, timeout, and headers
import httpx

class ApiClient:
    def __init__(self, base_url: str, api_key: str):
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
                "User-Agent": "myapp/1.0",
            },
            timeout=httpx.Timeout(10.0, connect=5.0),
        )

    async def get_user(self, user_id: int) -> dict:
        response = await self._client.get(f"/users/{user_id}")
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self._client.aclose()
```

**Python -- httpx (sync)**

```python
# GOOD - synchronous client for scripts, CLIs, or sync frameworks
import httpx

client = httpx.Client(
    base_url="https://api.example.com",
    headers={"Authorization": f"Bearer {api_key}"},
    timeout=httpx.Timeout(10.0, connect=5.0),
)

def get_user(user_id: int) -> dict:
    response = client.get(f"/users/{user_id}")
    response.raise_for_status()
    return response.json()
```

**TypeScript -- fetch wrapper**

```typescript
// BAD - raw fetch with no error handling or shared config
const res = await fetch("https://api.example.com/users/1");
const data = await res.json();

// GOOD - typed fetch wrapper with defaults
interface RequestConfig extends RequestInit {
  params?: Record<string, string>;
}

class ApiClient {
  constructor(
    private baseUrl: string,
    private defaultHeaders: Record<string, string> = {},
  ) {}

  private async request<T>(path: string, config: RequestConfig = {}): Promise<T> {
    const url = new URL(path, this.baseUrl);
    if (config.params) {
      Object.entries(config.params).forEach(([k, v]) => url.searchParams.set(k, v));
    }

    const response = await fetch(url.toString(), {
      ...config,
      headers: { ...this.defaultHeaders, ...config.headers },
    });

    if (!response.ok) {
      throw new ApiError(response.status, await response.text());
    }
    return response.json() as Promise<T>;
  }

  get<T>(path: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(path, { ...config, method: "GET" });
  }

  post<T>(path: string, body: unknown, config?: RequestConfig): Promise<T> {
    return this.request<T>(path, {
      ...config,
      method: "POST",
      body: JSON.stringify(body),
      headers: { "Content-Type": "application/json", ...config?.headers },
    });
  }
}

const api = new ApiClient("https://api.example.com", {
  Authorization: `Bearer ${process.env.API_KEY}`,
  Accept: "application/json",
});
```

**TypeScript -- axios instance**

```typescript
// GOOD - axios instance with shared config
import axios from "axios";

const api = axios.create({
  baseURL: "https://api.example.com",
  timeout: 10_000,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});

// All requests share the same base URL, timeout, and headers
const user = await api.get<User>("/users/1");
const created = await api.post<User>("/users", { name: "Alice" });
```

### 2. Request/Response Interceptors

Interceptors centralize cross-cutting concerns so individual API calls stay clean.

**Axios interceptors (TypeScript)**

```typescript
// GOOD - auth token injection
api.interceptors.request.use((config) => {
  const token = tokenStore.getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// GOOD - request/response logging
api.interceptors.request.use((config) => {
  console.debug(`[API] ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

api.interceptors.response.use(
  (response) => {
    console.debug(`[API] ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(`[API] Error ${error.response?.status} ${error.config?.url}`);
    return Promise.reject(error);
  },
);

// GOOD - error transformation to application-specific errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      throw new ApiError(status, data?.message ?? "Unknown API error", data?.code);
    }
    if (error.code === "ECONNABORTED") {
      throw new TimeoutError(`Request timed out: ${error.config?.url}`);
    }
    throw new NetworkError("Network connection failed");
  },
);
```

**httpx event hooks (Python)**

```python
# GOOD - logging and error hooks on httpx client
import httpx
import logging

logger = logging.getLogger("api_client")

async def log_request(request: httpx.Request):
    logger.debug(f"Request: {request.method} {request.url}")

async def log_response(response: httpx.Response):
    logger.debug(f"Response: {response.status_code} {response.url}")

async def raise_on_error(response: httpx.Response):
    if response.status_code >= 400:
        await response.aread()
        logger.error(f"API error {response.status_code}: {response.text[:200]}")

client = httpx.AsyncClient(
    base_url="https://api.example.com",
    event_hooks={
        "request": [log_request],
        "response": [log_response, raise_on_error],
    },
)
```

### 3. Retry Logic

Retry transient failures with exponential backoff. Never retry non-idempotent requests blindly.

**Python -- tenacity**

```python
# GOOD - retry with exponential backoff for specific status codes
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
import httpx

def is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (429, 500, 502, 503, 504)
    if isinstance(exc, (httpx.ConnectTimeout, httpx.ReadTimeout)):
        return True
    return False

@retry(
    retry=retry_if_exception(is_retryable),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
async def fetch_with_retry(client: httpx.AsyncClient, url: str) -> dict:
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
```

**Python -- manual retry with Retry-After**

```python
# GOOD - respects Retry-After header from rate-limited responses
import asyncio
import httpx

async def fetch_respecting_rate_limit(
    client: httpx.AsyncClient,
    url: str,
    max_retries: int = 3,
) -> httpx.Response:
    for attempt in range(max_retries):
        response = await client.get(url)
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
            await asyncio.sleep(min(retry_after, 60))
            continue
        response.raise_for_status()
        return response
    raise httpx.HTTPStatusError(
        "Max retries exceeded", request=response.request, response=response
    )
```

**TypeScript -- custom retry wrapper**

```typescript
// GOOD - generic retry wrapper with exponential backoff
interface RetryOptions {
  maxRetries: number;
  baseDelay: number;
  maxDelay: number;
  retryableStatuses: number[];
}

const DEFAULT_RETRY: RetryOptions = {
  maxRetries: 3,
  baseDelay: 1000,
  maxDelay: 10000,
  retryableStatuses: [429, 500, 502, 503, 504],
};

async function withRetry<T>(
  fn: () => Promise<T>,
  options: Partial<RetryOptions> = {},
): Promise<T> {
  const opts = { ...DEFAULT_RETRY, ...options };

  for (let attempt = 0; attempt <= opts.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      const status = error instanceof ApiError ? error.status : 0;
      const isRetryable = opts.retryableStatuses.includes(status);
      const isLastAttempt = attempt === opts.maxRetries;

      if (!isRetryable || isLastAttempt) throw error;

      const delay = Math.min(opts.baseDelay * 2 ** attempt, opts.maxDelay);
      const jitter = delay * (0.5 + Math.random() * 0.5);
      await new Promise((resolve) => setTimeout(resolve, jitter));
    }
  }
  throw new Error("Unreachable");
}

// Usage
const user = await withRetry(() => api.get<User>("/users/1"));
```

### 4. Type-Safe Clients from OpenAPI

Generate clients from OpenAPI specs to eliminate hand-written API types and reduce drift between backend and frontend.

**TypeScript -- openapi-typescript + openapi-fetch**

```bash
# Generate types from an OpenAPI spec
npx openapi-typescript https://api.example.com/openapi.json -o src/api/schema.d.ts
```

```typescript
// GOOD - fully typed client from generated schema
import createClient from "openapi-fetch";
import type { paths } from "./schema";

const api = createClient<paths>({
  baseUrl: "https://api.example.com",
  headers: { Authorization: `Bearer ${token}` },
});

// Paths, methods, params, and response types are all inferred
const { data, error } = await api.GET("/users/{id}", {
  params: { path: { id: 42 } },
});
// data is typed as the 200 response schema
// error is typed as the error response schema
```

**TypeScript -- zodios (Zod + axios)**

```typescript
// GOOD - runtime-validated API client with Zod schemas
import { makeApi, Zodios } from "@zodios/core";
import { z } from "zod";

const userSchema = z.object({
  id: z.number(),
  name: z.string(),
  email: z.string().email(),
});

const api = makeApi([
  {
    method: "get",
    path: "/users/:id",
    alias: "getUser",
    response: userSchema,
  },
  {
    method: "post",
    path: "/users",
    alias: "createUser",
    parameters: [{ name: "body", type: "Body", schema: userSchema.omit({ id: true }) }],
    response: userSchema,
  },
]);

const client = new Zodios("https://api.example.com", api);

// Fully typed and runtime validated
const user = await client.getUser({ params: { id: 42 } });
```

**Python -- datamodel-code-generator**

```bash
# Generate Pydantic models from an OpenAPI spec
pip install datamodel-code-generator
datamodel-codegen --input openapi.json --output src/api/models.py --input-file-type openapi
```

```python
# Generated models are Pydantic BaseModel classes
from api.models import User, CreateUserRequest

# Use them with httpx for typed requests
async def create_user(client: httpx.AsyncClient, payload: CreateUserRequest) -> User:
    response = await client.post("/users", json=payload.model_dump())
    response.raise_for_status()
    return User.model_validate(response.json())
```

### 5. Authentication

Centralize auth token management so every request gets the right credentials without per-call boilerplate.

**Bearer token injection (axios)**

```typescript
// GOOD - automatic token refresh on 401
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else resolve(token!);
  });
  failedQueue = [];
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then((token) => {
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return api(originalRequest);
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const { data } = await axios.post("/auth/refresh", {
        refreshToken: tokenStore.getRefreshToken(),
      });
      tokenStore.setAccessToken(data.accessToken);
      processQueue(null, data.accessToken);
      originalRequest.headers.Authorization = `Bearer ${data.accessToken}`;
      return api(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError, null);
      tokenStore.clear();
      window.location.href = "/login";
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  },
);
```

**Python -- httpx auth class**

```python
# GOOD - custom auth flow with automatic refresh
import httpx
import time

class BearerAuth(httpx.Auth):
    def __init__(self, token_url: str, client_id: str, client_secret: str):
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: str | None = None
        self._expires_at: float = 0

    def auth_flow(self, request: httpx.Request):
        if self._is_expired():
            token_response = yield self._build_token_request()
            token_response.raise_for_status()
            data = token_response.json()
            self._access_token = data["access_token"]
            self._expires_at = time.time() + data["expires_in"] - 30  # 30s buffer

        request.headers["Authorization"] = f"Bearer {self._access_token}"
        yield request

    def _is_expired(self) -> bool:
        return self._access_token is None or time.time() >= self._expires_at

    def _build_token_request(self) -> httpx.Request:
        return httpx.Request(
            "POST",
            self.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )

# Usage
auth = BearerAuth(
    token_url="https://auth.example.com/token",
    client_id=os.environ["CLIENT_ID"],
    client_secret=os.environ["CLIENT_SECRET"],
)
client = httpx.AsyncClient(base_url="https://api.example.com", auth=auth)
```

**API key via custom header**

```python
# GOOD - API key as header, loaded from environment
import os
import httpx

client = httpx.AsyncClient(
    base_url="https://api.example.com",
    headers={"X-API-Key": os.environ["EXAMPLE_API_KEY"]},
)
```

### 6. Error Handling

Distinguish between network errors, timeout errors, and API-level errors. Never swallow exceptions silently.

**TypeScript -- structured error classes**

```typescript
// GOOD - error hierarchy for API calls
class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly body: string,
    public readonly code?: string,
  ) {
    super(`API error ${status}: ${body.slice(0, 200)}`);
    this.name = "ApiError";
  }

  get isClientError(): boolean {
    return this.status >= 400 && this.status < 500;
  }

  get isServerError(): boolean {
    return this.status >= 500;
  }
}

class NetworkError extends Error {
  constructor(message: string, public readonly cause?: Error) {
    super(message);
    this.name = "NetworkError";
  }
}

class TimeoutError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "TimeoutError";
  }
}
```

**Timeout and cancellation with AbortController**

```typescript
// GOOD - cancel requests that take too long or on component unmount
async function fetchWithTimeout<T>(url: string, timeoutMs: number = 5000): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, { signal: controller.signal });
    if (!response.ok) throw new ApiError(response.status, await response.text());
    return response.json() as Promise<T>;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new TimeoutError(`Request to ${url} timed out after ${timeoutMs}ms`);
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

// React -- cancel on unmount
function useApiData(url: string) {
  const [data, setData] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    fetch(url, { signal: controller.signal })
      .then((res) => res.json())
      .then(setData)
      .catch((err) => {
        if (err.name !== "AbortError") console.error(err);
      });
    return () => controller.abort();
  }, [url]);

  return data;
}
```

**Python -- structured error handling**

```python
# GOOD - catch specific httpx exceptions
import httpx

async def safe_api_call(client: httpx.AsyncClient, path: str) -> dict | None:
    try:
        response = await client.get(path)
        response.raise_for_status()
        return response.json()
    except httpx.ConnectTimeout:
        logger.error(f"Connection timeout: {path}")
        raise
    except httpx.ReadTimeout:
        logger.error(f"Read timeout: {path}")
        raise
    except httpx.HTTPStatusError as exc:
        logger.error(f"HTTP {exc.response.status_code} from {path}: {exc.response.text[:200]}")
        if exc.response.status_code == 404:
            return None
        raise
    except httpx.ConnectError:
        logger.error(f"Connection failed: {path}")
        raise
```

### 7. Rate Limiting (Client-Side)

Respect API rate limits to avoid being throttled or banned.

**TypeScript -- request queue with concurrency control**

```typescript
// GOOD - throttle outgoing requests to stay under rate limits
class RequestQueue {
  private queue: Array<() => Promise<void>> = [];
  private running = 0;

  constructor(
    private maxConcurrent: number = 5,
    private minDelay: number = 100,
  ) {}

  async add<T>(fn: () => Promise<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      this.queue.push(async () => {
        try {
          resolve(await fn());
        } catch (error) {
          reject(error);
        }
      });
      this.process();
    });
  }

  private async process(): Promise<void> {
    if (this.running >= this.maxConcurrent || this.queue.length === 0) return;

    this.running++;
    const task = this.queue.shift()!;
    await task();
    await new Promise((resolve) => setTimeout(resolve, this.minDelay));
    this.running--;
    this.process();
  }
}

// Usage -- at most 5 concurrent requests, 100ms between each
const queue = new RequestQueue(5, 100);
const users = await Promise.all(
  userIds.map((id) => queue.add(() => api.get<User>(`/users/${id}`))),
);
```

**Python -- asyncio semaphore throttle**

```python
# GOOD - limit concurrent requests with a semaphore
import asyncio
import httpx

class ThrottledClient:
    def __init__(self, client: httpx.AsyncClient, max_concurrent: int = 5):
        self._client = client
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def get(self, url: str, **kwargs) -> httpx.Response:
        async with self._semaphore:
            response = await self._client.get(url, **kwargs)
            # Respect Retry-After if rate limited
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "5"))
                await asyncio.sleep(retry_after)
                response = await self._client.get(url, **kwargs)
            return response
```

---

## Best Practices

1. **Create one client instance per external service.** Share it across your application. Instantiating new clients on every call wastes connections and prevents connection pooling.

2. **Always set explicit timeouts.** A missing timeout means a stuck request can hang your entire application. Set both connect and read timeouts. Five to ten seconds is a sensible default for most APIs.

3. **Centralize error handling in interceptors or middleware.** Do not scatter try/catch blocks around every individual API call. Use interceptors to transform HTTP errors into typed application errors.

4. **Add jitter to retry backoff.** Pure exponential backoff causes thundering herd problems when many clients retry simultaneously. Add random jitter to spread retries across time.

5. **Never retry non-idempotent requests automatically.** POST requests that create resources can cause duplicates if retried blindly. Only retry GET, HEAD, and PUT (idempotent methods) by default.

6. **Generate types from OpenAPI specs instead of writing them by hand.** This eliminates drift between backend and frontend types and reduces maintenance effort.

7. **Log request and response metadata, not bodies.** Log method, URL, status code, and duration. Avoid logging request or response bodies by default -- they may contain sensitive data like tokens or PII.

8. **Close clients when the application shuts down.** In Python, use `async with` or call `aclose()`. In Node.js, use AbortController or connection pool shutdown. Leaked connections cause resource exhaustion.

---

## Common Pitfalls

1. **Not closing httpx clients.** Failing to call `aclose()` leaks connections and file descriptors. Use `async with httpx.AsyncClient() as client:` or register a shutdown handler.

2. **Storing API keys in source code.** Always load secrets from environment variables or a secret manager. Never commit API keys, tokens, or credentials to version control.

3. **Ignoring response status codes.** `fetch()` does not throw on 4xx/5xx -- you must check `response.ok` or call `.raise_for_status()`. This is the most common fetch mistake.

4. **Retrying 400-level errors.** Client errors (400, 401, 403, 404, 422) are not transient. Retrying them wastes time and load. Only retry on 429 (rate limit) and 5xx (server errors).

5. **Building URLs with string concatenation.** Concatenating user input into URLs creates injection risks and encoding bugs. Use `URL` constructor (JS) or `httpx.URL` (Python) for safe URL building.

6. **Not cancelling requests on component unmount.** In React, fetch requests that complete after unmount cause state-update-on-unmounted-component warnings and potential memory leaks. Always use AbortController with a cleanup function.

---

## Related Skills

- `api/openapi` - OpenAPI spec design and documentation
- `patterns/error-handling` - Structured error handling patterns across the stack
- `patterns/authentication` - Authentication token management and OAuth2 flows
- `patterns/caching` - HTTP caching, conditional requests, and cache invalidation
- `patterns/logging` - Logging HTTP requests and responses
