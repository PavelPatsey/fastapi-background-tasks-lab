from typing import Callable

import sqlalchemy

from app import schemas
from app.repo import create_message, update_task

from ._garage import ActionsGarageError


def _run_steps(
    name: str,
    steps: list[Callable],
    task_id: int,
    session: sqlalchemy.orm.Session,
):
    status = "completed"
    is_successful = True
    _msg = create_message(f"Start {name}", task_id, session)
    while steps and is_successful:
        step_func = steps.pop()
        msg = None
        try:
            _res, msg = step_func()
        except ActionsGarageError as err:
            status = schemas.TaskStatuses.failed
            is_successful = False
            msg = str(err)
        finally:
            _ = create_message(msg, task_id, session)
    _msg = create_message(f"End {name}", task_id, session)
    return update_task(task_id, {"status": status}, session)
