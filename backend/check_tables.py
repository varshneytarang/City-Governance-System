import asyncio
from app.database import async_engine
from sqlalchemy import text

async def check():
    async with async_engine.begin() as conn:
        result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"))
        tables = [row[0] for row in result]
        print('Existing Tables:')
        for table in tables:
            print(f"  - {table}")

asyncio.run(check())
