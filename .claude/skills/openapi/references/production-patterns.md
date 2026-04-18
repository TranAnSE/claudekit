# Production-Grade API Patterns

Four patterns that separate hobby APIs from APIs developers actually trust in production: **idempotency keys**, **rate limiting**, **optimistic concurrency (ETag)**, and **webhook signing**. Plus the **async/202** pattern for long-running work.

Each section has: what it is, why it matters, the HTTP contract, and server-side pseudocode.

---

## 1. Idempotency Keys

**Problem.** A client calls `POST /payments` to charge $50. The request succeeds on the server but the response is lost to a network blip. The client retries. Without idempotency, the customer is charged twice.

**Solution.** The client generates a UUID per logical operation and sends it as an `Idempotency-Key` header. The server stores the full response keyed by `(idempotencyKey, userId)` for a TTL window (Stripe uses 24h). Any retry with the same key returns the stored response — no re-execution.

**Key insight — store the *response*, not the request.** Replaying the operation on retry defeats the purpose. You must serve the exact bytes the original call produced, including the status code, headers, and body. Otherwise a second worker racing the first will see inconsistent state.

### HTTP contract

```
POST /v1/payments
Idempotency-Key: 0f6f7a7d-1c6a-4a1e-9d1a-4f2a1b3c4d5e
Authorization: Bearer <token>
Content-Type: application/json

{ "amount": 5000, "currency": "usd", "customerId": "cus_abc" }
```

Server responses:
- **First call:** process normally, store `(key, response)`, return `201 Created` + `Payment` body.
- **Retry (same key, same body):** return the stored response verbatim. Include header `Idempotent-Replayed: true` so clients can log the replay.
- **Retry (same key, different body):** return `422 Unprocessable Entity` with `type: .../problems/idempotency-conflict`. The key was reused for a different payload — that is a client bug.
- **Retry during in-flight processing:** return `409 Conflict` so the client backs off and retries later. Acquire a lock on `(key)` before starting work.

### Server-side pseudocode

```python
async def create_payment(req: Request, key: str | None, user: User):
    if key is None:
        # Idempotency optional, but log the risk.
        return await process_payment(req, user)

    record = await idempotency_store.get(key, user.id)
    if record:
        if record.request_hash != hash(req.body):
            raise ProblemDetail(422, "idempotency-conflict",
                                "Key reused with a different request body.")
        if record.status == "in_progress":
            raise ProblemDetail(409, "idempotency-in-progress",
                                "Original request still processing.")
        return replay(record.response)  # exact bytes

    # Claim the key atomically — losing this race returns 409
    claimed = await idempotency_store.claim(key, user.id, hash(req.body))
    if not claimed:
        raise ProblemDetail(409, "idempotency-in-progress",
                            "Original request still processing.")

    try:
        response = await process_payment(req, user)
        await idempotency_store.save(key, user.id, response, ttl=24h)
        return response
    except Exception as e:
        # Release the claim so the client can retry cleanly.
        await idempotency_store.release(key, user.id)
        raise
```

**Storage:** Redis with a 24h TTL is the standard choice. Use a Redis transaction (`WATCH`/`MULTI`) or `SETNX` for the claim step to avoid races.

**Scope:** key by `(idempotencyKey, apiKeyId)` so keys from one tenant never collide with another.

**Apply to:** all `POST` and `PATCH` that create or mutate resources with side effects (billing, emails, external API calls). Pure `GET`/`HEAD` is already idempotent; `PUT` and `DELETE` are idempotent by HTTP semantics but still benefit from replay protection for in-flight retries.

---

## 2. Rate Limiting

**Problem.** One misbehaving client floods your API and degrades everyone else. Without limits, a single bug can take the service down.

**Solution.** Bound requests per client per time window, return `429 Too Many Requests` when exceeded, and publish headers on every response so well-behaved clients can self-throttle before they hit the wall.

### Algorithms

