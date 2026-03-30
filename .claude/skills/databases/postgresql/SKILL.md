---
name: postgresql
description: >
  Use this skill whenever working with PostgreSQL databases, writing SQL queries, designing schemas, or optimizing database performance. Trigger on keywords like PostgreSQL, Postgres, SQL query, schema design, indexing, migrations, EXPLAIN ANALYZE, connection pooling, or any relational database operation. Also applies when debugging slow queries, setting up database tables, or working with ORMs that target PostgreSQL.
---

# PostgreSQL

## When to Use

- PostgreSQL database operations
- SQL query optimization
- Schema design and migrations
- JSONB document storage within a relational model
- Full-text search without a dedicated search engine
- Complex analytical queries with window functions and CTEs

## When NOT to Use

- NoSQL-only projects where no relational database is involved
- In-memory databases like Redis or SQLite used purely for caching or ephemeral storage
- File-based storage scenarios that do not require a database engine

---

## Core Patterns

### 1. Schema Design

Design tables with explicit constraints, proper types, and clear relationships.

```sql
-- Enums for constrained value sets
CREATE TYPE user_role AS ENUM ('admin', 'editor', 'viewer');
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');

-- Composite types for reusable structures
CREATE TYPE address AS (
    street TEXT,
    city   TEXT,
    state  TEXT,
    zip    VARCHAR(10)
);

-- Users table with constraints
CREATE TABLE users (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email       TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL CHECK (char_length(name) >= 1),
    role        user_role NOT NULL DEFAULT 'viewer',
    metadata    JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Organizations with self-referencing hierarchy
CREATE TABLE organizations (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        TEXT NOT NULL,
    parent_id   BIGINT REFERENCES organizations(id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Membership join table with composite primary key
CREATE TABLE org_memberships (
    user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    org_id      BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    role        user_role NOT NULL DEFAULT 'viewer',
    joined_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, org_id)
);

-- Orders with foreign keys, check constraints, and enum status
CREATE TABLE orders (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    status      order_status NOT NULL DEFAULT 'pending',
    total_cents BIGINT NOT NULL CHECK (total_cents >= 0),
    shipping    address,
    items       JSONB NOT NULL DEFAULT '[]',
    placed_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Auto-update updated_at with a trigger
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
```

**Key principles:**
- Use `BIGINT GENERATED ALWAYS AS IDENTITY` over `SERIAL` for new projects
- Use `TIMESTAMPTZ` (not `TIMESTAMP`) to store times with timezone awareness
- Prefer `TEXT` over `VARCHAR(n)` unless a hard length limit is business-critical
- Add `ON DELETE` actions on every foreign key (CASCADE, RESTRICT, or SET NULL)
- Use `CHECK` constraints for business rules that live at the data level

---

### 2. Index Strategy

Choose the right index type based on your query patterns.

**Decision guide:**

| Query Pattern | Index Type | Example |
|---------------|-----------|---------|
| Equality (`=`) and range (`<`, `>`, `BETWEEN`) | B-tree (default) | `WHERE created_at > '2025-01-01'` |
| Array containment (`@>`), JSONB queries | GIN | `WHERE tags @> '{postgres}'` |
| Full-text search (`@@`) | GIN | `WHERE to_tsvector(body) @@ query` |
| Geometry, range overlap | GiST | `WHERE location <-> point '(40.7,-74.0)' < 0.01` |
| Filtered subset of rows | Partial | `WHERE active = true` |
| Index-only scans (no heap lookup) | Covering (INCLUDE) | Frequently selected columns |

