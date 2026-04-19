# Databases — Migration Patterns


# Database Migrations

## When to Use

- Adding or modifying database tables/columns
- Creating indexes or constraints
- Running migrations in development, staging, or production
- Resolving migration conflicts in a team
- Rolling back a failed migration

## When NOT to Use

- Query optimization without schema changes — use `postgresql` skill
- Initial database design from scratch — use `postgresql` or `mongodb` skill
- ORM configuration without migrations — use framework-specific skill

---

## Quick Reference

| I need... | Go to |
|-----------|-------|
| Alembic (FastAPI/SQLAlchemy) | SS Alembic below |
| Prisma (NestJS/Express) | SS Prisma below |
| Django migrations | SS Django below |
| Safe production patterns | SS Production Safety below |
| Rollback strategies | SS Rollbacks below |

---

## Alembic (Python / SQLAlchemy)

### Setup

```bash
pip install alembic
alembic init migrations
```

```python
# migrations/env.py — configure target metadata
from src.models import Base
target_metadata = Base.metadata
```

### Create a migration

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "add orders table"

# Manual migration (for data migrations or complex changes)
alembic revision -m "backfill order status"
```

### Migration file

```python
# migrations/versions/003_add_orders_table.py
"""add orders table"""

from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'

def upgrade() -> None:
    op.create_table(
        'orders',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('total', sa.Numeric(10, 2), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_orders_user_id', 'orders', ['user_id'])
    op.create_index('ix_orders_created_at', 'orders', ['created_at'])

def downgrade() -> None:
    op.drop_table('orders')
```

### Run migrations

```bash
# Apply all pending
alembic upgrade head

# Apply one step
alembic upgrade +1

# Check current state
alembic current

# Check for pending migrations
alembic check

# View migration history
alembic history --verbose
```

---

## Prisma (TypeScript / NestJS / Express)

### Create a migration

```bash
# Generate migration from schema changes
npx prisma migrate dev --name add_orders_table

# Apply in production (no interactive prompts)
npx prisma migrate deploy

# Check status
npx prisma migrate status
```

### Schema change

```prisma
// prisma/schema.prisma
model Order {
  id        String   @id @default(uuid())
  userId    String
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  total     Decimal  @db.Decimal(10, 2)
  status    String   @default("pending")
  createdAt DateTime @default(now())

  @@index([userId])
  @@index([createdAt])
}
```

### Generated migration SQL

```sql
-- prisma/migrations/20260417_add_orders_table/migration.sql
CREATE TABLE "Order" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "userId" TEXT NOT NULL,
    "total" DECIMAL(10,2) NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "Order_pkey" PRIMARY KEY ("id")
);

CREATE INDEX "Order_userId_idx" ON "Order"("userId");
CREATE INDEX "Order_createdAt_idx" ON "Order"("createdAt");

ALTER TABLE "Order" ADD CONSTRAINT "Order_userId_fkey"
  FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE;
```

---

## Django

### Create and apply

```bash
# Auto-generate from model changes
python manage.py makemigrations app_name

# Apply
python manage.py migrate

# Check for pending
python manage.py showmigrations

# SQL preview (don't execute)
python manage.py sqlmigrate app_name 0003
```

### Data migration

```python
# app/migrations/0004_backfill_order_status.py
from django.db import migrations

def backfill_status(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    Order.objects.filter(status='').update(status='pending')

class Migration(migrations.Migration):
    dependencies = [('orders', '0003_add_orders')]
    operations = [migrations.RunPython(backfill_status, migrations.RunPython.noop)]
```

---

## Production Safety

### Golden rules

1. **Never drop columns in the same deploy as removing code references.** Remove code first, deploy, then drop column in next migration.
2. **Add columns as nullable or with defaults.** `NOT NULL` without a default locks the table during backfill on large tables.
3. **Create indexes concurrently** (PostgreSQL):
   ```sql
   CREATE INDEX CONCURRENTLY ix_orders_status ON orders(status);
   ```
4. **Test migrations against a production-size dataset** before deploying.
5. **Always have a rollback plan** — either a `downgrade()` function or a manual SQL script.

### Safe column addition pattern

```python
# Step 1: Add nullable column (fast, no lock)
op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))

# Step 2: Backfill in batches (separate migration or script)
# Don't do UPDATE users SET phone = '...' on millions of rows at once

# Step 3: Add NOT NULL constraint (after backfill confirms all rows filled)
op.alter_column('users', 'phone', nullable=False)
```

### Safe column rename pattern

```
Deploy 1: Add new column, write to both old and new
Deploy 2: Backfill new column from old, read from new
Deploy 3: Stop writing to old column
Deploy 4: Drop old column
```

---

## Rollbacks

### Alembic

```bash
# Rollback one step
alembic downgrade -1

# Rollback to specific revision
alembic downgrade 002

# Rollback to base (dangerous — drops everything)
alembic downgrade base
```

### Prisma

Prisma doesn't have built-in rollback. Options:
- Apply a new migration that reverses the change
- Manually run SQL: `npx prisma db execute --file rollback.sql`
- Restore from database backup

### Django

```bash
# Rollback to specific migration
python manage.py migrate app_name 0002
```

---

## Team Workflow

### Resolving migration conflicts

When two developers create migrations from the same parent:

**Alembic:**
```bash
# Developer A and B both branched from revision 002
# Alembic detects multiple heads
alembic heads          # shows 003a and 003b
alembic merge -m "merge migrations" 003a 003b
alembic upgrade head
```

**Prisma:**
```bash
# Reset and re-apply (dev only)
npx prisma migrate reset
# Or resolve manually by editing the migration SQL
```

**Django:**
```bash
# Django auto-detects and asks to merge
python manage.py makemigrations --merge
```

---

## Common Pitfalls

1. **Running `migrate reset` in production.** This drops all data. Only use in development.
2. **Editing already-applied migrations.** Never modify a migration that's been deployed. Create a new migration instead.
3. **Forgetting indexes.** Add indexes for foreign keys and frequently-queried columns in the same migration.
4. **Large table locks.** `ALTER TABLE` with `NOT NULL` or `ADD COLUMN DEFAULT` can lock large tables. Use batched backfills.
5. **Not testing downgrade.** Always test your rollback path before deploying.
6. **Circular foreign keys.** Use `sa.ForeignKey` with `use_alter=True` in Alembic to handle circular deps.

---

## Related Skills

- `postgresql` — Database design, query optimization, indexing strategies
- `fastapi` — SQLAlchemy async patterns with FastAPI
- `nestjs` — Prisma integration with NestJS
- `django` — Django ORM models and migrations
- `docker` — Running migration containers in CI/CD