| Algorithm | Burst behavior | Memory per key | When to pick |
|-----------|---------------|----------------|--------------|
| **Fixed window** | Allows 2× burst at window boundary | O(1) | Simple, cheap. Acceptable for soft limits. |
| **Sliding window log** | Smooth | O(n) per key | Expensive but precise. Use for billing-grade metering. |
| **Sliding window counter** | Near-smooth | O(1) | **Default choice.** Good accuracy, constant memory. |
| **Token bucket** | Configurable burst | O(1) | Use when you want to allow small bursts but bound sustained rate. Common for customer-facing APIs. |

Redis + sliding-window-counter is the pragmatic default.

### HTTP contract

**Every successful response:**

```
X-RateLimit-Limit:     1000          # quota for this window
X-RateLimit-Remaining: 942           # how many calls left
X-RateLimit-Reset:     1767225600    # unix seconds when the window resets
```

**429 response:**

```
HTTP/1.1 429 Too Many Requests
Content-Type:  application/problem+json
Retry-After:   60

{
  "type":   "https://api.example.com/problems/rate-limited",
  "title":  "Too many requests",
  "status": 429,
  "detail": "Rate limit of 1000/hour exceeded. Retry after 60s."
}
```

**`Retry-After` is mandatory on 429.** Clients use it to schedule the retry. Use seconds (integer) rather than HTTP-date — simpler, no clock-skew bugs.

### Server-side pseudocode (Redis sliding-window counter)

```python
# Pseudocode — use a battle-tested library (redis-rate-limit, slowapi, limits)
# rather than hand-rolling this in production.

async def enforce_rate_limit(key: str, limit: int, window_seconds: int) -> RateLimitResult:
    now = int(time.time())
    window_start = now - (now % window_seconds)
    prev_window_start = window_start - window_seconds

    # Atomic increment + get prior-window count
    with redis.pipeline(transaction=True) as p:
        p.incr(f"rl:{key}:{window_start}")
        p.expire(f"rl:{key}:{window_start}", window_seconds * 2)
        p.get(f"rl:{key}:{prev_window_start}")
        curr, _, prev = p.execute()

    # Weight the prior window by how much of the current window has elapsed
    elapsed_fraction = (now % window_seconds) / window_seconds
    weighted = int((int(prev or 0)) * (1 - elapsed_fraction)) + int(curr)

    remaining = max(0, limit - weighted)
    reset_at  = window_start + window_seconds

    if weighted > limit:
        return RateLimitResult(
            allowed=False,
            retry_after=reset_at - now,
            limit=limit, remaining=0, reset_at=reset_at,
        )
    return RateLimitResult(
        allowed=True,
        limit=limit, remaining=remaining, reset_at=reset_at,
    )
```

**Key strategy:** by authenticated principal (`userId` or `apiKeyId`), not by IP. IP-based limiting punishes users behind corporate NATs.

**Tiers:** different limits for anonymous / free / paid is common. Store the tier on the auth token and look up the limit at enforcement time — don't hard-code.

**Where to enforce:** at the edge (gateway/middleware) before hitting your application logic. An API gateway (Kong, Envoy, Cloudflare) handles this natively if you use one.

---

## 3. Optimistic Concurrency (ETag + If-Match)

**Problem.** Alice and Bob both load the same user record. Alice updates the email, Bob updates the name. If both `PATCH` without coordination, the second write silently overwrites the first ("lost update").

**Solution.** On `GET`, return an `ETag` header — an opaque version token. On `PATCH`, require the client to echo that ETag in `If-Match`. If the server's current ETag doesn't match, return `412 Precondition Failed` and the client must refetch and retry.

### ETag generation strategies

| Strategy | Pros | Cons |
|----------|------|------|
| Version counter (`v42`) | Trivial to compare | Needs a `version` column on every row |
| `updated_at` timestamp | No schema change | Millisecond precision may collide on bulk updates |
| Hash of body (`"a1b2c3"`) | Stateless | Recomputed on every GET |
| Database row version | Cheap, natural fit | ORM-dependent |

All work. Pick whatever matches your data layer.

**Weak vs strong:** `ETag: W/"..."` for weak (semantically equivalent), `ETag: "..."` for strong (byte-identical). Use strong ETags unless you need to support content negotiation.

### HTTP contract