```sql
-- B-tree: default, good for equality and range
CREATE INDEX idx_orders_placed_at ON orders(placed_at DESC);
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- GIN: arrays and JSONB containment
CREATE INDEX idx_users_metadata ON users USING GIN (metadata);
CREATE INDEX idx_orders_items ON orders USING GIN (items jsonb_path_ops);

-- GIN: full-text search
ALTER TABLE articles ADD COLUMN search_vector tsvector
    GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(body, '')), 'B')
    ) STORED;

CREATE INDEX idx_articles_search ON articles USING GIN (search_vector);

-- Full-text search query
SELECT id, title, ts_rank(search_vector, query) AS rank
FROM articles, plainto_tsquery('english', 'database optimization') AS query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 20;

-- GiST: geometry and range types
CREATE INDEX idx_events_duration ON events USING GiST (
    tstzrange(starts_at, ends_at)
);

-- Find overlapping events
SELECT * FROM events
WHERE tstzrange(starts_at, ends_at) && tstzrange('2025-06-01', '2025-06-02');

-- Partial index: only index rows you actually query
CREATE INDEX idx_orders_pending ON orders(placed_at)
    WHERE status = 'pending';

-- Covering index: avoids heap lookup for common queries
CREATE INDEX idx_users_email_covering ON users(email)
    INCLUDE (name, role);

-- This query can now be answered entirely from the index
SELECT name, role FROM users WHERE email = 'user@example.com';
```

**When to add an index:** Run `EXPLAIN ANALYZE` first. Add an index when you see sequential scans on large tables with selective WHERE clauses. Do not index columns with very low cardinality (e.g., a boolean on a small table) unless combined with other columns.

---

### 3. Query Optimization

#### Reading EXPLAIN ANALYZE

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE o.placed_at > now() - INTERVAL '30 days'
GROUP BY u.id, u.name
ORDER BY order_count DESC
LIMIT 10;
```

**What to look for in the output:**
- **Seq Scan on large tables** -- add an index or rewrite the WHERE clause
- **Nested Loop with high row counts** -- consider a Hash Join (may need more `work_mem`)
- **actual rows far exceeding estimated rows** -- run `ANALYZE tablename` to update statistics
- **Buffers: shared read** large numbers -- data not cached, check `shared_buffers` sizing
- **Sort Method: external merge** -- increase `work_mem` for this query

#### Common Query Rewrites

```sql
-- BAD: correlated subquery runs once per row
SELECT u.name,
    (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) AS order_count
FROM users u;

-- GOOD: single pass with JOIN + GROUP BY
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name;

-- BAD: OR on different columns defeats index usage
SELECT * FROM orders WHERE user_id = 5 OR status = 'pending';

-- GOOD: UNION ALL lets each branch use its own index
SELECT * FROM orders WHERE user_id = 5
UNION ALL
SELECT * FROM orders WHERE status = 'pending' AND user_id != 5;

-- BAD: function call on indexed column prevents index use
SELECT * FROM users WHERE LOWER(email) = 'user@example.com';

-- GOOD: expression index or use citext
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
-- or better: define email as CITEXT type

-- Avoiding N+1: fetch users and their latest order in one query
SELECT DISTINCT ON (u.id)
    u.id, u.name, o.id AS latest_order_id, o.total_cents, o.placed_at
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
ORDER BY u.id, o.placed_at DESC;
```

---

### 4. Migrations

Follow the up/down pattern and plan for zero-downtime deployments.

```sql
-- ============================================
-- Migration: 20250601_001_add_user_preferences
-- ============================================

-- UP
ALTER TABLE users ADD COLUMN preferences JSONB DEFAULT '{}';

-- Create index CONCURRENTLY to avoid locking the table
CREATE INDEX CONCURRENTLY idx_users_preferences
    ON users USING GIN (preferences);

-- DOWN
DROP INDEX IF EXISTS idx_users_preferences;
ALTER TABLE users DROP COLUMN IF EXISTS preferences;
```

**Safe vs unsafe operations:**

| Operation | Safe? | Notes |
|-----------|-------|-------|
| ADD COLUMN (nullable or with volatile default) | Yes | Instant in PG 11+ with non-volatile default too |
| ADD COLUMN NOT NULL without default | No | Fails if rows exist; add nullable first, backfill, then set NOT NULL |
| DROP COLUMN | Mostly | Quick, but ORM queries may break if they SELECT * |
| RENAME COLUMN | Dangerous | Breaks all queries referencing old name; use a transition period |
| ADD INDEX | Safe with CONCURRENTLY | Without CONCURRENTLY, locks writes for duration |
| ADD CONSTRAINT (CHECK/FK) | Careful | Use NOT VALID then VALIDATE CONSTRAINT in two steps |
| Change column type | Dangerous | Rewrites entire table; use a new column + migration instead |

```sql
-- Zero-downtime: add NOT NULL constraint safely
-- Step 1: add column as nullable
ALTER TABLE users ADD COLUMN phone TEXT;

