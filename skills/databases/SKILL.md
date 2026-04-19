---
name: databases
description: >
  Use when working with PostgreSQL, MongoDB, or Redis — including schema design, queries, indexing, migrations, connection pooling, caching layers, or any database operation. Also activate for keywords like SQL, aggregation pipeline, BSON, ioredis, alembic, prisma migrate, django migrate, EXPLAIN ANALYZE, ORM configuration, or NoSQL data modeling.
---

# Databases

## When to Use

- PostgreSQL database operations, SQL query optimization, schema design
- JSONB document storage, full-text search, window functions, CTEs
- MongoDB document modeling, aggregation pipelines, semi-structured data
- Redis caching, session storage, rate limiting, pub/sub, job queues, distributed locks
- Database migrations — adding/modifying tables, columns, indexes, constraints
- Resolving migration conflicts, rolling back failed migrations

## When NOT to Use

- Simple key-value caching within a single process — use `functools.lru_cache` or `Map`
- File-based storage that doesn't need a database engine
- Static data or configuration that belongs in environment variables

---

## Quick Reference

| Topic | Reference | Key tools |
|-------|-----------|-----------|
| PostgreSQL | `references/postgresql.md` | SQL, SQLAlchemy, Prisma, EXPLAIN ANALYZE, pg_stat_statements |
| MongoDB | `references/mongodb.md` | Aggregation, Mongoose, Motor, document schemas, ESR indexing |
| Redis | `references/redis.md` | Caching, pub/sub, ioredis, BullMQ, session storage, distributed locks |
| Migrations | `references/migrations.md` | Alembic, Prisma Migrate, Django migrations, rollback strategies |

---

## Best Practices

1. **Use parameterized queries everywhere.** Never concatenate user input into SQL strings.
2. **Design schema around access patterns.** Ask "how will I read this?" before "how does this relate?" Embed data fetched together (MongoDB); normalize data accessed independently (PostgreSQL).
3. **Index foreign keys and query fields.** PostgreSQL doesn't auto-index FK child columns. MongoDB queries without indexes trigger full collection scans.
4. **Use appropriate consistency levels.** `TIMESTAMPTZ` over `TIMESTAMP` (PostgreSQL). `w: "majority"` for durable writes (MongoDB). TTLs on every Redis cache key.
5. **Monitor query performance.** `pg_stat_statements` (PostgreSQL), `db.setProfilingLevel(1)` (MongoDB), connection pool metrics (all).
6. **Use bulk/batch operations.** `bulkWrite` (MongoDB), `COPY` (PostgreSQL), pipelines (Redis) for high-throughput writes.
7. **Never edit deployed migrations.** Create a new migration instead of modifying one already applied.
8. **Test rollback paths.** Always verify your downgrade/rollback strategy before deploying schema changes.

## Common Pitfalls

1. **N+1 queries from ORM lazy loading.** Use eager loading (`joinedload`, `select_related`, `$lookup` with caution).
2. **Table locks during migrations.** Use `CREATE INDEX CONCURRENTLY` (PostgreSQL). Batch backfills for large tables.
3. **Unbounded growth.** Dead tuples from UPDATE-heavy workloads (PostgreSQL). Arrays exceeding 16MB document limit (MongoDB). Redis keys without TTLs.
4. **OFFSET pagination on large datasets.** Use keyset/cursor pagination instead.
5. **Connection exhaustion.** Use connection pools (PgBouncer, application-level pools). Never open per-request connections.
6. **Cache stampede.** When a popular Redis key expires, many requests hit the DB simultaneously. Use distributed locks or stale-while-revalidate.
7. **Running `migrate reset` in production.** This drops all data.

---

## Related Skills

- `backend-frameworks` — Framework-specific ORM integration
- `error-handling` — Database error handling patterns
- `logging` — Query logging and slow query detection
