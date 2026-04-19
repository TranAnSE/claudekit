# Caching — Patterns


# Caching

## When to Use

- Adding memoization to expensive pure functions or computations
- Setting HTTP cache headers on API responses or static assets
- Implementing a Redis or in-memory cache layer for database queries
- Configuring CDN caching rules for edge distribution
- Designing cache invalidation strategies for data that changes
- Optimizing Next.js data fetching with built-in caching primitives

## When NOT to Use

- Data that must always be real-time and consistent (financial transactions, inventory counts during checkout) — caching introduces staleness
- Write-heavy workloads where invalidation cost exceeds the read savings
- Small datasets that are fast to compute or fetch — the overhead of cache management is not worth it

---

## Core Patterns

### 1. Memoization

Memoization caches the result of a function call based on its arguments. Use it for pure functions (same input always produces same output) that are called repeatedly with the same arguments.

#### Python — functools

```python
from functools import lru_cache, cache

# lru_cache with a max size — evicts least recently used entries
@lru_cache(maxsize=256)
def compute_shipping_cost(weight_kg: float, zone: str) -> float:
    """Expensive calculation based on weight and shipping zone."""
    # Complex rate lookup, distance calculation, surcharges...
    return base_rate * weight_factor * zone_multiplier


# cache (Python 3.9+) — unbounded, equivalent to lru_cache(maxsize=None)
@cache
def parse_config(config_path: str) -> dict:
    """Parse a config file. Result never changes for the same path."""
    with open(config_path) as f:
        return yaml.safe_load(f)


# Check cache statistics
print(compute_shipping_cost.cache_info())
# CacheInfo(hits=142, misses=23, maxsize=256, currsize=23)

# Clear cache when needed
compute_shipping_cost.cache_clear()
```

**Important:** `lru_cache` requires hashable arguments. It does not work with lists, dicts, or mutable objects. For async functions, use `asyncache` or `aiocache`:

```python
# Async memoization with aiocache
from aiocache import cached, Cache

@cached(
    ttl=300,  # 5 minutes
    cache=Cache.MEMORY,
    key_builder=lambda f, *args, **kwargs: f"user_profile:{args[0]}",
)
async def get_user_profile(user_id: int) -> UserProfile:
    return await user_repo.get_with_preferences(user_id)
```

#### React — useMemo and useCallback

```tsx
import { useMemo, useCallback } from "react";

interface OrderSummaryProps {
  items: OrderItem[];
  taxRate: number;
  onCheckout: (total: number) => void;
}

function OrderSummary({ items, taxRate, onCheckout }: OrderSummaryProps) {
  // Memoize expensive computation — recalculates only when items or taxRate change
  const totals = useMemo(() => {
    const subtotal = items.reduce((sum, item) => sum + item.price * item.qty, 0);
    const tax = subtotal * taxRate;
    const total = subtotal + tax;
    return { subtotal, tax, total };
  }, [items, taxRate]);

  // Memoize callback to avoid re-renders in child components
  const handleCheckout = useCallback(() => {
    onCheckout(totals.total);
  }, [onCheckout, totals.total]);

  return (
    <div>
      <p>Subtotal: ${totals.subtotal.toFixed(2)}</p>
      <p>Tax: ${totals.tax.toFixed(2)}</p>
      <p>Total: ${totals.total.toFixed(2)}</p>
      <CheckoutButton onClick={handleCheckout} />
    </div>
  );
}
```

**When NOT to memoize in React:** Do not wrap every value in `useMemo`. If the computation is trivial (simple arithmetic, string concatenation, array access), the overhead of memoization exceeds the cost of recalculation. Memoize only when profiling shows a performance problem or when the value is passed as a prop to a `React.memo` child.

### 2. HTTP Caching

HTTP caching lets browsers and CDNs serve responses without hitting your server. Get this right and you can eliminate 80% or more of redundant requests.

#### Cache-Control headers