-- Step 2: backfill in batches
UPDATE users SET phone = '' WHERE phone IS NULL AND id BETWEEN 1 AND 10000;
UPDATE users SET phone = '' WHERE phone IS NULL AND id BETWEEN 10001 AND 20000;
-- ... continue in batches

-- Step 3: add constraint without full table lock
ALTER TABLE users ADD CONSTRAINT users_phone_not_null
    CHECK (phone IS NOT NULL) NOT VALID;

-- Step 4: validate (scans table but allows concurrent writes)
ALTER TABLE users VALIDATE CONSTRAINT users_phone_not_null;

-- Step 5: optionally convert to proper NOT NULL
ALTER TABLE users ALTER COLUMN phone SET NOT NULL;
ALTER TABLE users DROP CONSTRAINT users_phone_not_null;
```

---

### 5. JSON/JSONB

Use JSONB for semi-structured data that lives alongside relational columns.

**When to use JSONB:**
- User preferences, settings, or metadata with varying keys
- API response caching or event payloads
- Flexible attributes that differ per row

**When NOT to use JSONB:**
- Data you regularly JOIN on or use in WHERE clauses across tables -- normalize it
- Data that has a fixed, well-known schema -- use proper columns

```sql
-- Querying JSONB: operators
-- ->  returns JSONB element (keeps type)
-- ->> returns TEXT value
-- @>  containment (left contains right)
-- ?   key exists

-- Get a nested value
SELECT
    metadata->>'department' AS department,
    metadata->'settings'->>'theme' AS theme
FROM users
WHERE metadata @> '{"role": "admin"}';

-- Check if a key exists
SELECT * FROM users WHERE metadata ? 'avatar_url';

-- Query inside JSONB arrays
SELECT * FROM orders
WHERE items @> '[{"sku": "WIDGET-001"}]';

-- Update a nested JSONB field
UPDATE users
SET metadata = jsonb_set(metadata, '{settings,notifications}', '"email"')
WHERE id = 42;

-- Remove a key
UPDATE users
SET metadata = metadata - 'deprecated_field'
WHERE metadata ? 'deprecated_field';

-- Aggregate JSONB: expand array elements into rows
SELECT o.id, item->>'sku' AS sku, (item->>'qty')::int AS qty
FROM orders o, jsonb_array_elements(o.items) AS item
WHERE o.status = 'pending';

-- Index strategies for JSONB
-- General containment queries: GIN with jsonb_ops (default)
CREATE INDEX idx_users_metadata_gin ON users USING GIN (metadata);

-- Containment-only queries (smaller, faster index): jsonb_path_ops
CREATE INDEX idx_orders_items_path ON orders USING GIN (items jsonb_path_ops);

-- Specific key lookups: expression index on extracted value
CREATE INDEX idx_users_department ON users ((metadata->>'department'));
```

---

### 6. CTEs and Window Functions

#### Common Table Expressions (CTEs)

```sql
-- Readable multi-step query with CTEs
WITH monthly_revenue AS (
    SELECT
        date_trunc('month', placed_at) AS month,
        SUM(total_cents) AS revenue_cents
    FROM orders
    WHERE status = 'delivered'
    GROUP BY 1
),
revenue_with_growth AS (
    SELECT
        month,
        revenue_cents,
        LAG(revenue_cents) OVER (ORDER BY month) AS prev_month,
        ROUND(
            100.0 * (revenue_cents - LAG(revenue_cents) OVER (ORDER BY month))
            / NULLIF(LAG(revenue_cents) OVER (ORDER BY month), 0),
            1
        ) AS growth_pct
    FROM monthly_revenue
)
SELECT * FROM revenue_with_growth ORDER BY month DESC;

