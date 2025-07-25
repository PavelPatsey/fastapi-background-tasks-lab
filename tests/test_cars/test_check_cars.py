from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models


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
    messages = [msg.body for msg in task.messages]
    assert messages[0]["msg"] == "start check 'car_1'"
    assert messages[1]["response"] == {"car_1": True}
    assert messages[1]["success"] == True
    assert messages[2]["msg"] == "finish check 'car_1'"
    assert messages[2]["status"] == "completed"
