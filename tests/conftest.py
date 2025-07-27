from typing import Any, AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.dependencies import get_garage_client, get_session
from app.garage import GarageClient
from app.main import app
from app.models import Base


class FakeGarageClient(GarageClient):
    UPDATE_STATUS_PROBABILITY = 100
    SLEEP_DURATION = 0


@pytest_asyncio.fixture(name="async_session")
async def session_fixture() -> AsyncGenerator[AsyncSession, Any]:
    engine = create_async_engine("sqlite+aiosqlite:///tests/fake_database.db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(name="async_client")
async def client_fixture(async_session: AsyncSession):
    def get_session_override():
        return async_session

    def get_garage_client_override():
        return FakeGarageClient()

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_garage_client] = get_garage_client_override
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
    app.dependency_overrides.clear()
