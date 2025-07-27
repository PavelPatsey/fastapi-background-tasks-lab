from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app import settings
from app.garage import GarageClient


def get_garage_client():
    return GarageClient()


GarageClientDepends = Annotated[GarageClient, Depends(get_garage_client)]


async def get_sql_engine() -> AsyncEngine:
    engine = create_async_engine(
        url=settings.DB_URL,
        connect_args=settings.CONNECT_ARGS,
    )
    return engine


EngineDepends = Annotated[AsyncEngine, Depends(get_sql_engine)]


async def get_session(engine: EngineDepends) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


SessionDepends = Annotated[AsyncSession, Depends(get_session)]
