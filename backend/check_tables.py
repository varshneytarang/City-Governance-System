"""
Check Task Orchestration Tables

Quick script to check if task orchestration tables exist.
"""

import psycopg2
import os

# Direct config values (avoid circular imports)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "departments")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN (
            'workflows', 'tasks', 'task_dependencies',
            'contingency_plans', 'task_notifications', 'task_status_history',
            'task_blockers', 'workflow_approvals', 'knowledge_graph_nodes',
            'knowledge_graph_edges'
        )
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    
    print("=" * 60)
    print("TASK ORCHESTRATION TABLES STATUS")
    print("=" * 60)
    print()
    
    if tables:
        print(f"✓ Found {len(tables)}/10 tables:")
        for table in tables:
            print(f"  ✓ {table[0]}")
    else:
        print("❌ No task orchestration tables found")
    
    print()
    
    # Check if all required tables exist
    expected_tables = {
        'workflows', 'tasks', 'task_dependencies',
        'contingency_plans', 'task_notifications', 'task_status_history',
        'task_blockers', 'workflow_approvals', 'knowledge_graph_nodes',
        'knowledge_graph_edges'
    }
    
    found_tables = {t[0] for t in tables}
    missing_tables = expected_tables - found_tables
    
    if missing_tables:
        print(f"⚠️ Missing {len(missing_tables)} tables:")
        for table in sorted(missing_tables):
            print(f"  ❌ {table}")
    else:
        print("✅ All 10 required tables exist!")
    
    print()
    print("=" * 60)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