```
GET /v1/users/usr_abc123 HTTP/1.1
Authorization: Bearer ...

HTTP/1.1 200 OK
ETag: "v42"
Content-Type: application/json

{ "id": "usr_abc123", "name": "Alice", "email": "alice@example.com", ... }
```

```
PATCH /v1/users/usr_abc123 HTTP/1.1
If-Match: "v42"
Content-Type: application/json

{ "email": "alice@new.example.com" }
```

**Success:**
```
HTTP/1.1 200 OK
ETag: "v43"

{ ... updated user ... }
```

**Conflict — Bob's write races Alice's:**
```
HTTP/1.1 412 Precondition Failed
Content-Type: application/problem+json

{
  "type":   "https://api.example.com/problems/precondition-failed",
  "title":  "Precondition failed",
  "status": 412,
  "detail": "The resource was modified since you last fetched it. Re-fetch and retry."
}
```

### Server-side pseudocode

```python
async def update_user(user_id: str, body: dict, if_match: str | None):
    current = await users.get(user_id)
    if current is None:
        raise ProblemDetail(404, "not-found", f"User '{user_id}' not found.")

    if if_match is None:
        raise ProblemDetail(428, "precondition-required",
                            "If-Match header is required for this operation.")

    current_etag = f'"v{current.version}"'
    if if_match != current_etag:
        raise ProblemDetail(412, "precondition-failed",
                            "The resource was modified since you last fetched it.")

    updated = await users.patch(user_id, body, expected_version=current.version)
    return updated, f'"v{updated.version}"'
```

**`428 Precondition Required`** is the correct response when the server *requires* `If-Match` and the client didn't send one. RFC 6585.

**Also useful for GETs:** `If-None-Match: "v42"` lets clients skip the body and get `304 Not Modified` if nothing changed — cheap cache revalidation.

---

## 4. Webhook Signing (HMAC)

**Problem.** You deliver an event to a consumer URL. Without a signature, anyone who guesses the URL can forge events. Without a timestamp, an attacker who captures one valid payload can replay it forever.

**Solution.** Sign every webhook with HMAC-SHA256 over `timestamp + "." + body`, send both in a header, and require consumers to reject signatures older than 5 minutes.

### HTTP contract

```
POST https://consumer.example.com/webhooks/acme HTTP/1.1
Content-Type: application/json
Acme-Signature: t=1767225600,v1=5257a869e7...7f4b
Acme-Webhook-Id: evt_01HTZ4K5M8N9P0Q1R2S3T4V5W6

{
  "id":        "evt_01HTZ4K5M8N9P0Q1R2S3T4V5W6",
  "type":      "order.completed",
  "createdAt": "2026-04-15T10:30:00Z",
  "data":      { "orderId": "ord_xyz", "total": 4999, "currency": "usd" }
}
```

**`t=` is the unix timestamp when the signature was generated.**
**`v1=` is the hex-encoded HMAC-SHA256 of `t + "." + rawBody` using the consumer's signing secret.**

The version prefix (`v1=`) lets you rotate signing schemes in the future without breaking existing consumers.

### Server-side signing

```python
import hmac, hashlib, time, json

def sign_webhook(raw_body: bytes, secret: str) -> str:
    t = int(time.time())
    payload = f"{t}.".encode() + raw_body
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return f"t={t},v1={sig}"

async def deliver(endpoint: Endpoint, event: dict):
    raw = json.dumps(event, separators=(",", ":")).encode()
    signature = sign_webhook(raw, endpoint.signing_secret)
    await http.post(
        endpoint.url,
        content=raw,
        headers={
            "Content-Type":    "application/json",
            "Acme-Signature":  signature,
            "Acme-Webhook-Id": event["id"],
        },
    )
```

### Consumer-side verification (for your docs)

