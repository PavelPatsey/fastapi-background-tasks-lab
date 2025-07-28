import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.schemas import TaskStatuses


@pytest.mark.asyncio
async def test_read_tasks(async_client: AsyncClient, async_session: AsyncSession):
    task_1 = models.Task(
        name="test task 1",
        car_id="car_1",
        status=TaskStatuses.in_progress,
    )
    async_session.add(task_1)
    await async_session.commit()

    response = await async_client.get("/tasks")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["name"] == "test task 1"


@pytest.mark.asyncio
async def test_read_task_by_id(async_client: AsyncClient, async_session: AsyncSession):
    task_in = schemas.TaskCreate(
        name="test task 1",
        car_id="car_1",
        status=TaskStatuses.in_progress,
    )
    task = models.Task(**task_in.model_dump())
    async_session.add(task)
    await async_session.commit()

    response = await async_client.get("/tasks/1")
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


@pytest.mark.asyncio
async def test_read_task_by_invalid_id(async_client: AsyncClient):
    response = await async_client.get("/tasks/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Task with id=1 not found"}
