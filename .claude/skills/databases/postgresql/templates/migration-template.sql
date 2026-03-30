-- =============================================================================
-- Migration: [DESCRIPTION]
-- Created:   [DATE]
-- Author:    [AUTHOR]
-- Ticket:    [TICKET-ID]
-- =============================================================================
--
-- SAFETY CHECKLIST (review before running):
--   [ ] Tested on staging with production-size data
--   [ ] Backward compatible with current application code
--   [ ] No exclusive locks on large tables during peak hours
--   [ ] Rollback (DOWN) section tested independently
--   [ ] Estimated run time: ___
--   [ ] Estimated lock duration: ___
--

-- ============================================================
-- UP MIGRATION
-- ============================================================

BEGIN;

-- Set a statement timeout to prevent long-running locks.
-- Adjust as needed; remove for data-only migrations.
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '30s';

-- ------------------------------------
-- 1. Schema changes
-- ------------------------------------

-- Add new table
-- CREATE TABLE IF NOT EXISTS example (
--     id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
--     name        text NOT NULL,
--     created_at  timestamptz NOT NULL DEFAULT now(),
--     updated_at  timestamptz NOT NULL DEFAULT now()
-- );

-- Add column (safe: does not rewrite table)
-- ALTER TABLE example ADD COLUMN IF NOT EXISTS description text;

-- Add column with default (PG 11+: does not rewrite table)
-- ALTER TABLE example ADD COLUMN IF NOT EXISTS is_active boolean NOT NULL DEFAULT true;

-- Rename column (safe: metadata-only change)
-- ALTER TABLE example RENAME COLUMN old_name TO new_name;

-- ------------------------------------
-- 2. Constraints
-- ------------------------------------

-- Add NOT NULL (requires all existing rows to satisfy it)
-- ALTER TABLE example ALTER COLUMN name SET NOT NULL;

-- Add check constraint (NOT VALID avoids full table scan, then VALIDATE separately)
-- ALTER TABLE example ADD CONSTRAINT chk_example_name CHECK (name <> '') NOT VALID;
-- ALTER TABLE example VALIDATE CONSTRAINT chk_example_name;

-- Add foreign key (NOT VALID + VALIDATE pattern to avoid long locks)
-- ALTER TABLE example ADD CONSTRAINT fk_example_parent
--     FOREIGN KEY (parent_id) REFERENCES parent(id) NOT VALID;
-- ALTER TABLE example VALIDATE CONSTRAINT fk_example_parent;

-- ------------------------------------
-- 3. Indexes (use CONCURRENTLY outside transaction)
-- ------------------------------------

-- NOTE: CREATE INDEX CONCURRENTLY cannot run inside a transaction.
-- Run these statements separately after committing the transaction above.
--
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_example_name
--     ON example (name);
--
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_example_created_at
--     ON example USING brin (created_at);

-- ------------------------------------
-- 4. Data migration
-- ------------------------------------

-- Backfill in batches to avoid long transactions:
-- UPDATE example SET description = 'default' WHERE description IS NULL;
--
-- For large tables, batch with:
-- DO $$
-- DECLARE
--     batch_size int := 10000;
--     rows_updated int;
-- BEGIN
--     LOOP
--         UPDATE example
--         SET description = 'default'
--         WHERE id IN (
--             SELECT id FROM example
--             WHERE description IS NULL
--             LIMIT batch_size
--             FOR UPDATE SKIP LOCKED
--         );
--         GET DIAGNOSTICS rows_updated = ROW_COUNT;
--         EXIT WHEN rows_updated = 0;
--         RAISE NOTICE 'Updated % rows', rows_updated;
--         COMMIT;
--     END LOOP;
-- END $$;

-- ------------------------------------
-- 5. Permissions
-- ------------------------------------

-- GRANT SELECT, INSERT, UPDATE ON example TO app_role;
-- GRANT USAGE ON SEQUENCE example_id_seq TO app_role;

COMMIT;


-- ============================================================
-- DOWN MIGRATION (rollback)
-- ============================================================
-- Run this section to undo the UP migration.
-- Test this independently before deploying the UP migration.

-- BEGIN;
--
-- -- Reverse data migration
-- -- UPDATE example SET description = NULL;
--
-- -- Drop constraints
-- -- ALTER TABLE example DROP CONSTRAINT IF EXISTS chk_example_name;
-- -- ALTER TABLE example DROP CONSTRAINT IF EXISTS fk_example_parent;
--
-- -- Drop columns
-- -- ALTER TABLE example DROP COLUMN IF EXISTS description;
-- -- ALTER TABLE example DROP COLUMN IF EXISTS is_active;
--
-- -- Drop tables
-- -- DROP TABLE IF EXISTS example;
--
-- COMMIT;
--
-- -- Drop indexes (outside transaction)
-- -- DROP INDEX CONCURRENTLY IF EXISTS idx_example_name;
-- -- DROP INDEX CONCURRENTLY IF EXISTS idx_example_created_at;
