# DevOps — Cloudflare Workers Patterns


# Cloudflare Workers & Pages

## Overview

Edge-first deployment patterns for Cloudflare's platform. Covers Workers (compute), Pages (static + SSR), R2 (object storage), D1 (SQLite at edge), KV (key-value), Durable Objects (stateful), and Queues (async processing). Focused on the Python/TypeScript stack this kit targets.

## When to Use
- Deploying APIs or full-stack apps to Cloudflare's edge network
- Building serverless functions with Workers
- Deploying Next.js or static sites via Cloudflare Pages
- Using D1 (edge SQLite), R2 (S3-compatible storage), or KV (low-latency reads)
- Implementing real-time coordination with Durable Objects
- Background job processing with Cloudflare Queues

## When NOT to Use
- **Long-running compute** (> 30s CPU) — use traditional servers or containers
- **Heavy database workloads** — D1 is SQLite; use Postgres/Mongo for complex queries
- **GPU/ML inference** (unless using Workers AI) — use dedicated compute
- **Local-only development** — Workers run on V8 isolates, not Node.js

---

## Quick Reference

| I need... | Go to |
|-----------|-------|
| Worker project structure | § Project Structure below |
| Hono framework on Workers | § Hono Framework below |
| D1 database patterns | § D1 (Edge SQLite) below |
| R2 object storage | § R2 (Object Storage) below |
| KV key-value store | § KV below |
| Durable Objects | § Durable Objects below |
| Pages deployment (Next.js) | § Cloudflare Pages below |
| CI/CD with GitHub Actions | § CI/CD below |
| Wrangler config reference | See `wrangler-patterns.md` in this skill's directory |

---

## Project Structure

```
my-worker/
├── wrangler.toml           # Wrangler config (bindings, routes, env)
├── src/
│   ├── index.ts            # Entry point (fetch handler)
│   ├── routes/             # Route handlers
│   ├── middleware/          # Auth, CORS, logging
│   ├── services/           # Business logic
│   └── types.ts            # Env bindings type
├── migrations/             # D1 migrations
├── test/                   # Vitest tests
└── package.json
```

### Entry point

```typescript
// src/index.ts
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/health') {
      return Response.json({ status: 'ok' });
    }

    // Route to handlers...
    return new Response('Not found', { status: 404 });
  },
} satisfies ExportedHandler<Env>;
```

### Type-safe bindings

```typescript
// src/types.ts
export interface Env {
  DB: D1Database;
  BUCKET: R2Bucket;
  CACHE: KVNamespace;
  API_KEY: string;
  ENVIRONMENT: 'development' | 'staging' | 'production';
}
```

---

## Hono Framework (Recommended)

Hono is the de facto framework for Workers — ultralight (~14KB), type-safe, and built for edge runtimes.

```typescript
// src/index.ts
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';
import { HTTPException } from 'hono/http-exception';
import { zValidator } from '@hono/zod-validator';
import { z } from 'zod';

type Bindings = {
  DB: D1Database;
  BUCKET: R2Bucket;
  API_KEY: string;
};

const app = new Hono<{ Bindings: Bindings }>();

app.use('*', logger());
app.use('*', cors({ origin: ['https://app.example.com'], credentials: true }));

// Health check
app.get('/health', (c) => c.json({ status: 'ok' }));

// Validated endpoint
const createUserSchema = z.object({
  email: z.string().email().max(254),
  name: z.string().min(1).max(100),
});

app.post('/v1/users', zValidator('json', createUserSchema), async (c) => {
  const { email, name } = c.req.valid('json');
  const result = await c.env.DB
    .prepare('INSERT INTO users (id, email, name) VALUES (?, ?, ?) RETURNING *')
    .bind(crypto.randomUUID(), email, name)
    .first();
  return c.json(result, 201);
});

// Error handling — RFC 9457 Problem Details
app.onError((err, c) => {
  if (err instanceof HTTPException) {
    return c.json({
      type: `https://api.example.com/problems/${err.status}`,
      title: err.message,
      status: err.status,
    }, err.status);
  }
  console.error(err);
  return c.json({
    type: 'https://api.example.com/problems/internal-error',
    title: 'Internal server error',
    status: 500,
  }, 500);
});

export default app;
```

---

## D1 (Edge SQLite)

Cloudflare's serverless SQL database. SQLite at the edge with automatic replication.

### Migrations

```bash
# Create migration
npx wrangler d1 migrations create my-db create-users

# Apply locally
npx wrangler d1 migrations apply my-db --local

# Apply to production
npx wrangler d1 migrations apply my-db --remote
```

```sql
-- migrations/0001_create-users.sql
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  role TEXT DEFAULT 'member' CHECK(role IN ('admin', 'member', 'viewer')),
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_users_email ON users(email);
```

### Querying with prepared statements

```typescript
// Always use prepared statements — never concatenate SQL
async function getUser(db: D1Database, id: string) {
  return db.prepare('SELECT * FROM users WHERE id = ?').bind(id).first();
}