```python
# Python — FastAPI response headers
from fastapi import Response

@router.get("/api/v1/products/{product_id}")
async def get_product(product_id: int, response: Response):
    product = await product_service.get(product_id)

    # Public: CDN and browser can cache. max-age: browser TTL. s-maxage: CDN TTL.
    response.headers["Cache-Control"] = "public, max-age=60, s-maxage=300"
    return product


@router.get("/api/v1/me/profile")
async def get_my_profile(response: Response, user: User = Depends(get_current_user)):
    # Private: only browser cache, not CDN (contains user-specific data)
    response.headers["Cache-Control"] = "private, max-age=300"
    return user


@router.post("/api/v1/orders")
async def create_order(order: OrderCreate, response: Response):
    # No cache for mutations
    response.headers["Cache-Control"] = "no-store"
    return await order_service.create(order)
```

```typescript
// TypeScript — Express response headers
app.get("/api/v1/products/:id", async (req, res) => {
  const product = await productService.get(req.params.id);

  res.set("Cache-Control", "public, max-age=60, s-maxage=300");
  res.json(product);
});

// stale-while-revalidate: serve stale content while fetching fresh in background
app.get("/api/v1/feed", async (req, res) => {
  const feed = await feedService.getLatest();

  // Browser uses cache for 60s, then serves stale for up to 600s while revalidating
  res.set(
    "Cache-Control",
    "public, max-age=60, s-maxage=300, stale-while-revalidate=600"
  );
  res.json(feed);
});
```

#### ETag and conditional requests

```python
# Python — ETag-based caching
import hashlib
from fastapi import Request, Response

@router.get("/api/v1/catalog")
async def get_catalog(request: Request, response: Response):
    catalog = await catalog_service.get_full()
    catalog_json = json.dumps(catalog, sort_keys=True)

    # Generate ETag from content hash
    etag = f'"{hashlib.md5(catalog_json.encode()).hexdigest()}"'

    # Check if client already has this version
    if_none_match = request.headers.get("If-None-Match")
    if if_none_match == etag:
        return Response(status_code=304)  # Not Modified

    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "public, max-age=0, must-revalidate"
    return catalog
```

```typescript
// TypeScript — ETag middleware
import { createHash } from "node:crypto";

app.get("/api/v1/catalog", async (req, res) => {
  const catalog = await catalogService.getFull();
  const body = JSON.stringify(catalog);

  const etag = `"${createHash("md5").update(body).digest("hex")}"`;

  if (req.headers["if-none-match"] === etag) {
    res.status(304).end();
    return;
  }

  res.set("ETag", etag);
  res.set("Cache-Control", "public, max-age=0, must-revalidate");
  res.json(catalog);
});
```

#### Cache-Control cheat sheet

| Directive | Meaning |
|-----------|---------|
| `public` | Any cache (CDN, browser) may store the response |
| `private` | Only the browser may cache (not CDN) |
| `no-store` | Do not cache at all |
| `no-cache` | Cache but revalidate with server before using |
| `max-age=N` | Browser cache TTL in seconds |
| `s-maxage=N` | CDN/proxy cache TTL in seconds (overrides max-age for shared caches) |
| `must-revalidate` | Once stale, must revalidate before using |
| `stale-while-revalidate=N` | Serve stale while fetching fresh in background for N seconds |
| `immutable` | Content will never change (use for hashed assets like `app.a1b2c3.js`) |

### 3. Redis Caching

Redis is the standard external cache for web applications. It survives process restarts, can be shared across multiple servers, and supports TTL-based expiry natively.

#### Cache-aside pattern (read-through)

The most common pattern: check cache first, fetch from source on miss, populate cache for next time.

