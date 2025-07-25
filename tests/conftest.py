import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.dependencies import get_garage_client, get_session
from app.garage import GarageClient
from app.main import app
from app.models import Base


class FakeGarageClient(GarageClient):
    UPDATE_STATUS_PROBABILITY = 100
    SLEEP_DURATION = 0


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///tests/fake_database.db")
    Base.metadata.create_all(bind=engine)
    session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with session_maker() as session:
        yield session
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    def get_garage_client_override():
        return FakeGarageClient()

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_garage_client] = get_garage_client_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
