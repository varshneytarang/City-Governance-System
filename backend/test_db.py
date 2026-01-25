"""
Test database connection
Run this to verify your .env DATABASE_URL is correct
"""
import asyncio
from app.database import check_db_connection, get_db_info


async def main():
    print("=" * 60)
    print("🧪 Testing Database Connection")
    print("=" * 60)
    
    # Show connection info
    print("\n📋 Database Configuration:")
    info = get_db_info()
    for key, value in info.items():
        print(f"   • {key}: {value}")
    
    # Test connection
    print("\n🔌 Testing connection...")
    is_connected = await check_db_connection()
    
    if is_connected:
        print("\n✅ SUCCESS! Database connected successfully!")
        print("\n🎉 Your setup is working correctly.")
        print("   You can now run: python run_migration.py")
    else:
        print("\n❌ FAILED! Could not connect to database.")
        print("\n💡 Troubleshooting:")
        print("   1. Check DATABASE_URL in .env file")
        print("   2. Ensure PostgreSQL is running")
        print("   3. Verify 'city_mas' database exists")
        print("   4. Check username and password")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
