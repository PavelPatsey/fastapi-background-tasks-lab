import logging
from functools import partial
from typing import Callable

import sqlalchemy
from fastapi import BackgroundTasks

from garage import GarageClient

from ._garage import _add_problem, _check, _fix_problems, _get_problems, _update_status
from ._messages import create_message
from ._tasks import _create_task, _create_task_model, _update_task

logger = logging.getLogger("uvicorn.error")


def _run_steps(
    name: str,
    steps: list[Callable],
    task_id: int,
    session: sqlalchemy.orm.Session,
):
    status = "completed"
    is_successful = True
    while steps and is_successful:
        step_func = steps.pop()
        return_value = step_func()
        _ = create_message(return_value, task_id, session)
        if not (is_successful := return_value.get("success")):
            status = "failed"
    _ = create_message({"msg": f"finish {name}", "status": status}, task_id, session)
    data = {"status": status}
    _ = _update_task(task_id, data, session)
    return


def background_check_car(
    car_id: str,
    garage_client: GarageClient,
    background_tasks: BackgroundTasks,
    session: sqlalchemy.orm.Session,
):
    name = f"check {repr(car_id)}"
    task = _create_task_model(name, car_id)
    db_task = _create_task(task, session)
    _ = create_message({"msg": f"start {name}"}, db_task.id, session)

    steps = [partial(_check, car_id, garage_client)]
    background_tasks.add_task(_run_steps, name, steps, db_task.id, session)
    return db_task


def background_send_for_repair(
    car_id: str,
    problem: str,
    garage_client: GarageClient,
    background_tasks: BackgroundTasks,
    session: sqlalchemy.orm.Session,
):
    name = f"send for repair {repr(car_id)} with problem {repr(problem)}"
    task = _create_task_model(name, car_id)
    db_task = _create_task(task, session)
    _ = create_message({"msg": f"start {name}"}, db_task.id, session)
    steps = [
        partial(_check, car_id, garage_client),
        partial(_get_problems, car_id, garage_client),
        partial(_add_problem, car_id, problem, garage_client),
        partial(_get_problems, car_id, garage_client),
        partial(_update_status, car_id, garage_client),
    ][::-1]
    background_tasks.add_task(_run_steps, name, steps, db_task.id, session)
    return db_task


def background_send_to_parking(
    car_id: str,
    garage_client: GarageClient,
    background_tasks: BackgroundTasks,
    session: sqlalchemy.orm.Session,
):
    name = f"send to parking car {repr(car_id)}"
    task = _create_task_model(name, car_id)
    db_task = _create_task(task, session)
    _ = create_message({"msg": f"start {name}"}, db_task.id, session)
    steps = [
        partial(_check, car_id, garage_client),
        partial(_get_problems, car_id, garage_client),
        partial(_fix_problems, car_id, garage_client),
        partial(_get_problems, car_id, garage_client),
        partial(_update_status, car_id, garage_client),
    ][::-1]
    background_tasks.add_task(_run_steps, name, steps, db_task.id, session)
    return db_task
