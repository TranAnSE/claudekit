# PostgreSQL Index Decision Tree

Quick reference for choosing the right index type.

## Decision Tree

```
What are you querying?
|
+-- Equality (=) or Range (<, >, BETWEEN, ORDER BY)?
|   |
|   +-- On a single scalar column?
|   |   --> B-tree (default)
|   |
|   +-- On a timestamp/date column with append-only inserts?
|   |   --> BRIN (much smaller than B-tree)
|   |
|   +-- Need the index to also return columns without table lookup?
|       --> Covering Index (B-tree with INCLUDE)
|
+-- Array containment (@>, &&) or JSONB queries?
|   --> GIN
|
+-- Full-text search (tsvector, @@)?
|   --> GIN
|
+-- Geometric/spatial data (points, polygons, PostGIS)?
|   --> GiST
|
+-- Range types (int4range, tsrange, overlaps)?
|   --> GiST
|
+-- Nearest-neighbor / distance queries (KNN)?
|   --> GiST (or SP-GiST for partitioned space)
|
+-- Only a subset of rows match your WHERE clause?
|   --> Partial Index (any type + WHERE filter)
|
+-- Trigram similarity (LIKE '%pattern%', pg_trgm)?
|   --> GIN with pg_trgm  (or GiST for smaller, slower)
|
+-- Hash equality only (= but never range)?
    --> Hash index (rarely better than B-tree in practice)
```

## Index Type Comparison

| Type | Best For | Operators | Size | Write Cost | Notes |
|------|----------|-----------|------|------------|-------|
| **B-tree** | Equality, range, sorting | `=  <  >  <=  >=  BETWEEN  IN  IS NULL` | Medium | Low | Default. Covers 90% of cases. |
| **GIN** | Multi-valued data | `@>  &&  @@  ?  ?&  ?|` | Large | High (slow updates) | Best for arrays, JSONB, full-text. Use `fastupdate=on`. |
| **GiST** | Spatial, ranges, nearest-neighbor | `<<  >>  &&  @>  <@  <->` | Medium | Medium | Lossy for some types. Supports KNN. |
| **SP-GiST** | Partitioned search spaces | Same as GiST | Medium | Medium | Good for phone numbers, IP addresses, non-balanced trees. |
| **BRIN** | Large sequential/append-only tables | `=  <  >  <=  >=` | Tiny | Very Low | 1000x smaller than B-tree. Only effective when physical order correlates with column values. |
| **Hash** | Equality only | `=` | Medium | Low | WAL-logged since PG10. Rarely outperforms B-tree. |

## Common Patterns

### Covering Index (Index-Only Scans)

Avoid heap lookups by including extra columns:

```sql
-- Query: SELECT email, name FROM users WHERE email = ?
CREATE INDEX idx_users_email_covering
    ON users (email) INCLUDE (name);
```

### Partial Index (Filtered)

Index only the rows you actually query:

```sql
-- Only index active orders (skip 95% of rows)
CREATE INDEX idx_orders_active
    ON orders (created_at)
    WHERE status = 'active';
```

### Composite Index (Multi-Column)

Column order matters -- put equality columns first, range columns last:

```sql
-- Query: WHERE tenant_id = ? AND created_at > ?
CREATE INDEX idx_events_tenant_date
    ON events (tenant_id, created_at);
```

### Expression Index

Index a computed value:

```sql
CREATE INDEX idx_users_lower_email
    ON users (lower(email));
```

### GIN for JSONB

```sql
-- Index all keys and values in a JSONB column
CREATE INDEX idx_metadata_gin
    ON products USING gin (metadata jsonb_path_ops);

-- Supports: metadata @> '{"color": "red"}'
```

### GiST for Range Overlap

```sql
CREATE INDEX idx_reservations_during
    ON reservations USING gist (during);

-- Supports: WHERE during && '[2025-01-01, 2025-01-31]'::daterange
```

### BRIN for Time-Series

```sql
-- Table has millions of rows inserted in timestamp order
CREATE INDEX idx_logs_ts_brin
    ON logs USING brin (created_at)
    WITH (pages_per_range = 32);
```

## Sizing Rules of Thumb

| Table Rows | B-tree Size | BRIN Size | GIN Size |
|------------|-------------|-----------|----------|
| 1M | ~20 MB | ~50 KB | ~30 MB |
| 10M | ~200 MB | ~500 KB | ~300 MB |
| 100M | ~2 GB | ~5 MB | ~3 GB |

## Diagnostic Queries

```sql
-- Check if an index is being used
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;

-- Find unused indexes
SELECT indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Check index size
SELECT pg_size_pretty(pg_relation_size('idx_name'));

-- Index bloat estimate
SELECT * FROM pgstatindex('idx_name');
```

## Anti-Patterns

| Mistake | Why It Hurts |
|---------|-------------|
| Indexing every column | Slows writes, wastes disk, confuses planner |
| Wrong column order in composite | Index cannot be used for the query |
| GIN on tiny tables | Overhead exceeds benefit |
| B-tree on low-cardinality columns | Planner prefers seq scan anyway |
| Missing `CONCURRENTLY` on production | Locks the table during index build |
| Forgetting `ANALYZE` after bulk load | Planner uses stale statistics |

## Safe Index Creation

```sql
-- Non-blocking index creation (no table lock)
CREATE INDEX CONCURRENTLY idx_name ON table (column);

-- Always run ANALYZE after bulk operations
ANALYZE table;
```
