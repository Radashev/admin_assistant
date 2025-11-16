import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


engine: AsyncEngine = create_async_engine(
    settings.postgres_url,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)


# ---------------------------
# TEST CONNECTION
# ---------------------------
async def test_connection() -> None:
    """Simple connectivity check: SELECT 1."""
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        print("DB RESULT:", result.scalar_one())


# ---------------------------
# SHOW TABLES
# ---------------------------
async def print_tables() -> None:
    from app.db import models  # noqa

    print("Tables:", Base.metadata.tables.keys())


if __name__ == "__main__":

    async def main():
        await test_connection()
        await print_tables()

    asyncio.run(main())
