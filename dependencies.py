from typing import Annotated, Any, Generator

from fastapi import Depends
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

import settings
from garage import GarageClient


def get_garage_client():
    return GarageClient()


GarageClientDepends = Annotated[GarageClient, Depends(get_garage_client)]


def get_sql_engine() -> Engine:
    engine = create_engine(
        url=settings.SQLITE_URL,
        connect_args=settings.CONNECT_ARGS,
    )
    return engine


SQLEngineDepends = Annotated[Engine, Depends(get_sql_engine)]


def get_session(engine: SQLEngineDepends) -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session


SQLSessionDepends = Annotated[Session, Depends(get_session)]
