"""add_automatic_timestamp_triggers

Revision ID: 7ce9179e5a3b
Revises: 74de74a58414
Create Date: 2026-08-26 17:23:10.457170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ce9179e5a3b'
down_revision: Union[str, Sequence[str], None] = '74de74a58414'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- TASK 1: The Function (Separate call) ---
    op.execute("""
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # --- TASK 2: The Existing Tables (Separate call) ---
    op.execute("""
    DO $$
    DECLARE
        r RECORD;
    BEGIN
        FOR r IN 
            SELECT table_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
              AND column_name = 'updated_at'
        LOOP
            EXECUTE format('DROP TRIGGER IF EXISTS trg_set_updated_at ON %I', r.table_name);
            EXECUTE format('
                CREATE TRIGGER trg_set_updated_at
                BEFORE UPDATE ON %I
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
            ', r.table_name);
        END LOOP;
    END $$;
    """)

    # --- TASK 3 part A: The Event Trigger Function ---
    op.execute("""
    CREATE OR REPLACE FUNCTION auto_add_updated_at_trigger()
    RETURNS event_trigger AS $$
    DECLARE
        obj record;
        v_has_column boolean;
    BEGIN
        FOR obj IN SELECT * FROM pg_event_trigger_ddl_commands() WHERE command_tag = 'CREATE TABLE'
        LOOP
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'public' 
                  AND table_name = split_part(obj.object_identity, '.', 2)
                  AND column_name = 'updated_at'
            ) INTO v_has_column;

            IF v_has_column THEN
                EXECUTE format('
                    CREATE TRIGGER trg_set_updated_at
                    BEFORE UPDATE ON %s
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();
                ', obj.object_identity);
            END IF;
        END LOOP;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # --- TASK 3 part B: The actual Event Trigger (Separate call) ---
    op.execute("""
    CREATE EVENT TRIGGER tg_auto_add_updated_at
    ON ddl_command_end
    WHEN tag IN ('CREATE TABLE')
    EXECUTE FUNCTION auto_add_updated_at_trigger();
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
