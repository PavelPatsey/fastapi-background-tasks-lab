import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.repo import RepoTasksError, create_task, update_task


@pytest.mark.asyncio
async def test_create_task(async_session: AsyncSession):
    name = "test task name"
    car_id = "test car id"
    task = await create_task(name=name, car_id=car_id, session=async_session)
    assert isinstance(task, models.Task)
    assert hasattr(task, "id")
    assert hasattr(task, "name")
    assert hasattr(task, "car_id")
    assert hasattr(task, "status")
    assert hasattr(task, "created_at")
    assert hasattr(task, "updated_at")
    assert hasattr(task, "messages")
    assert task.id == 1
    assert task.name == name
    assert task.car_id == car_id
    assert task.status == "in progress"
    assert task.messages == []


@pytest.mark.asyncio
async def test_update_task(async_session: AsyncSession):
    name = "test task name"
    car_id = "test car id"
    task = await create_task(name=name, car_id=car_id, session=async_session)
    data = {"status": schemas.TaskStatuses.completed}
    task = await update_task(task_id=task.id, data=data, session=async_session)
    assert task.status == schemas.TaskStatuses.completed
    assert task.created_at <= task.updated_at


@pytest.mark.asyncio
async def test_update_task_invalid_task_id(async_session: AsyncSession):
    data = {"status": schemas.TaskStatuses.completed}

    with pytest.raises(RepoTasksError) as exc_info:
        await update_task(task_id=1, data=data, session=async_session)

    assert str(exc_info.value) == "There is no task with id=1"
