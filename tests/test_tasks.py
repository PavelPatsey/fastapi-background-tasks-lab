from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, schemas
from app.schemas import TaskStatuses


def test_read_tasks(client: TestClient, session: Session):
    task_1 = models.Task(
        name="test task 1",
        car_id="car_1",
        status=TaskStatuses.in_progress,
    )
    task_2 = models.Task(
        name="test task 2",
        car_id="car_2",
        status=TaskStatuses.in_progress,
    )
    session.add(task_1)
    session.add(task_2)
    session.commit()

    response = client.get("/tasks")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["tasks"]) == 2
    assert data["tasks"][0]["name"] == "test task 2"
    assert data["tasks"][1]["name"] == "test task 1"


def test_read_task_by_id(client: TestClient, session: Session):
    task_in = schemas.TaskCreate(
        name="test task 1",
        car_id="car_1",
        status=TaskStatuses.in_progress,
    )
    task = models.Task(**task_in.model_dump())
    session.add(task)
    session.commit()

    response = client.get("/tasks/1")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["id"] == 1
    assert response_json["name"] == "test task 1"
    assert response_json["car_id"] == "car_1"
    assert response_json["car_id"] == "car_1"
    assert response_json["status"] == "in progress"
    assert response_json["messages"] == []
    assert "created_at" in response_json
    assert "updated_at" in response_json


def test_read_task_by_invalid_id(client: TestClient, session: Session):
    response = client.get("/tasks/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Task with id=1 not found"}
