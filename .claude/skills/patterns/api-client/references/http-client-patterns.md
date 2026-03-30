# HTTP Client Patterns Quick Reference

## Python HTTP Clients

| Feature | httpx | requests | aiohttp |
|---------|-------|----------|---------|
| Async support | Yes (native) | No | Yes (async-only) |
| HTTP/2 | Yes | No | No |
| Connection pooling | Yes | Yes (Session) | Yes |
| Streaming | Yes | Yes | Yes |
| Type hints | Yes | Partial | Partial |
| Timeout default | No timeout | No timeout | 5 min |
| Recommended for | Modern projects | Simple scripts | Legacy async |

### httpx Setup (Recommended)

```python
import httpx

# Sync client with defaults
client = httpx.Client(
    base_url="https://api.example.com",
    timeout=httpx.Timeout(10.0, connect=5.0),
    headers={"Authorization": f"Bearer {token}"},
)

# Async client
async_client = httpx.AsyncClient(
    base_url="https://api.example.com",
    timeout=10.0,
    http2=True,
)

# Always use as context manager (ensures cleanup)
async with httpx.AsyncClient() as client:
    response = await client.get("/users")
```

### httpx Retry Pattern

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
)
async def fetch_with_retry(client: httpx.AsyncClient, url: str) -> dict:
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
```

### httpx Interceptor Pattern (Event Hooks)

```python
def log_request(request: httpx.Request):
    print(f"--> {request.method} {request.url}")

def log_response(response: httpx.Response):
    print(f"<-- {response.status_code} {response.url} ({response.elapsed.total_seconds():.2f}s)")

def raise_on_error(response: httpx.Response):
    response.raise_for_status()

client = httpx.AsyncClient(
    event_hooks={
        "request": [log_request],
        "response": [log_response, raise_on_error],
    }
)
```

---

## JavaScript/TypeScript HTTP Clients

| Feature | fetch (native) | axios | ky |
|---------|---------------|-------|-----|
| Built-in | Yes | No (~13KB) | No (~3KB) |
| Interceptors | No (manual) | Yes | Yes (hooks) |
| Auto JSON | No (manual `.json()`) | Yes | Yes |
| Timeout | AbortSignal.timeout() | Built-in | Built-in |
| Retry | No | No (plugin) | Built-in |
| Cancel | AbortController | CancelToken (deprecated) / AbortController | AbortController |
| Streaming | Yes (ReadableStream) | Node only | Yes |
| Recommended for | Simple needs, SSR | Large existing codebases | Modern projects |

### fetch Wrapper Pattern

```typescript
class ApiClient {
  constructor(
    private baseUrl: string,
    private defaultHeaders: Record<string, string> = {}
  ) {}

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const response = await fetch(url, {
      ...init,
      headers: { "Content-Type": "application/json", ...this.defaultHeaders, ...init?.headers },
      signal: init?.signal ?? AbortSignal.timeout(10_000),
    });

    if (!response.ok) {
      const body = await response.text();
      throw new ApiError(response.status, body, url);
    }

    return response.json();
  }

  get<T>(path: string, signal?: AbortSignal) {
    return this.request<T>(path, { signal });
  }

  post<T>(path: string, data: unknown) {
    return this.request<T>(path, { method: "POST", body: JSON.stringify(data) });
  }

  put<T>(path: string, data: unknown) {
    return this.request<T>(path, { method: "PUT", body: JSON.stringify(data) });
  }

  delete<T>(path: string) {
    return this.request<T>(path, { method: "DELETE" });
  }
}
```

### ky Setup (Recommended for JS)

```typescript
import ky from "ky";

const api = ky.create({
  prefixUrl: "https://api.example.com",
  timeout: 10_000,
  retry: { limit: 3, methods: ["get"], statusCodes: [408, 429, 500, 502, 503] },
  hooks: {
    beforeRequest: [
      (request) => {
        request.headers.set("Authorization", `Bearer ${getToken()}`);
      },
    ],
    afterResponse: [
      async (_request, _options, response) => {
        if (response.status === 401) {
          await refreshToken();
          // ky will retry automatically
        }
      },
    ],
  },
});

// Usage
const users = await api.get("users").json<User[]>();
const user = await api.post("users", { json: { name: "Alice" } }).json<User>();
```

---

## Error Handling Patterns

### Typed Error Class

```typescript
class ApiError extends Error {
  constructor(
    public status: number,
    public body: string,
    public url: string,
  ) {
    super(`HTTP ${status} from ${url}`);
    this.name = "ApiError";
  }

  get isRetryable(): boolean {
    return this.status >= 500 || this.status === 429;
  }

  get isAuthError(): boolean {
    return this.status === 401;
  }
}
```

```python
class ApiError(Exception):
    def __init__(self, status: int, body: str, url: str):
        self.status = status
        self.body = body
        self.url = url
        super().__init__(f"HTTP {status} from {url}")

    @property
    def is_retryable(self) -> bool:
        return self.status >= 500 or self.status == 429
```

### Error Handling Decision

| Status | Action |
|--------|--------|
| 400 | Don't retry. Fix the request. Log validation details. |
| 401 | Refresh token and retry once. If still 401, re-authenticate. |
| 403 | Don't retry. User lacks permission. |
| 404 | Don't retry. Resource doesn't exist. |
| 408, 429 | Retry with backoff. Respect `Retry-After` header. |
| 500-503 | Retry with exponential backoff (max 3 attempts). |
| Network error | Retry with backoff. Check connectivity. |
| Timeout | Retry with longer timeout or fail fast. |

---

## Auth Token Refresh Pattern

```typescript
let refreshPromise: Promise<string> | null = null;

async function getValidToken(): Promise<string> {
  const token = getStoredToken();
  if (!isExpired(token)) return token;

  // Deduplicate concurrent refresh calls
  if (!refreshPromise) {
    refreshPromise = refreshToken().finally(() => { refreshPromise = null; });
  }
  return refreshPromise;
}
```

---

## Quick Setup Checklist

| Concern | Implementation |
|---------|---------------|
| Base URL | Configure once in client factory |
| Auth header | Interceptor / hook (not per-request) |
| Timeout | Always set (10s default, 30s for uploads) |
| Retry | 3 attempts, exponential backoff, only GET + idempotent |
| Error handling | Typed errors, status-based decisions |
| Cancellation | AbortController (pass signal to all requests) |
| Logging | Log method, URL, status, duration (not bodies in prod) |
| Content-Type | Set `application/json` as default, override for file uploads |
