from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, schemas


def test_check_car(client: TestClient, session: Session):
    car_id = "car_1"
    response = client.post(f"/cars/{car_id}/actions/check")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json == {
        "car_id": "car_1",
        "task_id": 1,
        "message": "ok",
    }
    task_id = response_json["task_id"]
    task = session.get(models.Task, task_id)
    assert task.status == schemas.TaskStatuses.completed
    assert [msg.body for msg in task.messages] == [
        "Start check 'car_1'",
        "Ping 'car_1': Ok",
        "End check 'car_1'",
    ]


def test_error_while_trying_to_check(client: TestClient, session: Session):
    car_id = "invalid_car"
    response = client.post(f"/cars/{car_id}/actions/check")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json == {
        "car_id": "invalid_car",
        "task_id": 1,
        "message": "ok",
    }
    task_id = response_json["task_id"]
    task = session.get(models.Task, task_id)
    assert task.status == schemas.TaskStatuses.failed
    assert [msg.body for msg in task.messages] == [
        "Start check 'invalid_car'",
        "Error while trying to check car 'invalid_car'!",
        "End check 'invalid_car'",
    ]