```python
# Python — redis cache-aside
import json
from typing import TypeVar, Callable, Awaitable

import redis.asyncio as redis

T = TypeVar("T")

class RedisCache:
    def __init__(self, redis_url: str, default_ttl: int = 300):
        self.client = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = default_ttl

    async def get_or_set(
        self,
        key: str,
        fetch_fn: Callable[[], Awaitable[T]],
        ttl: int | None = None,
    ) -> T:
        """Cache-aside: return cached value or fetch, cache, and return."""
        cached = await self.client.get(key)
        if cached is not None:
            return json.loads(cached)

        # Cache miss — fetch from source
        value = await fetch_fn()
        await self.client.set(
            key,
            json.dumps(value, default=str),
            ex=ttl or self.default_ttl,
        )
        return value

    async def invalidate(self, key: str) -> None:
        await self.client.delete(key)

    async def invalidate_pattern(self, pattern: str) -> None:
        """Delete all keys matching a pattern (e.g., 'user:42:*')."""
        cursor = 0
        while True:
            cursor, keys = await self.client.scan(cursor, match=pattern, count=100)
            if keys:
                await self.client.delete(*keys)
            if cursor == 0:
                break


# Usage
cache = RedisCache("redis://localhost:6379/0")

async def get_user_profile(user_id: int) -> UserProfile:
    return await cache.get_or_set(
        key=f"user_profile:{user_id}",
        fetch_fn=lambda: user_repo.get_with_preferences(user_id),
        ttl=600,  # 10 minutes
    )

async def update_user_profile(user_id: int, data: UserUpdate) -> UserProfile:
    profile = await user_repo.update(user_id, data)
    await cache.invalidate(f"user_profile:{user_id}")
    return profile
```

```typescript
// TypeScript — ioredis cache-aside
import Redis from "ioredis";

const redis = new Redis(process.env.REDIS_URL);

export class RedisCache {
  constructor(private defaultTtl = 300) {}

  async getOrSet<T>(
    key: string,
    fetchFn: () => Promise<T>,
    ttl?: number
  ): Promise<T> {
    const cached = await redis.get(key);
    if (cached !== null) {
      return JSON.parse(cached) as T;
    }

    const value = await fetchFn();
    await redis.set(key, JSON.stringify(value), "EX", ttl ?? this.defaultTtl);
    return value;
  }

  async invalidate(key: string): Promise<void> {
    await redis.del(key);
  }

  async invalidatePattern(pattern: string): Promise<void> {
    const stream = redis.scanStream({ match: pattern, count: 100 });
    const pipeline = redis.pipeline();
    for await (const keys of stream) {
      for (const key of keys as string[]) {
        pipeline.del(key);
      }
    }
    await pipeline.exec();
  }
}
```

#### Write-through pattern

Update cache and source simultaneously on writes. Guarantees cache is always fresh at the cost of slower writes.

```python
async def update_product(product_id: int, data: ProductUpdate) -> Product:
    # Update database
    product = await product_repo.update(product_id, data)

    # Update cache atomically
    await cache.client.set(
        f"product:{product_id}",
        json.dumps(product.model_dump(), default=str),
        ex=3600,
    )

    return product
```

#### TTL strategies

| Data Type | Recommended TTL | Rationale |
|-----------|----------------|-----------|
| User session data | 15-30 minutes | Balance security with UX |
| Product catalog | 5-60 minutes | Changes infrequently, high read volume |
| Search results | 1-5 minutes | Acceptable staleness, expensive to compute |
| Configuration | 5-15 minutes | Rarely changes, critical path |
| Rate limit counters | Match the rate limit window | Must be precise |
| Feature flags | 30-60 seconds | Needs to propagate quickly |

### 4. Application Cache

For single-server applications or per-process caching where Redis is overkill.

#### Python — cachetools

```python
from cachetools import TTLCache, LRUCache
from cachetools.keys import hashkey
import asyncio

# TTL cache: entries expire after 300 seconds, max 1000 entries
user_cache: TTLCache = TTLCache(maxsize=1000, ttl=300)

# LRU cache: evicts least recently used when full
template_cache: LRUCache = LRUCache(maxsize=100)

# Thread-safe / async-safe wrapper
_cache_lock = asyncio.Lock()

async def get_user_cached(user_id: int) -> User:
    key = hashkey(user_id)
    async with _cache_lock:
        if key in user_cache:
            return user_cache[key]

    # Fetch outside the lock to avoid holding it during I/O
    user = await user_repo.get(user_id)

    async with _cache_lock:
        user_cache[key] = user
    return user
```

#### TypeScript — node-cache

