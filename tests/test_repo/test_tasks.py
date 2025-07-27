import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, repo, schemas
from app.repo import RepoTasksError, create_task, update_task


@pytest.mark.asyncio
async def test_create_task(async_session: AsyncSession):
    name = "test task name"
    car_id = "test car id"
    task = await create_task(name=name, car_id=car_id, session=async_session)
    assert isinstance(task, models.Task)
    assert task.id == 1
    assert task.name == name
    assert task.car_id == car_id
    assert task.status == "in progress"
    assert isinstance("created_at", str)
    assert isinstance("updated_at", str)
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


@pytest.mark.asyncio
async def test_read_tasks(async_session: AsyncSession):
    task_1 = models.Task(
        name="test task 1",
        car_id="car_1",
        status=schemas.TaskStatuses.in_progress,
    )
    task_2 = models.Task(
        name="test task 2",
        car_id="car_2",
        status=schemas.TaskStatuses.in_progress,
    )
    async_session.add(task_1)
    async_session.add(task_2)
    await async_session.commit()

    tasks = await repo.read_tasks(async_session)
    assert task_2 == tasks[0]
    assert task_1 == tasks[1]

    tasks = await repo.read_tasks(async_session, 0, 1)
    assert len(tasks) == 1
    assert task_2 == tasks[0]

    tasks = await repo.read_tasks(async_session, 1, 1)
    assert len(tasks) == 1
    assert task_1 == tasks[0]
