import sqlalchemy

import models
import schemas


class RepoError(Exception):
    pass


def create_task_model(name: str, car_id: str):
    return schemas.TaskCreate(
        name=name,
        car_id=car_id,
        status=schemas.TaskStatuses.in_progress,
    )


def create_task(
    task: schemas.TaskCreate,
    session: sqlalchemy.orm.Session,
) -> models.Task:
    task_data = task.model_dump()
    db_task = models.Task(**task_data)
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
        raise RepoError(f"There is no task with id={task_id}")
    for field, value in data.items():
        setattr(task_db, field, value)
    session.commit()
    session.refresh(task_db)
    return task_db