```typescript
import NodeCache from "node-cache";

// stdTTL: default TTL in seconds, checkperiod: cleanup interval
const cache = new NodeCache({ stdTTL: 300, checkperiod: 60 });

export async function getUserCached(userId: number): Promise<User> {
  const cacheKey = `user:${userId}`;
  const cached = cache.get<User>(cacheKey);
  if (cached !== undefined) {
    return cached;
  }

  const user = await userRepo.findById(userId);
  cache.set(cacheKey, user);
  return user;
}

// Listen for eviction events
cache.on("expired", (key: string, value: unknown) => {
  log.debug({ key }, "cache_entry_expired");
});

// Cache statistics
const stats = cache.getStats();
// { hits: 1523, misses: 89, keys: 234, ksize: 4680, vsize: 156000 }
```

### 5. CDN Caching

CDN caching moves content to edge servers close to users. Configure it correctly and your origin server handles a fraction of the traffic.

#### Cloudflare cache rules

```python
# Python — set headers that Cloudflare respects
@router.get("/api/v1/public/articles")
async def list_articles(response: Response):
    articles = await article_service.list_published()

    # Cloudflare respects s-maxage for edge cache TTL
    response.headers["Cache-Control"] = "public, s-maxage=3600, max-age=60"
    # Vary tells the CDN to cache different versions for different values
    response.headers["Vary"] = "Accept-Encoding, Accept-Language"
    return articles


# Hashed static assets — cache forever
@router.get("/assets/{filename}")
async def serve_asset(filename: str, response: Response):
    # Filenames contain content hash: app.a3b2c1.js
    response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return FileResponse(f"static/{filename}")
```

#### Cache purge on content update

```python
import httpx

async def purge_cdn_cache(urls: list[str]) -> None:
    """Purge specific URLs from Cloudflare edge cache."""
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/purge_cache",
            headers={"Authorization": f"Bearer {CF_API_TOKEN}"},
            json={"files": urls},
        )
```

```typescript
// TypeScript — purge after content update
export async function purgeCache(urls: string[]): Promise<void> {
  await fetch(
    `https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/purge_cache`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${CF_API_TOKEN}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ files: urls }),
    }
  );
}

// Purge after publishing an article
export async function publishArticle(id: string): Promise<void> {
  await articleRepo.publish(id);
  await purgeCache([
    `https://example.com/api/v1/articles/${id}`,
    `https://example.com/api/v1/articles`, // List endpoint
  ]);
}
```

#### Vary header

The `Vary` header tells the CDN to maintain separate cached versions for different request header values:

```
Vary: Accept-Encoding              → separate cache for gzip vs brotli
Vary: Accept-Language              → separate cache per language
Vary: Accept-Encoding, Authorization → DO NOT DO THIS — Authorization varies per user, so nothing is ever cached
```

**Rule:** Never include `Authorization`, `Cookie`, or other high-cardinality headers in `Vary` unless you specifically want per-user caching (which defeats the purpose of a CDN).

### 6. Cache Invalidation

The two hardest problems in computer science are cache invalidation, naming things, and off-by-one errors. Here are patterns that make invalidation manageable.

#### Tag-based invalidation

Group related cache entries under tags so you can invalidate them together.

```python
class TaggedCache:
    """Redis-backed cache with tag-based invalidation."""

    def __init__(self, redis_client):
        self.redis = redis_client

    async def set(self, key: str, value: str, ttl: int, tags: list[str]) -> None:
        pipe = self.redis.pipeline()
        pipe.set(key, value, ex=ttl)
        for tag in tags:
            pipe.sadd(f"tag:{tag}", key)
            pipe.expire(f"tag:{tag}", ttl + 60)  # Tag lives slightly longer
        await pipe.execute()

    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)

    async def invalidate_tag(self, tag: str) -> int:
        """Delete all cache entries associated with a tag."""
        tag_key = f"tag:{tag}"
        keys = await self.redis.smembers(tag_key)
        if keys:
            pipe = self.redis.pipeline()
            pipe.delete(*keys)
            pipe.delete(tag_key)
            results = await pipe.execute()
            return results[0]  # Number of deleted keys
        return 0


# Usage
cache = TaggedCache(redis_client)