-- Recursive CTE: org hierarchy tree
WITH RECURSIVE org_tree AS (
    -- Base case: top-level orgs
    SELECT id, name, parent_id, 0 AS depth, name::TEXT AS path
    FROM organizations
    WHERE parent_id IS NULL

    UNION ALL

    -- Recursive step
    SELECT o.id, o.name, o.parent_id, t.depth + 1, t.path || ' > ' || o.name
    FROM organizations o
    JOIN org_tree t ON o.parent_id = t.id
)
SELECT * FROM org_tree ORDER BY path;
```

#### Window Functions

```sql
-- ROW_NUMBER: assign rank within a partition
SELECT
    user_id,
    id AS order_id,
    total_cents,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY placed_at DESC) AS rn
FROM orders;

-- Get each user's most recent order
SELECT * FROM (
    SELECT
        o.*,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY placed_at DESC) AS rn
    FROM orders o
) sub WHERE rn = 1;

-- LAG/LEAD: compare with previous/next row
SELECT
    placed_at::date AS order_date,
    total_cents,
    LAG(total_cents) OVER (ORDER BY placed_at) AS prev_order_total,
    total_cents - LAG(total_cents) OVER (ORDER BY placed_at) AS diff
FROM orders
WHERE user_id = 42;

-- Running total
SELECT
    placed_at::date AS order_date,
    total_cents,
    SUM(total_cents) OVER (
        ORDER BY placed_at
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total
FROM orders
WHERE user_id = 42;

-- NTILE: divide rows into equal buckets (e.g., quartiles)
SELECT
    user_id,
    SUM(total_cents) AS lifetime_spend,
    NTILE(4) OVER (ORDER BY SUM(total_cents) DESC) AS spend_quartile
FROM orders
GROUP BY user_id;
```

---

### 7. Transaction Isolation

PostgreSQL supports four isolation levels. The two most commonly used:

| Level | Dirty Read | Non-Repeatable Read | Phantom Read | Use Case |
|-------|-----------|-------------------|-------------|----------|
| READ COMMITTED (default) | No | Possible | Possible | Most OLTP workloads |
| REPEATABLE READ | No | No | No (in PG) | Reports, consistent snapshots |
| SERIALIZABLE | No | No | No | Financial transactions, inventory |

```sql
-- Default: READ COMMITTED
-- Each statement sees the latest committed data
BEGIN;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- SERIALIZABLE: full isolation, detects write conflicts
BEGIN ISOLATION LEVEL SERIALIZABLE;
    -- Read current inventory
    SELECT quantity FROM inventory WHERE sku = 'WIDGET-001';
    -- Decrement if sufficient (PG will abort if concurrent tx conflicts)
    UPDATE inventory SET quantity = quantity - 1 WHERE sku = 'WIDGET-001';
COMMIT;
-- If another SERIALIZABLE tx modified the same row, one will get:
-- ERROR: could not serialize access due to concurrent update
-- Your application must retry on serialization failure (SQLSTATE 40001)

-- Advisory locks for application-level coordination
SELECT pg_advisory_xact_lock(hashtext('process-user-' || '42'));
-- Lock is held until transaction ends; no table-level contention
```

**Guidelines:**
- Use READ COMMITTED for general CRUD operations
- Use SERIALIZABLE when correctness requires that concurrent transactions behave as if run sequentially (e.g., balance transfers, seat reservations)
- Always implement retry logic for serialization failures
- Keep transactions as short as possible to reduce contention

---

### 8. Connection Pooling

Direct PostgreSQL connections are expensive (~1-10 MB RAM each). Use a pooler.

**PgBouncer configuration (pgbouncer.ini):**

```ini
[databases]
myapp = host=127.0.0.1 port=5432 dbname=myapp

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = 6432
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt

; Pool mode: transaction is best for most web apps
pool_mode = transaction

; Sizing: start conservative, tune with monitoring
default_pool_size = 20
max_client_conn = 200
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 3

; Timeouts
server_idle_timeout = 300
client_idle_timeout = 60
query_timeout = 30
```

**Pool sizing formula:**

```
optimal_pool_size = ((2 * cpu_cores) + effective_disk_spindles)
```

For a 4-core SSD server: `(2 * 4) + 1 = 9` connections is a good starting point. More connections does not mean more throughput -- too many causes contention.

**Pool modes:**

| Mode | Description | Caveats |
|------|-------------|---------|
| `transaction` | Connection returned after each transaction | Cannot use session-level features (LISTEN/NOTIFY, prepared statements, temp tables) |
| `session` | Connection held for entire client session | Fewer pooling benefits; use only when session features needed |
| `statement` | Connection returned after each statement | No multi-statement transactions; rarely used |

**Application-level pooling (Python example with asyncpg):**

```python
import asyncpg

pool = await asyncpg.create_pool(
    dsn="postgresql://user:pass@localhost:6432/myapp",
    min_size=5,
    max_size=20,
    max_inactive_connection_lifetime=300,
    command_timeout=30,
)

async with pool.acquire() as conn:
    rows = await conn.fetch("SELECT * FROM users WHERE active = true")
```

---

## Best Practices

1. **Use parameterized queries everywhere.** Never concatenate user input into SQL strings. ORMs and query builders handle this, but verify in raw SQL contexts.

2. **Run ANALYZE after bulk data changes.** The query planner relies on statistics. After large imports or deletes, run `ANALYZE tablename` to update them.

3. **Prefer BIGINT for primary keys.** INTEGER (max ~2.1 billion) can be exhausted sooner than expected in high-write systems. BIGINT costs 4 extra bytes per row but avoids a painful migration later.

4. **Store money as integers (cents).** Floating-point arithmetic causes rounding errors. Use `BIGINT` for cents or `NUMERIC(19,4)` if sub-cent precision is needed.

5. **Add indexes for foreign keys.** PostgreSQL does not automatically index the child side of a foreign key. Without it, DELETE on the parent table triggers a sequential scan on the child.

6. **Use TIMESTAMPTZ, not TIMESTAMP.** `TIMESTAMP WITHOUT TIME ZONE` silently drops timezone info. Always use `TIMESTAMPTZ` and let the application control display timezone.

7. **Set statement_timeout for web requests.** Prevent runaway queries from holding connections: `SET statement_timeout = '5s';` at session start, or configure per-role in PostgreSQL.

8. **Monitor with pg_stat_statements.** Enable this extension to track query performance over time. The top queries by `total_exec_time` are your optimization targets.

```sql
-- Find slowest queries
SELECT
    calls,
    round(total_exec_time::numeric, 1) AS total_ms,
    round(mean_exec_time::numeric, 1) AS mean_ms,
    query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

## Common Pitfalls

1. **N+1 queries from ORM lazy loading.** Loading a list of users and then accessing `user.orders` in a loop generates one query per user. Use eager loading (`joinedload` in SQLAlchemy, `select_related` in Django) or batch the query with a JOIN.

2. **Locking the table during migrations.** `ALTER TABLE ... ADD COLUMN NOT NULL DEFAULT 'x'` is safe in PG 11+, but `CREATE INDEX` without `CONCURRENTLY` locks writes. Always use `CREATE INDEX CONCURRENTLY` in production migrations.

3. **Bloated tables from UPDATE-heavy workloads.** PostgreSQL MVCC creates dead tuples on every UPDATE. If autovacuum cannot keep up, table size and query times grow. Monitor `pg_stat_user_tables.n_dead_tup` and tune autovacuum settings for hot tables.

4. **Using OFFSET for pagination on large datasets.** `OFFSET 100000` forces PG to scan and discard 100,000 rows. Use keyset pagination instead:

```sql
-- BAD: slow for deep pages
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 100000;

-- GOOD: keyset pagination
SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20;
```

5. **Ignoring connection limits.** Each PostgreSQL connection consumes RAM. Opening hundreds of direct connections (e.g., one per serverless function invocation) will exhaust `max_connections` and crash the server. Always use PgBouncer or an application-level pool.

6. **Storing large blobs in the database.** Files over a few KB should go in object storage (S3, R2). Store the URL/key in PostgreSQL. Large `bytea` or `TEXT` columns bloat the table, slow backups, and waste shared_buffers cache.

## Related Skills

- `databases/mongodb` - Document-based database patterns for non-relational data
- `patterns/caching` - Caching strategies to reduce database load
- `patterns/logging` - Logging patterns for query debugging and monitoring
