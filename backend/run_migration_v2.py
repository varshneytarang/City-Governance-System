"""
Database Migration Runner - Professional Agent Architecture
Runs all SQL migration files in order
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost/city_mas")

# Parse connection string
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DB_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
else:
    DB_URL = DATABASE_URL


async def run_migration(conn, migration_file: Path):
    """Run a single migration file"""
    print(f"\n{'='*70}")
    print(f"Running migration: {migration_file.name}")
    print(f"{'='*70}")
    
    try:
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        await conn.execute(sql)
        print(f"✅ Migration {migration_file.name} completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error running migration {migration_file.name}:")
        print(f"   {str(e)}")
        return False


async def check_extension(conn):
    """Check and enable uuid-ossp extension"""
    print("\n" + "="*70)
    print("Checking PostgreSQL Extensions")
    print("="*70)
    
    try:
        # Check if extension exists
        result = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'uuid-ossp')"
        )
        
        if result:
            print("✅ uuid-ossp extension already enabled")
        else:
            print("⚙️  Enabling uuid-ossp extension...")
            await conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
            print("✅ uuid-ossp extension enabled")
            
    except Exception as e:
        print(f"❌ Error checking/enabling extension: {e}")


async def get_migration_status(conn):
    """Get list of applied migrations from tracking table"""
    try:
        # Create migrations tracking table if not exists
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                migration_name VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Get applied migrations
        rows = await conn.fetch("SELECT migration_name FROM schema_migrations")
        return {row['migration_name'] for row in rows}
        
    except Exception as e:
        print(f"⚠️  Warning: Could not check migration status: {e}")
        return set()


async def record_migration(conn, migration_name: str):
    """Record that a migration has been applied"""
    try:
        await conn.execute(
            "INSERT INTO schema_migrations (migration_name) VALUES ($1) ON CONFLICT (migration_name) DO NOTHING",
            migration_name
        )
    except Exception as e:
        print(f"⚠️  Warning: Could not record migration: {e}")


async def run_all_migrations():
    """Run all migrations in order"""
    print("\n" + "="*70)
    print("🗄️  DATABASE MIGRATION - Professional Agent Architecture")
    print("="*70)
    
    # Get migration files
    migrations_dir = Path(__file__).parent / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    if not migration_files:
        print("⚠️  No migration files found!")
        return
    
    print(f"\nFound {len(migration_files)} migration file(s):")
    for mf in migration_files:
        print(f"  - {mf.name}")
    
    # Connect to database
    try:
        print(f"\n{'='*70}")
        print(f"Connecting to database...")
        print(f"{'='*70}")
        
        conn = await asyncpg.connect(DB_URL)
        print("✅ Database connection established")
        
        # Check extensions
        await check_extension(conn)
        
        # Get migration status
        applied_migrations = await get_migration_status(conn)
        
        # Run migrations
        success_count = 0
        skip_count = 0
        fail_count = 0
        
        for migration_file in migration_files:
            migration_name = migration_file.name
            
            if migration_name in applied_migrations:
                print(f"\n⏭️  Skipping {migration_name} (already applied)")
                skip_count += 1
                continue
            
            success = await run_migration(conn, migration_file)
            
            if success:
                await record_migration(conn, migration_name)
                success_count += 1
            else:
                fail_count += 1
                # Stop on first failure
                break
        
        # Summary
        print("\n" + "="*70)
        print("📊 MIGRATION SUMMARY")
        print("="*70)
        print(f"✅ Successfully applied: {success_count}")
        print(f"⏭️  Skipped (already applied): {skip_count}")
        print(f"❌ Failed: {fail_count}")
        print("="*70)
        
        if fail_count == 0:
            print("\n🎉 All migrations completed successfully!")
        else:
            print("\n⚠️  Some migrations failed. Please check the errors above.")
        
        # Close connection
        await conn.close()
        print("\n✅ Database connection closed")
        
    except Exception as e:
        print(f"\n❌ Database connection error:")
        print(f"   {str(e)}")
        print(f"\n💡 Troubleshooting:")
        print(f"   1. Check if PostgreSQL is running")
        print(f"   2. Verify DATABASE_URL in .env file")
        print(f"   3. Ensure database 'city_mas' exists")
        print(f"   4. Check username/password credentials")


async def verify_tables():
    """Verify that all tables were created"""
    print("\n" + "="*70)
    print("🔍 VERIFYING TABLE CREATION")
    print("="*70)
    
    try:
        conn = await asyncpg.connect(DB_URL)
        
        expected_tables = [
            # Professional architecture tables
            'agent_decisions',
            'department_budgets',
            'projects',
            'work_schedules',
            'workers',
            'pipelines',
            'reservoirs',
            'incidents',
            # Original water/fire tables
            'water_infrastructure',
            'water_incidents',
            'water_resources',
            'fire_stations',
            'emergency_incidents',
            'agent_messages',
        ]
        
        for table in expected_tables:
            exists = await conn.fetchval(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                table
            )
            
            if exists:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                print(f"✅ {table:30s} (rows: {count})")
            else:
                print(f"❌ {table:30s} NOT FOUND")
        
        await conn.close()
        print("\n✅ Verification complete")
        
    except Exception as e:
        print(f"❌ Verification error: {e}")


if __name__ == "__main__":
    print("\n🚀 Starting database migration...\n")
    asyncio.run(run_all_migrations())
    asyncio.run(verify_tables())
    print("\n✨ Migration process complete!\n")
