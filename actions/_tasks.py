import sqlalchemy

import models
import schemas

from ._helpers import CarActionsError, get_current_time


def _create_task_model(name: str, car_id: str):
    return schemas.Task(
        name=name,
        car_id=car_id,
        status="in progress",
        messages=[
            {
                "timestamp": get_current_time(),
                "msg": f"start {name}",
            }
        ],
    )


def _create_task(
    task: schemas.Task,
    session: sqlalchemy.orm.Session,
) -> models.Task:
    task_data = task.model_dump()
    db_task = models.Task(**task_data)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


def _update_task(
    task_id: int,
    data: dict,
    session: sqlalchemy.orm.Session,
) -> models.Task:
    task_db: models.Task = session.get(models.Task, task_id)
    if not task_db:
        raise CarActionsError(f"There is no task with id={task_id}")
    for field, value in data.items():
        if field == "messages":
            messages: list = list(task_db.messages)
            messages.extend(value)
            setattr(task_db, field, messages)
        else:
            setattr(task_db, field, value)
    session.commit()
    session.refresh(task_db)
    return task_db
