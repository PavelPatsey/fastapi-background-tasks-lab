from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, schemas


def test_send_for_repair(client: TestClient, session: Session):
    car_id = "car_1"
    test_problem = "test car problem"
    response = client.post(
        f"/cars/{car_id}/actions/send_for_repair?problem={test_problem}"
    )
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["id"] == 1
    assert (
        response_json["name"]
        == "send car 'car_1' for repair with problem 'test car problem'"
    )
    assert response_json["car_id"] == "car_1"
    assert response_json["status"] == "in progress"
    assert response_json["messages"] == []
    assert "created_at" in response_json
    assert "updated_at" in response_json

    task = session.get(models.Task, response_json["id"])
    assert task.status == schemas.TaskStatuses.completed
    assert [msg.body for msg in task.messages] == [
        "Start send car 'car_1' for repair with problem 'test car problem'",
        "Ping 'car_1': Ok",
        "Car 'car_1' problems: []",
        "Car 'car_1' problems after adding: ['test car problem']",
        "Car 'car_1' problems: ['test car problem']",
        "Car 'car_1' status after update: under repair",
        "End send car 'car_1' for repair with problem 'test car problem'",
    ]


def test_repair_error_while_trying_to_check(client: TestClient, session: Session):
    car_id = "invalid_repair_car"
    test_problem = "test car problem"
    response = client.post(
        f"/cars/{car_id}/actions/send_for_repair?problem={test_problem}"
    )
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    task = session.get(models.Task, response_json["id"])
    assert task.status == schemas.TaskStatuses.failed
    assert [msg.body for msg in task.messages] == [
        f"Start send car '{car_id}' for repair with problem '{test_problem}'",
        "Error while trying to check car 'invalid_repair_car'!",
        "End send car 'invalid_repair_car' for repair with problem 'test car problem'",
    ]
