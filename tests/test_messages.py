import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas


@pytest.mark.asyncio
async def test_read_messages(async_client: AsyncClient, async_session: AsyncSession):
    msg_in_1 = schemas.MessageCreate(body="test msg 1", task_id=1)
    msg_in_2 = schemas.MessageCreate(body="test msg 2", task_id=1)
    msg_1 = models.Message(**msg_in_1.model_dump())
    msg_2 = models.Message(**msg_in_2.model_dump())

    async_session.add(msg_1)
    async_session.add(msg_2)
    await async_session.commit()

    response = await async_client.get("/messages")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert len(response_json["messages"]) == 2
    msg_data_1 = response_json["messages"][1]
    msg_data_2 = response_json["messages"][0]

    assert msg_data_1["body"] == "test msg 1"
    assert msg_data_1["id"] == 1
    assert msg_data_1["task_id"] == 1
    assert "created_at" in msg_data_1
    assert isinstance(msg_data_1["created_at"], str)

    assert msg_data_2["body"] == "test msg 2"
    assert msg_data_2["id"] == 2
    assert msg_data_2["task_id"] == 1
    assert "created_at" in msg_data_2
    assert isinstance(msg_data_2["created_at"], str)
