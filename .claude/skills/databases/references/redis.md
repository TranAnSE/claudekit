# Databases — Redis Patterns


# Redis

## When to Use

- Caching database queries or API responses
- Session storage for web applications
- Rate limiting (distributed across instances)
- Job/task queues (BullMQ, Celery)
- Pub/sub messaging between services
- Distributed locks

## When NOT to Use

- **Primary data storage** — Redis is a cache/broker, not a database of record
- **Complex queries** — use PostgreSQL for relational queries
- **Large blobs** — use S3/R2 for file storage
- **In-memory caching only** — use `functools.lru_cache` or `Map` for single-process caches

---

## Python (redis-py / FastAPI)

### Connection

```python
# src/core/redis.py
import redis.asyncio as redis

pool = redis.ConnectionPool.from_url(
    "redis://localhost:6379/0",
    max_connections=20,
    decode_responses=True,
)

async def get_redis() -> redis.Redis:
    return redis.Redis(connection_pool=pool)
```

### Cache-aside pattern

```python
import json
from datetime import timedelta

async def get_user_cached(user_id: str, db: AsyncSession) -> User:
    r = await get_redis()
    cache_key = f"user:{user_id}"

    # Check cache
    cached = await r.get(cache_key)
    if cached:
        return User(**json.loads(cached))

    # Cache miss — fetch from DB
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Store in cache with TTL
    await r.setex(cache_key, timedelta(minutes=15), json.dumps(user.to_dict()))
    return user
```

### Cache invalidation

```python
async def update_user(user_id: str, data: UpdateUserRequest, db: AsyncSession) -> User:
    user = await db.get(User, user_id)
    for key, value in data.dict(exclude_unset=True).items():
        setattr(user, key, value)
    await db.commit()

    # Invalidate cache
    r = await get_redis()
    await r.delete(f"user:{user_id}")

    return user
```

### Rate limiting

```python
from fastapi import Request, HTTPException

async def rate_limit(request: Request, limit: int = 100, window: int = 900):
    r = await get_redis()
    key = f"rate:{request.client.host}"
    current = await r.incr(key)
    if current == 1:
        await r.expire(key, window)
    if current > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
```

### Session storage

```python
import secrets

async def create_session(user_id: str) -> str:
    r = await get_redis()
    session_id = secrets.token_urlsafe(32)
    await r.setex(f"session:{session_id}", timedelta(hours=24), user_id)
    return session_id

async def get_session(session_id: str) -> str | None:
    r = await get_redis()
    return await r.get(f"session:{session_id}")

async def delete_session(session_id: str):
    r = await get_redis()
    await r.delete(f"session:{session_id}")
```

---

## TypeScript (ioredis / NestJS / Express)

### Connection

```typescript
// src/core/redis.ts
import Redis from 'ioredis';

export const redis = new Redis(process.env.REDIS_URL ?? 'redis://localhost:6379', {
  maxRetriesPerRequest: 3,
  lazyConnect: true,
});
```

### NestJS module

```typescript
// src/cache/cache.module.ts
import { Global, Module } from '@nestjs/common';
import { CacheService } from './cache.service';

@Global()
@Module({
  providers: [CacheService],
  exports: [CacheService],
})
export class CacheModule {}
```

```typescript
// src/cache/cache.service.ts
import { Injectable, OnModuleDestroy } from '@nestjs/common';
import Redis from 'ioredis';

@Injectable()
export class CacheService implements OnModuleDestroy {
  private readonly redis = new Redis(process.env.REDIS_URL!);

  async get<T>(key: string): Promise<T | null> {
    const data = await this.redis.get(key);
    return data ? JSON.parse(data) : null;
  }

  async set(key: string, value: unknown, ttlSeconds: number): Promise<void> {
    await this.redis.setex(key, ttlSeconds, JSON.stringify(value));
  }

  async del(key: string): Promise<void> {
    await this.redis.del(key);
  }

  async onModuleDestroy() {
    await this.redis.quit();
  }
}
```

### Cache-aside in service

```typescript
@Injectable()
export class UsersService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly cache: CacheService,
  ) {}

  async findOne(id: string): Promise<User> {
    // Check cache
    const cached = await this.cache.get<User>(`user:${id}`);
    if (cached) return cached;

    // Cache miss
    const user = await this.prisma.user.findUnique({ where: { id } });
    if (!user) throw new NotFoundException(`User ${id} not found`);

    // Store with 15min TTL
    await this.cache.set(`user:${id}`, user, 900);
    return user;
  }

  async update(id: string, dto: UpdateUserDto): Promise<User> {
    const user = await this.prisma.user.update({ where: { id }, data: dto });
    await this.cache.del(`user:${id}`);  // Invalidate
    return user;
  }
}
```

---

## Pub/Sub

### Python

```python
# Publisher
async def publish_event(channel: str, event: dict):
    r = await get_redis()
    await r.publish(channel, json.dumps(event))

# Subscriber
async def subscribe_events(channel: str):
    r = await get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(channel)
    async for message in pubsub.listen():
        if message['type'] == 'message':
            yield json.loads(message['data'])
```

### TypeScript

```typescript
// Publisher
const pub = new Redis(process.env.REDIS_URL!);
await pub.publish('orders', JSON.stringify({ type: 'created', orderId: '123' }));

// Subscriber (separate connection required)
const sub = new Redis(process.env.REDIS_URL!);
sub.subscribe('orders');
sub.on('message', (channel, message) => {
  const event = JSON.parse(message);
  console.log(`[${channel}]`, event);
});
```

---

## Key Naming Conventions

```
entity:id              → user:abc123
entity:id:field        → user:abc123:orders
rate:ip                → rate:192.168.1.1
session:token          → session:abc123def
lock:resource          → lock:order-processing
queue:name             → queue:email-notifications
```

---

## Common Pitfalls

1. **Not setting TTLs.** Every cache key should have an expiration. Unbounded caches exhaust memory.
2. **Cache stampede.** When a popular key expires, many requests hit the DB simultaneously. Use distributed locks or stale-while-revalidate.
3. **Using the same connection for pub/sub.** Subscribers can't run other commands. Use a dedicated connection.
4. **Storing large objects.** Redis is fast for small values. Keep values under 1MB; for larger data, store a pointer to S3.
5. **Not handling connection failures.** Redis connections drop. Use retry logic and connection pools.
6. **Forgetting to invalidate.** When data changes, delete the cache key. Stale cache is worse than no cache.

---

## Related Skills

- `caching` — HTTP caching, CDN, memoization (framework-agnostic patterns)
- `background-jobs` — BullMQ/Celery use Redis as broker
- `fastapi` — Redis integration with FastAPI dependency injection
- `nestjs` — Redis caching module in NestJS
- `docker` — Running Redis in Docker Compose for development
