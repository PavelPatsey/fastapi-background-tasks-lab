import logging
from typing import Callable

import sqlalchemy
from fastapi import BackgroundTasks

from garage import GarageClient

from ._garage import _add_problem, _check, _fix_problems, _get_problems, _update_status
from ._helpers import get_current_time
from ._tasks import _create_task, _create_task_model, _update_task

logger = logging.getLogger("uvicorn.error")


def _run_steps(
    name: str,
    steps: list[Callable],
    task_id: int,
    session: sqlalchemy.orm.Session,
):
    messages = []
    status = "completed"
    is_successful = True
    while steps and is_successful:
        step_func = steps.pop()
        return_value = step_func()
        messages.append(return_value)
        if not (is_successful := return_value.get("success")):
            status = "failed"

    messages.append(
        {
            "timestamp": get_current_time(),
            "msg": f"finish {name}",
        }
    )
    data = {"status": status, "messages": messages}
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

    steps = [lambda: _check(car_id, garage_client)]
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
    steps = [
        lambda: _check(car_id, garage_client),
        lambda: _get_problems(car_id, garage_client),
        lambda: _add_problem(car_id, problem, garage_client),
        lambda: _get_problems(car_id, garage_client),
        lambda: _update_status(car_id, garage_client),
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
    steps = [
        lambda: _check(car_id, garage_client),
        lambda: _get_problems(car_id, garage_client),
        lambda: _fix_problems(car_id, garage_client),
        lambda: _get_problems(car_id, garage_client),
        lambda: _update_status(car_id, garage_client),
    ][::-1]
    background_tasks.add_task(_run_steps, name, steps, db_task.id, session)
    return db_task
