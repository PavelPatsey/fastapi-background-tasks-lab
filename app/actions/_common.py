import logging
from functools import partial
from typing import Callable

import sqlalchemy
from fastapi import BackgroundTasks

from app import schemas
from app.garage import GarageClient
from app.repo import create_message, create_task, update_task

from ._garage import (
    ActionsGarageError,
    _add_problem,
    _check,
    _fix_problems,
    _get_problems,
    _update_status,
)


class CarActionsError(Exception):
    pass


logger = logging.getLogger("uvicorn.error")


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


def background_check_car(
    car_id: str,
    garage_client: GarageClient,
    background_tasks: BackgroundTasks,
    session: sqlalchemy.orm.Session,
):
    name = f"check {repr(car_id)}"
    task = create_task(name, car_id, session)
    steps = [partial(_check, car_id, garage_client)]
    background_tasks.add_task(_run_steps, name, steps, task.id, session)
    return task


def background_send_for_repair(
    car_id: str,
    problem: str,
    garage_client: GarageClient,
    background_tasks: BackgroundTasks,
    session: sqlalchemy.orm.Session,
):
    name = f"send car {repr(car_id)} for repair with problem {repr(problem)}"
    task = create_task(name, car_id, session)
    steps = [
        partial(_check, car_id, garage_client),
        partial(_get_problems, car_id, garage_client),
        partial(_add_problem, car_id, problem, garage_client),
        partial(_get_problems, car_id, garage_client),
        partial(_update_status, car_id, garage_client),
    ][::-1]
    background_tasks.add_task(_run_steps, name, steps, task.id, session)
    return task


def background_send_to_parking(
    car_id: str,
    garage_client: GarageClient,
    background_tasks: BackgroundTasks,
    session: sqlalchemy.orm.Session,
):
    name = f"send car {repr(car_id)} to parking"
    task = create_task(name, car_id, session)
    steps = [
        partial(_check, car_id, garage_client),
        partial(_get_problems, car_id, garage_client),
        partial(_fix_problems, car_id, garage_client),
        partial(_get_problems, car_id, garage_client),
        partial(_update_status, car_id, garage_client),
    ][::-1]
    background_tasks.add_task(_run_steps, name, steps, task.id, session)
    return task