```python
import hmac, hashlib, time

MAX_AGE_SECONDS = 300  # 5 minutes

def verify_webhook(raw_body: bytes, header: str, secret: str) -> dict:
    parts = dict(p.split("=", 1) for p in header.split(","))
    t   = int(parts["t"])
    sig = parts["v1"]

    # Replay protection — reject anything older than MAX_AGE
    if abs(time.time() - t) > MAX_AGE_SECONDS:
        raise SignatureError("Timestamp outside tolerance window.")

    expected = hmac.new(
        secret.encode(),
        f"{t}.".encode() + raw_body,
        hashlib.sha256,
    ).hexdigest()

    # Constant-time compare — prevents timing attacks
    if not hmac.compare_digest(expected, sig):
        raise SignatureError("Signature mismatch.")

    return json.loads(raw_body)
```

**Three non-negotiables:**

1. **Sign `timestamp + body`, not just body.** Without the timestamp, replay protection is impossible.
2. **Use constant-time comparison (`hmac.compare_digest`).** Never `==`. Side-channel leaks.
3. **Verify against the raw body bytes**, not a parsed-and-reserialized version. JSON serializers don't roundtrip byte-for-byte.

### Retry and dedup

- Retry on any non-2xx response with exponential backoff: 1m, 5m, 15m, 1h, 6h, 24h (cap at ~24h total).
- Include a unique event `id` in every payload; consumers must dedupe on it (retries will re-send the same `id`).
- Consumer must respond within ~5s with any 2xx. Do the actual work in a background job.

---

## 5. Async Long-Running Operations (202 Accepted)

**Problem.** Generating a report takes 30 seconds. You can't hold an HTTP connection that long — load balancers kill it, clients time out.

**Solution.** Return `202 Accepted` immediately with a `Location` header pointing to a status resource. The client polls (or subscribes to a webhook) until the job completes.

### HTTP contract

```
POST /v1/reports HTTP/1.1
Content-Type: application/json

{ "type": "sales", "startDate": "2026-01-01", "endDate": "2026-03-31" }
```

```
HTTP/1.1 202 Accepted
Location:    /v1/jobs/job_01HTZ9K5M8N9P0Q1R2S3T4V5W6
Retry-After: 5

{
  "id":        "job_01HTZ9K5M8N9P0Q1R2S3T4V5W6",
  "status":    "queued",
  "createdAt": "2026-04-15T10:30:00Z"
}
```

```
GET /v1/jobs/job_01HTZ9K5M8N9P0Q1R2S3T4V5W6 HTTP/1.1

HTTP/1.1 200 OK
{
  "id":         "job_01HTZ9K5M8N9P0Q1R2S3T4V5W6",
  "status":     "completed",
  "createdAt":  "2026-04-15T10:30:00Z",
  "completedAt":"2026-04-15T10:30:32Z",
  "result":     { "reportUrl": "https://cdn.example.com/reports/xyz.csv" }
}
```

**Job states:** `queued` → `running` → `completed` | `failed` | `cancelled`.

On `failed`, embed a `ProblemDetails` object in the job body under `error` so the client gets structured failure info without a separate endpoint.

**Webhook option:** let the client register a callback URL on the job creation (`"callbackUrl": "https://..."`) and deliver a webhook when the job terminates, following the signing pattern above. Saves polling and is what mature APIs offer as the default.

---

## Applying this in OpenAPI

The starter template [openapi-3.1-starter.yaml](../templates/openapi-3.1-starter.yaml) already demonstrates four of these patterns on the `/users` endpoints:

| Pattern | Where in the template |
|---------|----------------------|
| Idempotency keys | `POST /users` → `IdempotencyKeyHeader` parameter |
| Rate limit headers | `GET /users` responses → `X-RateLimit-*` header refs |
| ETag + If-Match | `GET` + `PATCH /users/{userId}` → `ETag` header, `If-Match` param, `412` response |
| Problem Details errors | All `4xx`/`5xx` responses use `application/problem+json` |

Copy the relevant `parameters`, `headers`, and `responses` blocks into your own spec.

---

## Related

- [http-status-codes.md](http-status-codes.md) — 202, 409, 412, 428, 429 selection rules
- [rest-naming.md](rest-naming.md) — URL conventions
- [api-governance.md](api-governance.md) — linting, docs, client gen, contract testing
- [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457) — Problem Details for HTTP APIs
- [Stripe: Designing APIs with Idempotency](https://stripe.com/blog/idempotency) — the canonical write-up
