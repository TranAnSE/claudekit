# Caching Decision Tree

## Primary Decision Tree

```
What are you caching?
│
├─ PURE FUNCTION RESULT (same input = same output)
│  │
│  ├─ In React component?
│  │  └─ useMemo(() => compute(data), [data])
│  │
│  ├─ Expensive computation called repeatedly?
│  │  └─ Memoize the function
│  │     Python: @functools.lru_cache or @functools.cache
│  │     JS: hand-rolled Map cache or lodash.memoize
│  │
│  └─ Shared across requests/processes?
│     └─ Use external cache (Redis) -- see below
│
├─ HTTP RESPONSE (browser or CDN caching)
│  │
│  ├─ Is it public (same for all users)?
│  │  │
│  │  ├─ Static asset (JS, CSS, images)?
│  │  │  └─ Cache-Control: public, max-age=31536000, immutable
│  │  │     (Use content hash in filename for busting)
│  │  │
│  │  ├─ API response that changes occasionally?
│  │  │  └─ Cache-Control: public, max-age=60, stale-while-revalidate=300
│  │  │     + ETag or Last-Modified for conditional requests
│  │  │
│  │  └─ HTML page?
│  │     └─ Cache-Control: public, max-age=0, must-revalidate
│  │        + ETag (let CDN/browser validate freshness)
│  │
│  └─ Is it private (user-specific)?
│     └─ Cache-Control: private, max-age=60
│        (Never cache auth tokens or sensitive data at CDN)
│
├─ DATABASE QUERY RESULT (shared across requests)
│  │
│  ├─ Read-heavy, rarely changes?
│  │  └─ Redis/Memcached with TTL
│  │     Pattern: Cache-aside (read-through)
│  │
│  ├─ Must always be fresh?
│  │  └─ Don't cache. Optimize the query instead.
│  │     (Add indexes, denormalize, materialized view)
│  │
│  └─ Needs real-time invalidation?
│     └─ Write-through cache or event-driven invalidation
│        (Update cache when DB changes)
│
├─ EXTERNAL API RESPONSE
│  │
│  ├─ API has rate limits?
│  │  └─ Cache aggressively. Respect Cache-Control from API.
│  │     Fallback: cache with reasonable TTL (5-60 min)
│  │
│  ├─ API is slow (>500ms)?
│  │  └─ Cache + stale-while-revalidate pattern
│  │     Serve stale, refresh in background
│  │
│  └─ API data is critical and must be fresh?
│     └─ Short TTL (10-30s) + circuit breaker on failure
│
└─ EDGE/CDN CACHING
   │
   ├─ Global audience, same content?
   │  └─ CDN with long TTL + purge on deploy
   │     (Cloudflare, CloudFront, Vercel Edge)
   │
   ├─ Personalized at edge?
   │  └─ Edge compute (Cloudflare Workers, Vercel Edge Functions)
   │     Cache shared parts, inject personalization
   │
   └─ A/B testing at edge?
      └─ Vary by cookie or header
         Vary: Cookie (careful: reduces cache hit rate)
```

---

## Cache-Aside Pattern (Most Common)

```
Read:
  1. Check cache for key
  2. HIT  --> return cached value
  3. MISS --> query DB, store in cache with TTL, return value

Write:
  1. Update DB
  2. Delete cache key (don't update -- avoids race conditions)
  3. Next read will repopulate cache
```

```python
# Python + Redis
import redis, json

r = redis.Redis()
TTL = 300  # 5 minutes

def get_user(user_id: str) -> dict:
    key = f"user:{user_id}"
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    user = db.query("SELECT * FROM users WHERE id = %s", user_id)
    r.setex(key, TTL, json.dumps(user))
    return user

def update_user(user_id: str, data: dict):
    db.execute("UPDATE users SET ... WHERE id = %s", user_id)
    r.delete(f"user:{user_id}")  # Invalidate, don't update
```

---

## TTL Strategy Guide

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| User session | 15-60 min | Balance security and UX |
| User profile | 5-15 min | Changes infrequently |
| Product catalog | 1-5 min | Needs reasonable freshness |
| Search results | 30s-2 min | Changes frequently |
| Static config | 1-24 hours | Rarely changes |
| Feature flags | 30s-1 min | Needs fast propagation |
| API rate limit counters | Match the rate limit window | Exact timing matters |
| Dashboard aggregations | 1-5 min | Expensive to compute |

### TTL Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| No TTL (cache forever) | Stale data, memory leak | Always set a TTL |
| TTL too short (<1s) | Cache provides no benefit | Remove cache or increase TTL |
| Same TTL for everything | Over/under-caching | Tune per data type |
| Stampede on expiry | All caches expire at once, DB overload | Jitter: TTL + random(0, 60s) |

---

## Cache Invalidation Strategies

| Strategy | How | Best For |
|----------|-----|----------|
| TTL expiry | Automatic, time-based | Most cases |
| Explicit delete | Delete key on write | Strong consistency needs |
| Write-through | Update cache on every write | Read-heavy, write-infrequent |
| Event-driven | Invalidate on DB change event | Microservices |
| Version key | Append version to cache key | Bulk invalidation |
| Tag-based | Group keys by tag, purge by tag | CDN, grouped content |

---

## Cache Headers Quick Reference

| Header | Example | Purpose |
|--------|---------|---------|
| `Cache-Control` | `max-age=3600` | Primary caching directive |
| `ETag` | `"abc123"` | Content fingerprint for conditional requests |
| `Last-Modified` | `Wed, 29 Jan 2025 12:00:00 GMT` | Timestamp for conditional requests |
| `Vary` | `Accept-Encoding, Authorization` | Cache varies by these headers |
| `CDN-Cache-Control` | `max-age=86400` | CDN-specific (Cloudflare, etc.) |

### Common Cache-Control Patterns

```
# Immutable static asset (hashed filename)
Cache-Control: public, max-age=31536000, immutable

# API data with background refresh
Cache-Control: public, max-age=60, stale-while-revalidate=300

# Private user data
Cache-Control: private, no-cache
# (no-cache = must revalidate, NOT "don't cache")

# Never cache
Cache-Control: no-store

# HTML pages (revalidate every time)
Cache-Control: public, max-age=0, must-revalidate
ETag: "content-hash-here"
```

---

## When NOT to Cache

| Scenario | Why |
|----------|-----|
| Data changes on every request | Cache hit rate ~0% |
| Data must be real-time consistent | Stale data is unacceptable |
| Write-heavy workload | Constant invalidation negates benefit |
| Data is cheap to compute/fetch | Cache overhead exceeds savings |
| Sensitive data (PII, financial) | Risk of serving wrong user's data |
| Early in development | Premature optimization; adds complexity |
