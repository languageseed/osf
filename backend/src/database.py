"""
OSF Demo - Database Connection
Supports both SQLite (demo) and PostgreSQL (production)
"""

import os
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
import structlog

from src.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


def get_database_url() -> str:
    """Get database URL, using SQLite for demo if PostgreSQL not available."""
    database_url = settings.database_url
    
    # Check if we should use SQLite (simpler for hackathon demo)
    use_sqlite = os.getenv("USE_SQLITE", "true").lower() == "true"
    
    if use_sqlite or "postgresql" not in database_url:
        # Use SQLite for demo
        db_path = Path("data/osf_demo.db")
        db_path.parent.mkdir(exist_ok=True)
        sqlite_url = f"sqlite+aiosqlite:///{db_path}"
        logger.info("database_using_sqlite", path=str(db_path))
        return sqlite_url
    
    # Convert postgres:// to postgresql+asyncpg://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    logger.info("database_using_postgresql")
    return database_url


# Get appropriate database URL
database_url = get_database_url()
is_sqlite = "sqlite" in database_url

# Create async engine with appropriate settings
if is_sqlite:
    engine = create_async_engine(
        database_url,
        echo=settings.is_development,
        connect_args={"check_same_thread": False},  # SQLite specific
    )
else:
    engine = create_async_engine(
        database_url,
        echo=settings.is_development,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    """Base class for all models."""
    metadata = metadata


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database - create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database_initialized")


async def close_db():
    """Close database connections."""
    await engine.dispose()
    logger.info("database_closed")
