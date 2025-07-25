from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, schemas


def test_check_car(client: TestClient, session: Session):
    car_id = "car_1"
    response = client.post(f"/cars/{car_id}/actions/check")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["id"] == 1
    assert response_json["name"] == "check 'car_1'"
    assert response_json["car_id"] == "car_1"
    assert response_json["status"] == "in progress"
    assert response_json["messages"] == []
    assert "created_at" in response_json
    assert "updated_at" in response_json

    task = session.get(models.Task, response_json["id"])
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
    task = session.get(models.Task, response_json["id"])
    assert task.status == schemas.TaskStatuses.failed
    assert [msg.body for msg in task.messages] == [
        "Start check 'invalid_car'",
        "Error while trying to check car 'invalid_car'!",
        "End check 'invalid_car'",
    ]
