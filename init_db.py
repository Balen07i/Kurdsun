"""
Creates all tables from the SQLAlchemy models.
Run once on a fresh database: `python -m scripts.init_db`

For real production use, migrate to Alembic migrations instead of this
script once the schema starts changing between deployments.
"""
import asyncio

from bot.core.db.models import Base
from bot.core.db.session import engine


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created.")


if __name__ == "__main__":
    asyncio.run(main())
