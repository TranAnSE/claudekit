---
name: caching
description: >
  Use when implementing memoization, HTTP cache headers, Redis caching, CDN configuration, or in-memory caches. Also activate whenever code deals with Cache-Control headers, ETags, functools.lru_cache, React useMemo, TanStack Query cache, or any caching strategy. Applies to cache invalidation, TTL policies, and cache-aside patterns.
---

# Caching

## When to Use

- Memoizing expensive function calls (lru_cache, useMemo, node-cache)
- Setting HTTP cache headers (Cache-Control, ETag, Last-Modified)
- Implementing Redis cache-aside pattern for database query results
- Configuring CDN caching for static assets and API responses
- Building multi-layer caches (in-memory + Redis + CDN)
- Implementing cache invalidation strategies

## When NOT to Use

- Data that changes on every request (real-time prices, live feeds)
- Security-sensitive responses that must never be cached (auth tokens, personal data)
- Development environments where stale data causes confusion

---

## Quick Reference

| Topic | Reference | Key content |
|-------|-----------|-------------|
| All caching patterns | `references/patterns.md` | Memoization, HTTP headers, ETags, Redis, CDN, multi-layer, invalidation |
| Decision tree | `references/caching-decision-tree.md` | When to use which caching strategy |

---

## Best Practices

1. **Cache at the right layer.** In-memory for hot paths (<1ms), Redis for shared state (<5ms), CDN for static/semi-static content.
2. **Always set TTLs.** Every cache entry must expire. Unbounded caches grow until they crash.
3. **Use cache-aside (lazy loading) by default.** Read from cache, miss goes to DB, write result to cache. Simplest and most predictable pattern.
4. **Invalidate on write.** When data changes, delete the cache key immediately. Don't wait for TTL expiry.
5. **Use ETag-based validation** for HTTP caching. Cheaper than full responses and guarantees freshness.
6. **Prevent cache stampede.** When a popular key expires, use distributed locks or stale-while-revalidate to prevent all requests from hitting the DB simultaneously.
7. **Monitor cache hit rates.** A cache with <80% hit rate may not be worth the complexity. Measure before optimizing.

## Common Pitfalls

1. **Caching without TTL** — memory grows unboundedly until OOM.
2. **Cache invalidation bugs** — stale data served after writes. Always invalidate on mutation.
3. **Caching user-specific data with shared keys** — one user sees another's data.
4. **Over-caching in development** — confusing stale responses with bugs.
5. **Ignoring serialization costs** — caching large objects in Redis costs more in ser/deser than the DB query saved.
6. **Not handling cache failures gracefully** — if Redis is down, fall through to DB, don't crash.

---

## Related Skills

- `databases` — Redis patterns and database query optimization
- `backend-frameworks` — Framework-specific cache middleware
- `frontend` — React useMemo, TanStack Query cache
