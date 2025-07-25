from datetime import UTC, datetime

import sqlalchemy

from app import models, schemas


class RepoTasksError(Exception):
    pass


def create_task(
    name: str,
    car_id: str,
    session: sqlalchemy.orm.Session,
) -> models.Task:
    task_in = schemas.TaskCreate(
        name=name,
        car_id=car_id,
        status=schemas.TaskStatuses.in_progress,
    )
    data = task_in.model_dump()
    db_task = models.Task(**data)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


def update_task(
    task_id: int,
    data: dict,
    session: sqlalchemy.orm.Session,
) -> models.Task:
    task_db: models.Task = session.get(models.Task, task_id)
    if not task_db:
        raise RepoTasksError(f"There is no task with id={task_id}")
    for field, value in data.items():
        setattr(task_db, field, value)
    setattr(task_db, "updated_at", datetime.now(UTC).replace(microsecond=0))
    session.commit()
    session.refresh(task_db)
    return task_db