async function listUsers(db: D1Database, cursor?: string, limit = 20) {
  const stmt = cursor
    ? db.prepare('SELECT * FROM users WHERE id > ? ORDER BY id LIMIT ?').bind(cursor, limit)
    : db.prepare('SELECT * FROM users ORDER BY id LIMIT ?').bind(limit);
  return stmt.all();
}

// Batch multiple statements in a transaction
async function transferCredits(db: D1Database, from: string, to: string, amount: number) {
  const results = await db.batch([
    db.prepare('UPDATE accounts SET balance = balance - ? WHERE id = ?').bind(amount, from),
    db.prepare('UPDATE accounts SET balance = balance + ? WHERE id = ?').bind(amount, to),
  ]);
  return results;
}
```

### D1 limitations to know

- **No JOINs across databases** — one D1 database per binding
- **5MB max row size**, 10GB max database
- **Read replicas are automatic** but writes go to a single leader
- **No stored procedures / triggers** — SQLite subset
- **Prepared statements are mandatory** — `db.exec()` with raw SQL is for migrations only

---

## R2 (Object Storage)

S3-compatible object storage without egress fees.

```typescript
// Upload
app.put('/v1/files/:key', async (c) => {
  const key = c.req.param('key');
  const body = await c.req.arrayBuffer();
  const contentType = c.req.header('Content-Type') ?? 'application/octet-stream';

  await c.env.BUCKET.put(key, body, {
    httpMetadata: { contentType },
    customMetadata: { uploadedBy: c.get('userId') },
  });

  return c.json({ key, size: body.byteLength }, 201);
});

// Download
app.get('/v1/files/:key', async (c) => {
  const obj = await c.env.BUCKET.get(c.req.param('key'));
  if (!obj) return c.json({ error: 'Not found' }, 404);

  return new Response(obj.body, {
    headers: {
      'Content-Type': obj.httpMetadata?.contentType ?? 'application/octet-stream',
      'ETag': obj.etag,
    },
  });
});

// List with prefix
app.get('/v1/files', async (c) => {
  const prefix = c.req.query('prefix') ?? '';
  const listed = await c.env.BUCKET.list({ prefix, limit: 100 });
  return c.json({ objects: listed.objects.map((o) => ({ key: o.key, size: o.size })) });
});
```

### Presigned URLs for direct upload

```typescript
// Generate a presigned URL so clients upload directly to R2
app.post('/v1/upload-url', async (c) => {
  const key = `uploads/${crypto.randomUUID()}`;
  // Use the S3-compatible API for presigned URLs
  // Requires R2 API token with write access
  return c.json({ key, uploadUrl: `https://${ACCOUNT_ID}.r2.cloudflarestorage.com/${BUCKET_NAME}/${key}` });
});
```

---

## KV (Key-Value Store)

Global low-latency reads (~10ms worldwide), eventually consistent writes.

```typescript
// Set with TTL
await c.env.CACHE.put('session:abc123', JSON.stringify(sessionData), {
  expirationTtl: 3600, // 1 hour
});

// Get with type safety
const raw = await c.env.CACHE.get('session:abc123');
const session = raw ? JSON.parse(raw) as SessionData : null;

// List keys by prefix
const keys = await c.env.CACHE.list({ prefix: 'session:' });

// Delete
await c.env.CACHE.delete('session:abc123');
```

**Use KV for:** session tokens, feature flags, cached API responses, configuration. **Not for:** frequently updated counters, multi-key transactions (use Durable Objects).

---

## Durable Objects

Stateful, single-instance coordination. Each Durable Object has a unique ID and runs in exactly one location.

```typescript
// src/counter.ts
export class Counter implements DurableObject {
  private count = 0;

  constructor(private state: DurableObjectState, private env: Env) {}

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/increment') {
      this.count++;
      await this.state.storage.put('count', this.count);
      return Response.json({ count: this.count });
    }

    this.count = (await this.state.storage.get<number>('count')) ?? 0;
    return Response.json({ count: this.count });
  }
}

// In the Worker, route to the Durable Object:
app.post('/v1/counters/:name/increment', async (c) => {
  const id = c.env.COUNTER.idFromName(c.req.param('name'));
  const stub = c.env.COUNTER.get(id);
  const res = await stub.fetch(new Request('https://dummy/increment'));
  return c.json(await res.json());
});
```

**Use Durable Objects for:** rate limiting, WebSocket rooms, collaborative editing, distributed locks, shopping carts. **Not for:** read-heavy caching (use KV).

---

## Cloudflare Pages

### Next.js on Pages

```bash
# Deploy Next.js to Cloudflare Pages
npx wrangler pages deploy .next --project-name=my-app
```

Use `@cloudflare/next-on-pages` for full App Router + Server Components support:

```bash
pnpm add @cloudflare/next-on-pages
```

```typescript
// next.config.ts
import { setupDevPlatform } from '@cloudflare/next-on-pages/next-dev';

