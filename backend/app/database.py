"""
Database connection and session management
Supports both sync and async connections to PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager, asynccontextmanager
from typing import AsyncGenerator, Generator

from app.config import get_settings
from app.models import Base

settings = get_settings()


# ============= SYNCHRONOUS DATABASE =============

# Create sync engine for migrations and admin tasks
sync_engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Sync session factory
SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)


@contextmanager
def get_sync_db() -> Generator[Session, None, None]:
    """
    Synchronous database session context manager
    Use for migrations, CLI scripts, and synchronous operations
    """
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize database tables (for development)
    In production, use Alembic migrations
    """
    Base.metadata.create_all(bind=sync_engine)
    print("✅ Database tables created successfully")


# ============= ASYNCHRONOUS DATABASE =============

# Create async engine for FastAPI endpoints
async_engine = create_async_engine(
    settings.async_database_url,
    echo=settings.debug,
    pool_pre_ping=True
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous database session dependency
    Use with FastAPI dependency injection
    
    Example:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_async_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session context manager
    Use for background tasks or non-FastAPI async operations
    
    Example:
        async with get_async_db_context() as db:
            result = await db.execute(select(User))
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_async_db():
    """
    Initialize database tables asynchronously (for development)
    In production, use Alembic migrations
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Async database tables created successfully")


async def close_db():
    """
    Close database connections
    Call during application shutdown
    """
    await async_engine.dispose()
    print("✅ Database connections closed")


# ============= UTILITY FUNCTIONS =============

async def check_db_connection() -> bool:
    """
    Check if database connection is healthy
    Returns True if connection successful, False otherwise
    """
    try:
        from sqlalchemy import text
        async with get_async_db_context() as db:
            await db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def get_db_info() -> dict:
    """
    Get database connection information
    Useful for debugging and health checks
    """
    return {
        "database_url": settings.database_url.split("@")[-1] if "@" in settings.database_url else "local",
        "async_url": settings.async_database_url.split("@")[-1] if "@" in settings.async_database_url else "local",
        "pool_size": 10,
        "max_overflow": 20,
        "echo": settings.debug
    }
