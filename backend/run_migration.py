"""
Run database migration to create Water & Fire agent tables
Execute this after updating your .env file with correct database credentials
"""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Read the migration SQL file
migration_file = "migrations/001_water_fire_agents.sql"

async def run_migration():
    """Execute the migration SQL file"""
    print("🔄 Starting database migration...")
    
    # Get database URL from environment
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/city_mas")
    
    # Parse connection string
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "")
    elif db_url.startswith("postgresql+psycopg2://"):
        db_url = db_url.replace("postgresql+psycopg2://", "")
    elif db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "")
    
    try:
        # Read migration file
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print(f"📄 Read migration file: {migration_file}")
        print(f"🔌 Connecting to database...")
        
        # Connect to database
        conn = await asyncpg.connect(dsn=f"postgresql://{db_url}")
        
        print("✅ Connected to database")
        print("⚙️ Executing migration...")
        
        # Execute the SQL
        await conn.execute(sql_content)
        
        print("✅ Migration completed successfully!")
        
        # Verify tables were created
        print("\n📊 Verifying created tables...")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN (
                'water_infrastructure', 
                'water_incidents', 
                'water_resources',
                'fire_stations',
                'emergency_incidents',
                'agent_messages'
            )
            ORDER BY table_name
        """)
        
        print(f"\n✅ Found {len(tables)} new tables:")
        for table in tables:
            print(f"   ✓ {table['table_name']}")
        
        # Count sample data
        print("\n📈 Sample data counts:")
        fire_stations_count = await conn.fetchval("SELECT COUNT(*) FROM fire_stations")
        water_resources_count = await conn.fetchval("SELECT COUNT(*) FROM water_resources")
        water_infra_count = await conn.fetchval("SELECT COUNT(*) FROM water_infrastructure")
        
        print(f"   • Fire stations: {fire_stations_count}")
        print(f"   • Water resources: {water_resources_count}")
        print(f"   • Water infrastructure: {water_infra_count}")
        
        # Close connection
        await conn.close()
        print("\n🎉 Migration successful! Database is ready for Water & Fire agents.")
        
    except FileNotFoundError:
        print(f"❌ Error: Migration file not found: {migration_file}")
        print("   Make sure you're running this from the backend directory")
    except asyncpg.exceptions.PostgresError as e:
        print(f"❌ Database error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your DATABASE_URL in .env file")
        print("   2. Ensure PostgreSQL is running")
        print("   3. Verify the 'city_mas' database exists")
        print("   4. Check username and password are correct")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(run_migration())