if (process.env.NODE_ENV === 'development') {
  await setupDevPlatform();
}

const nextConfig = { /* ... */ };
export default nextConfig;
```

### Static site on Pages

```bash
# Build and deploy
pnpm build
npx wrangler pages deploy dist/ --project-name=my-site
```

Pages auto-deploys from GitHub: connect your repo in the Cloudflare dashboard, set the build command and output directory. Preview deploys on every PR.

---

## Wrangler Config

```toml
# wrangler.toml
name = "my-api"
main = "src/index.ts"
compatibility_date = "2026-01-01"
compatibility_flags = ["nodejs_compat"]

[vars]
ENVIRONMENT = "production"

# D1 database
[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# R2 bucket
[[r2_buckets]]
binding = "BUCKET"
bucket_name = "my-bucket"

# KV namespace
[[kv_namespaces]]
binding = "CACHE"
id = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Durable Object
[[durable_objects.bindings]]
name = "COUNTER"
class_name = "Counter"

[[migrations]]
tag = "v1"
new_classes = ["Counter"]

# Environment overrides
[env.staging]
vars = { ENVIRONMENT = "staging" }

[env.staging.d1_databases]
binding = "DB"
database_name = "my-db-staging"
database_id = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
```

**`compatibility_date`** pins your Worker to a specific runtime version. Always set it to a recent date and update periodically. **`nodejs_compat`** enables Node.js built-in APIs (Buffer, crypto, streams) — required for most npm packages.

---

## CI/CD

### GitHub Actions deploy

```yaml
# .github/workflows/deploy.yml
name: Deploy Worker
on:
  push:
    branches: [main]
  pull_request:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: pnpm install

      - name: Run tests
        run: pnpm test

      - name: Apply D1 migrations (production)
        if: github.ref == 'refs/heads/main'
        run: npx wrangler d1 migrations apply my-db --remote
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CF_API_TOKEN }}

      - name: Deploy to staging (PR)
        if: github.event_name == 'pull_request'
        run: npx wrangler deploy --env staging
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CF_API_TOKEN }}

      - name: Deploy to production
        if: github.ref == 'refs/heads/main'
        run: npx wrangler deploy
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CF_API_TOKEN }}
```

### Local development

```bash
# Start local dev server with all bindings (D1, R2, KV, DO)
npx wrangler dev

# With local D1 persistence
npx wrangler dev --persist-to .wrangler/state
```

`wrangler dev` uses Miniflare under the hood — a local simulator for all Cloudflare primitives. Test against real bindings locally before deploying.

---

## Testing

Use **Vitest + Miniflare** (via `@cloudflare/vitest-pool-workers`):

```typescript
// vitest.config.ts
import { defineWorkersConfig } from '@cloudflare/vitest-pool-workers/config';

export default defineWorkersConfig({
  test: {
    poolOptions: {
      workers: {
        wrangler: { configPath: './wrangler.toml' },
      },
    },
  },
});
```

```typescript
// test/index.spec.ts
import { env, createExecutionContext, waitOnExecutionContext } from 'cloudflare:test';
import { describe, it, expect } from 'vitest';
import worker from '../src/index';

describe('Worker', () => {
  it('returns health check', async () => {
    const request = new Request('http://localhost/health');
    const ctx = createExecutionContext();
    const response = await worker.fetch(request, env, ctx);
    await waitOnExecutionContext(ctx);

    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body).toEqual({ status: 'ok' });
  });
});
```

---

## Common Pitfalls

1. **Using Node.js APIs without `nodejs_compat`.** Workers run on V8, not Node.js. Without the flag, `Buffer`, `crypto`, `process` are undefined.
2. **Blocking the event loop.** Workers have strict CPU time limits (10ms free, 30s paid). Heavy computation blocks all concurrent requests. Use `ctx.waitUntil()` for background work.
3. **Ignoring D1's eventually consistent reads.** Writes go to the leader; reads from replicas may lag by seconds. Design for eventual consistency.
4. **Using KV for frequently updated data.** KV is eventually consistent with ~60s propagation. Use Durable Objects for strong consistency.
5. **Not setting `compatibility_date`.** Without it, you get the oldest runtime behavior. Always pin to a recent date.
6. **Forgetting `ctx.waitUntil()`.** Background work (logging, analytics) must be wrapped in `waitUntil()` or it gets killed when the response is sent.
7. **Large Worker bundles.** Workers have a 10MB compressed limit (free: 1MB). Tree-shake aggressively; avoid heavy npm packages.
8. **Not testing locally with Miniflare.** `wrangler dev` simulates all bindings locally. Deploying untested changes to edge = debugging in production.

---

## Related Skills

- `docker` — alternative deployment model (containers vs edge)
- `github-actions` — CI/CD pipeline for deploying Workers
- `vitest` — testing Workers with Miniflare pool
