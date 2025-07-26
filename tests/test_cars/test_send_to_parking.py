from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, schemas


def test_send_to_parking(client: TestClient, session: Session):
    car_id = "car_3"
    response = client.post(f"/cars/{car_id}/actions/send_to_parking")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["id"] == 1
    assert response_json["name"] == "send car 'car_3' to parking"
    assert response_json["car_id"] == "car_3"
    assert response_json["status"] == "in progress"
    assert response_json["messages"] == []
    assert "created_at" in response_json
    assert "updated_at" in response_json

    task = session.get(models.Task, response_json["id"])
    assert task.status == schemas.TaskStatuses.completed
    assert [msg.body for msg in task.messages] == [
        "Start send car 'car_3' to parking",
        "Ping 'car_3': Ok",
        "Car 'car_3' problems: []",
        "Car 'car_3' problems after fixing: []",
        "Car 'car_3' problems: []",
        "Car 'car_3' status after update: ok",
        "End send car 'car_3' to parking",
    ]


def test_parking_error_while_trying_to_check(client: TestClient, session: Session):
    car_id = "invalid_parking_car"
    response = client.post(f"/cars/{car_id}/actions/send_to_parking")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    task = session.get(models.Task, response_json["id"])
    assert task.status == schemas.TaskStatuses.failed
    assert [msg.body for msg in task.messages] == [
        "Start send car 'invalid_parking_car' to parking",
        "Error while trying to check car 'invalid_parking_car'!",
        "End send car 'invalid_parking_car' to parking",
    ]
