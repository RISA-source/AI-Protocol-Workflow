"""
Database configuration and session management
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Convert sync database URL to async
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Create async engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """
    Initialize database - create tables if they don't exist
    """
    try:
        async with engine.begin() as conn:
            # Import all models to ensure they're registered
            from app.models import artifacts, agents, workflows
            
            # Create tables that don't exist yet
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database tables created successfully (or already exist)")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

async def close_db():
    """
    Close database connections
    """
    await engine.dispose()


# Optional: auto-initialize when running this file directly
if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
