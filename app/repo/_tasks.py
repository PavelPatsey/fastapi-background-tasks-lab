from datetime import UTC, datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas


class RepoTasksError(Exception):
    pass


async def create_task(name: str, car_id: str, session: AsyncSession) -> models.Task:
    task_in = schemas.TaskCreate(
        name=name,
        car_id=car_id,
        status=schemas.TaskStatuses.in_progress,
    )
    data = task_in.model_dump()
    task = models.Task(**data)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def update_task(task_id: int, data: dict, session: AsyncSession) -> models.Task:
    stmt = select(models.Task).where(models.Task.id == task_id)
    result = await session.execute(stmt)
    task = result.scalars().first()
    if not task:
        raise RepoTasksError(f"There is no task with id={task_id}")
    for field, value in data.items():
        setattr(task, field, value)
    setattr(task, "updated_at", datetime.now(UTC).replace(microsecond=0))
    await session.commit()
    await session.refresh(task)
    return task


async def read_tasks(
    session: AsyncSession, offset: int | None = None, limit: int | None = None
) -> Sequence[models.Task]:
    stmt = select(models.Task).order_by(models.Task.id.desc())
    if offset is not None:
        stmt = stmt.offset(offset)
    if limit is not None:
        stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()
