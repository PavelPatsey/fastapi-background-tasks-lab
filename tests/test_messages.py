from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, schemas


def test_read_messages(client: TestClient, session: Session):
    msg_in_1 = schemas.MessageCreate(body={"msg": "test msg 1"}, task_id=1)
    msg_in_2 = schemas.MessageCreate(body={"msg": "test msg 2"}, task_id=1)
    msg_1 = models.Message(**msg_in_1.model_dump())
    msg_2 = models.Message(**msg_in_2.model_dump())

    session.add(msg_1)
    session.add(msg_2)
    session.commit()

    response = client.get("/messages")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["messages"]) == 2
    assert data["messages"][0] == {"body": {"msg": "test msg 2"}, "id": 2, "task_id": 1}
    assert data["messages"][1] == {"body": {"msg": "test msg 1"}, "id": 1, "task_id": 1}
