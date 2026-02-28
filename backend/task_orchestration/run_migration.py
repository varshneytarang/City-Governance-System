"""
Run Task Orchestration Database Migration

This script creates the task orchestration tables in PostgreSQL.
Run this once before using the task orchestration features.
"""

import psycopg2
import sys
from pathlib import Path
from config import task_config

def run_migration():
    """Run the task orchestration schema migration"""
    
    # Read the migration SQL file
    migration_file = Path(__file__).parent.parent.parent / "migrations" / "task_orchestration_schema.sql"
    
    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False
    
    print(f"📄 Reading migration from: {migration_file}")
    with open(migration_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    # Connect to database
    try:
        print(f"🔌 Connecting to database: {task_config.DB_NAME} at {task_config.DB_HOST}:{task_config.DB_PORT}")
        conn = psycopg2.connect(
            host=task_config.DB_HOST,
            port=task_config.DB_PORT,
            database=task_config.DB_NAME,
            user=task_config.DB_USER,
            password=task_config.DB_PASSWORD
        )
        
        print("✓ Connected to database")
        
        # Execute migration
        cursor = conn.cursor()
        print("🚀 Running migration...")
        
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✅ Migration completed successfully!")
        
        # Verify tables created
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
        print(f"\n📊 Created {len(tables)} tables:")
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
            print(f"\n📊 Created {len(views)} views:")
            for view in views:
                print(f"  ✓ {view[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection error: {e}")
        print(f"\n💡 Please ensure PostgreSQL is running and credentials are correct:")
        print(f"   Host: {task_config.DB_HOST}")
        print(f"   Port: {task_config.DB_PORT}")
        print(f"   Database: {task_config.DB_NAME}")
        print(f"   User: {task_config.DB_USER}")
        return False
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("TASK ORCHESTRATION - DATABASE MIGRATION")
    print("=" * 60)
    print()
    
    success = run_migration()
    
    print()
    print("=" * 60)
    
    if success:
        print("✅ MIGRATION SUCCESSFUL")
        print("\nYou can now use the task orchestration features!")
        sys.exit(0)
    else:
        print("❌ MIGRATION FAILED")
        print("\nPlease check the error messages above and try again.")
        sys.exit(1)
