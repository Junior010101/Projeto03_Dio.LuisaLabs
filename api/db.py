from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from api.config import settings


class BaseModel(DeclarativeBase):
    __abstract__ = True


if settings.environment == "production":
    engine = create_async_engine(
        settings.database_url,
        echo=True,
    )
else:
    engine = create_async_engine(
        settings.database_url,
        connect_args={"check_same_thread": True},
        echo=True,
    )

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator:
    async with async_session() as session:
        yield session
