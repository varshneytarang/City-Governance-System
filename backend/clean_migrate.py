"""
Clean and Re-run Task Orchestration Migration

This script drops any partial task orchestration tables and re-runs the migration cleanly.
"""

import psycopg2
import os
from pathlib import Path

# Direct config values
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "departments")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def cleanup_and_migrate():
    """Drop any existing task orchestration objects and re-run migration"""
    
    try:
        print("=" * 60)
        print("TASK ORCHESTRATION - CLEAN MIGRATION")
        print("=" * 60)
        print()
        
        # Connect to database
        print(f"🔌 Connecting to database: {DB_NAME} at {DB_HOST}:{DB_PORT}")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✓ Connected to database\n")
        
        # Step 1: Drop existing task orchestration tables (in rev Dependency order)
        print("🧹 Cleaning up existing tables...")
        
        tables_to_drop = [
            'workflow_notifications',
            'workflow_tags',
            'task_assignments',
            'task_execution_logs',
            'task_executions',
            'workflow_executions',
            'contingency_plans',
            'task_dependencies',
            'workflow_tasks',
            'task_workflows'
        ]
        
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                print(f"  ✓ Dropped {table}")
            except Exception as e:
                print(f"  ⚠️  {table}: {e}")
        
        # Drop views
        cursor.execute("DROP VIEW IF EXISTS active_workflows_view CASCADE")
        cursor.execute("DROP VIEW IF EXISTS overdue_tasks_view CASCADE")
        print("  ✓ Dropped views")
        
        # Drop existing indexes
        print("  🧹 Dropping indexes...")
        cursor.execute("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT indexname FROM pg_indexes 
                          WHERE indexname LIKE 'idx_%' 
                          AND schemaname = 'public') LOOP
                    EXECUTE 'DROP INDEX IF EXISTS ' || quote_ident(r.indexname) || ' CASCADE';
                END LOOP;
            END $$;
        """)
        print("  ✓ Dropped all indexes")
        
        # Drop existing triggers
        print("  🧹 Dropping triggers...")
        cursor.execute("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tgname, relname FROM pg_trigger t
                          JOIN pg_class c ON t.tgrelid = c.oid
                          WHERE tgname LIKE 'update_%_updated_at'
                          AND c.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) LOOP
                    EXECUTE 'DROP TRIGGER IF EXISTS ' || quote_ident(r.tgname) || ' ON ' || quote_ident(r.relname) || ' CASCADE';
                END LOOP;
            END $$;
        """)
        print("  ✓ Dropped all triggers")
        
        # Drop functions
        print("  🧹 Dropping functions...")
        cursor.execute("DROP FUNCTION IF EXISTS update_updated_at_column CASCADE")
        cursor.execute("DROP FUNCTION IF EXISTS check_task_dependencies CASCADE")
        cursor.execute("DROP FUNCTION IF EXISTS update_workflow_progress CASCADE")
        print("  ✓ Dropped all functions\n")
        
        # Step 2: Read and execute migration
        migration_file = Path(__file__).parent.parent / "migrations" / "task_orchestration_schema.sql"
        
        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            return False
        
        print(f"📄 Reading migration from: {migration_file}")
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print("🚀 Running migration...\n")
        cursor.execute(migration_sql)
        
        print("✅ Migration completed successfully!\n")
        
        # Step 3: Verify tables created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN (
                'task_workflows', 'workflow_tasks', 'task_dependencies',
                'workflow_executions', 'task_executions', 'task_execution_logs',
                'task_assignments', 'workflow_tags', 'workflow_notifications',
                'contingency_plans'
            )
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"📊 Created {len(tables)}/10 tables:")
        for table in tables:
            print(f"  ✓ {table[0]}")
        
        # Check views
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'VIEW'
            AND table_name IN ('active_workflows_view', 'overdue_tasks_view')
            ORDER BY table_name;
        """)
        
        views = cursor.fetchall()
        if views:
            print(f"\n📊 Created {len(views)}/2 views:")
            for view in views:
                print(f"  ✓ {view[0]}")
        
        print()
        print("=" * 60)
        print("✅ MIGRATION SUCCESSFUL")
        print("=" * 60)
        print("\n✨ You can now create workflows and tasks!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection error: {e}")
        print(f"\n💡 Please ensure PostgreSQL is running and credentials are correct:")
        print(f"   Host: {DB_HOST}")
        print(f"   Port: {DB_PORT}")
        print(f"   Database: {DB_NAME}")
        print(f"   User: {DB_USER}")
        return False
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    
    success = cleanup_and_migrate()
    sys.exit(0 if success else 1)