# Cache a product, tagged with its category and brand
await cache.set(
    key=f"product:{product.id}",
    value=json.dumps(product.dict()),
    ttl=3600,
    tags=[f"category:{product.category_id}", f"brand:{product.brand_id}"],
)

# When a category is updated, invalidate all products in that category
await cache.invalidate_tag(f"category:{category_id}")
```

#### Event-driven invalidation

Invalidate caches in response to domain events rather than inline in business logic.

```python
# events.py
from dataclasses import dataclass

@dataclass
class ProductUpdated:
    product_id: int
    category_id: int

@dataclass
class CategoryUpdated:
    category_id: int


# event_handlers.py
async def handle_product_updated(event: ProductUpdated) -> None:
    await cache.invalidate(f"product:{event.product_id}")
    await cache.invalidate(f"product_list:category:{event.category_id}")

async def handle_category_updated(event: CategoryUpdated) -> None:
    await cache.invalidate_tag(f"category:{event.category_id}")
```

#### Versioned keys

Instead of deleting cache entries, change the key so old entries become unreachable and expire naturally.

```python
async def get_catalog_version() -> int:
    """Stored in Redis or database. Increment on catalog changes."""
    version = await redis.get("catalog:version")
    return int(version) if version else 1

async def get_catalog_cached() -> list[Product]:
    version = await get_catalog_version()
    key = f"catalog:v{version}"
    return await cache.get_or_set(key, catalog_service.get_all, ttl=3600)

async def on_catalog_change() -> None:
    """Called when any product is added, updated, or removed."""
    await redis.incr("catalog:version")
    # Old version keys expire naturally via TTL — no explicit deletion needed
```

### 7. Next.js Caching

Next.js has multiple cache layers. Understanding which layer applies to your use case avoids common bugs.

#### Data cache with fetch

```typescript
// Cached by default in Next.js App Router (builds use static generation)
async function getProducts(): Promise<Product[]> {
  const res = await fetch("https://api.example.com/products", {
    // Revalidate every 60 seconds (ISR behavior)
    next: { revalidate: 60 },
  });
  return res.json();
}

