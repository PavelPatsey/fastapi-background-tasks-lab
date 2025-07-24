from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models
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
