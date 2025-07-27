from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import settings


def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def init_db_state(app: FastAPI) -> None:
    async_engine = create_async_engine(
        url=settings.DB_URL,
        connect_args=settings.CONNECT_ARGS,
    )
    app.state.engine = async_engine
    session_maker = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=True,
    )

    app.state.session_maker = session_maker


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_state(app)
    yield