// Opt out of caching entirely
async function getCurrentUser(): Promise<User> {
  const res = await fetch("https://api.example.com/me", {
    cache: "no-store", // Always fetch fresh
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  return res.json();
}
```

#### Tag-based revalidation

```typescript
// Fetch with tags for targeted invalidation
async function getProduct(id: string): Promise<Product> {
  const res = await fetch(`https://api.example.com/products/${id}`, {
    next: {
      tags: [`product:${id}`, "products"],
    },
  });
  return res.json();
}

// Server action to revalidate
"use server";
import { revalidateTag, revalidatePath } from "next/cache";

export async function updateProduct(id: string, data: ProductUpdate) {
  await productApi.update(id, data);

  // Revalidate specific product and the list
  revalidateTag(`product:${id}`);
  revalidateTag("products");

  // Or revalidate an entire path
  revalidatePath("/products");
}
```

#### unstable_cache for non-fetch data

```typescript
import { unstable_cache } from "next/cache";

// Cache database queries or any async function
const getCachedProducts = unstable_cache(
  async (categoryId: string) => {
    return await db.product.findMany({
      where: { categoryId },
    });
  },
  ["products-by-category"], // Cache key prefix
  {
    revalidate: 300, // 5 minutes
    tags: ["products"], // For manual invalidation
  }
);

// Usage in a Server Component
export default async function ProductList({ categoryId }: Props) {
  const products = await getCachedProducts(categoryId);
  return <ProductGrid products={products} />;
}
```

#### Next.js cache layers summary

| Layer | What It Caches | Controlled By |
|-------|---------------|---------------|
| Request Memoization | Duplicate fetch calls in a single render | Automatic (same URL + options) |
| Data Cache | fetch responses on the server | `next: { revalidate }`, `cache: "no-store"` |
| Full Route Cache | Complete HTML and RSC payload | Static vs dynamic rendering |
| Router Cache | RSC payload in the browser | `revalidatePath`, `revalidateTag`, `router.refresh()` |

---

## Best Practices

1. **Cache at the right layer** — choose the caching layer closest to the consumer. HTTP caching eliminates network hops. CDN caching eliminates origin hits. Application caching eliminates database queries. Memoization eliminates repeated computation. Layer them, do not pick just one.

2. **Set TTLs based on data characteristics** — how stale can this data be before it causes a user-visible problem? Set TTL to that tolerance. A product description can be stale for minutes. An account balance cannot be stale at all.

3. **Use cache-aside as the default pattern** — read from cache, on miss fetch from source, populate cache. It is simple, handles cache failures gracefully (just hits the source), and keeps business logic decoupled from cache logic.

4. **Always set a max size or TTL** — unbounded caches cause memory leaks. Every cache should have either a size limit with eviction (LRU, LFU) or a TTL, or both. Monitor memory usage.

5. **Monitor cache hit rates** — a cache with a low hit rate is wasting memory without improving performance. Track hits, misses, and evictions. If the hit rate is below 80%, reconsider your key design or TTL.

6. **Design cache keys carefully** — keys should be deterministic, unique, and human-readable for debugging. Include a prefix identifying the data type, the relevant IDs, and optionally a version: `product:42:v3`, `user:123:profile`.

7. **Handle cache failures gracefully** — if Redis is down, fall through to the database. A cache failure should degrade performance, not break the application. Wrap cache calls in try/catch and log failures.

8. **Warm critical caches on startup** — for data that is expensive to fetch and always needed (configuration, feature flags, popular items), pre-populate the cache at application startup rather than waiting for the first user request to trigger a cold miss.

---

## Common Pitfalls

1. **Cache stampede (thundering herd)** — when a popular cache entry expires, hundreds of requests simultaneously hit the database to regenerate it. Mitigate with lock-based repopulation (only one request fetches, others wait), stale-while-revalidate (serve expired data while one request refreshes), or randomized TTLs (spread expiry times across a range).

    ```python
    # Python — lock-based stampede prevention
    async def get_with_lock(key: str, fetch_fn, ttl: int = 300) -> Any:
        cached = await redis.get(key)
        if cached is not None:
            return json.loads(cached)

        lock_key = f"lock:{key}"
        acquired = await redis.set(lock_key, "1", ex=30, nx=True)

        if acquired:
            try:
                value = await fetch_fn()
                await redis.set(key, json.dumps(value, default=str), ex=ttl)
                return value
            finally:
                await redis.delete(lock_key)
        else:
            # Another request is fetching — wait and retry
            await asyncio.sleep(0.1)
            return await get_with_lock(key, fetch_fn, ttl)
    ```

2. **Stale data in production** — a user updates their profile but keeps seeing old data because the cache was not invalidated. Always invalidate or update the cache in every write path. Use write-through caching for critical data, and test invalidation logic as carefully as you test the write itself.

3. **Caching errors** — if a database query fails and you cache the error response, every subsequent request gets the error until the TTL expires. Only cache successful results. Check the response before writing to cache.

    ```python
    # Wrong — caches None on failure
    result = await fetch_fn()
    await redis.set(key, json.dumps(result), ex=ttl)

    # Right — only cache valid results
    result = await fetch_fn()
    if result is not None:
        await redis.set(key, json.dumps(result), ex=ttl)
    ```

4. **Over-memoizing in React** — wrapping every variable in `useMemo` and every function in `useCallback` adds overhead without benefit unless the value is passed to a memoized child component or is genuinely expensive to compute. Profile first, memoize second.

5. **Forgetting the Vary header** — if your API returns different content based on `Accept-Language` or `Accept-Encoding` but does not include `Vary`, the CDN may serve the wrong cached version to users. Always set `Vary` when response content depends on request headers.

6. **Cache key collisions** — using overly generic keys like `"products"` instead of `"products:category:5:page:2:sort:price"` causes different requests to share cached data. Include all parameters that affect the response in the cache key.

---

## Related Skills

- `state-management` — Client-side state management patterns that interact with cache layers
- `postgresql` — Query optimization and connection pooling that complement caching strategies
- `mongodb` — MongoDB query patterns and when to add a cache layer
- `nextjs` — Next.js data fetching, ISR, and caching architecture
- `api-client` — Client-side caching for API responses
