"""
Verify database setup and show sample data
"""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

async def verify_setup():
    """Verify database setup and display sample data"""
    
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/city_mas")
    
    # Parse connection string
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "")
    elif db_url.startswith("postgresql+psycopg2://"):
        db_url = db_url.replace("postgresql+psycopg2://", "")
    elif db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "")
    
    try:
        print("=" * 70)
        print("🎉 DATABASE SETUP VERIFICATION")
        print("=" * 70)
        
        conn = await asyncpg.connect(dsn=f"postgresql://{db_url}")
        
        # List all tables
        print("\n📊 ALL TABLES IN DATABASE:")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        for i, table in enumerate(tables, 1):
            print(f"   {i:2d}. {table['table_name']}")
        
        # Show Fire Stations
        print("\n🚒 FIRE STATIONS:")
        fire_stations = await conn.fetch("""
            SELECT name, location, zone, total_vehicles, available_vehicles, 
                   total_crew, available_crew, operational_status
            FROM fire_stations
            ORDER BY name
        """)
        
        for station in fire_stations:
            print(f"\n   📍 {station['name']}")
            print(f"      Location: {station['location']}, Zone: {station['zone']}")
            print(f"      Vehicles: {station['available_vehicles']}/{station['total_vehicles']}")
            print(f"      Crew: {station['available_crew']}/{station['total_crew']}")
            print(f"      Status: {station['operational_status']}")
        
        # Show Water Resources
        print("\n💧 WATER RESOURCES:")
        water_resources = await conn.fetch("""
            SELECT name, resource_type, location, capacity_liters, 
                   current_level_liters, level_percentage, operational_status
            FROM water_resources
            ORDER BY resource_type, name
        """)
        
        for resource in water_resources:
            print(f"\n   🚰 {resource['name']}")
            print(f"      Type: {resource['resource_type']}")
            print(f"      Location: {resource['location']}")
            if resource['capacity_liters']:
                print(f"      Capacity: {resource['capacity_liters']:,} liters")
                if resource['current_level_liters']:
                    print(f"      Current Level: {resource['current_level_liters']:,} liters ({resource['level_percentage']}%)")
            print(f"      Status: {resource['operational_status']}")
        
        # Show Water Infrastructure
        print("\n🔧 WATER INFRASTRUCTURE:")
        pipelines = await conn.fetch("""
            SELECT location, zone, pipeline_type, diameter_mm, material, 
                   condition, risk_level, operational_status
            FROM water_infrastructure
            ORDER BY zone, location
        """)
        
        for pipeline in pipelines:
            print(f"\n   🔹 {pipeline['location']}")
            print(f"      Zone: {pipeline['zone']}")
            print(f"      Type: {pipeline['pipeline_type']}, Diameter: {pipeline['diameter_mm']}mm, Material: {pipeline['material']}")
            print(f"      Condition: {pipeline['condition']}, Risk: {pipeline['risk_level']}")
            print(f"      Status: {pipeline['operational_status']}")
        
        # Check agent_messages table structure
        print("\n📨 AGENT MESSAGE SYSTEM:")
        message_count = await conn.fetchval("SELECT COUNT(*) FROM agent_messages")
        print(f"   Messages in queue: {message_count}")
        print("   ✅ Inter-agent communication system ready")
        
        await conn.close()
        
        print("\n" + "=" * 70)
        print("✅ DATABASE SETUP COMPLETE AND VERIFIED!")
        print("=" * 70)
        print("\n🚀 Next Steps:")
        print("   1. Build Water Agent LangGraph workflow")
        print("   2. Build Fire Agent LangGraph workflow")
        print("   3. Create API endpoints")
        print("   4. Test inter-agent communication")
        print("\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_setup())
