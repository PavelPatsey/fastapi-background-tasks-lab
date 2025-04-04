import logging
from datetime import datetime
from typing import Callable

import sqlalchemy
from fastapi import BackgroundTasks

import models
import schemas
from garage import GarageClient

logger = logging.getLogger("uvicorn.error")


class CarActionsError(Exception):
    pass


def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


##################
# Garage actions #
##################


def _check(car_id: str, garage_client: GarageClient) -> dict:
    result = {}
    try:
        response = garage_client.check(car_id)
        result["response"] = response
        result["success"] = True
    except Exception as err:
        msg = f"Error while trying to check car {repr(car_id)}!"
        logger.error("msg: %s\nerr: %s\ntype(err): %s", msg, err, type(err))
        result["error"] = msg
        result["success"] = False
    result["timestamp"] = get_current_time()
    return result


def _get_problems(car_id: str, garage_client: GarageClient) -> dict:
    result = {}
    try:
        response = garage_client.get_problems(car_id)
        result["response"] = response
        result["success"] = True
    except Exception as err:
        msg = f"Error while trying to get problems of car {repr(car_id)}!"
        logger.error("msg: %s\nerr: %s\ntype(err): %s", msg, err, type(err))
        result["error"] = msg
        result["success"] = False
    result["timestamp"] = get_current_time()
    return result


def _add_problem(car_id: str, problem: str, garage_client: GarageClient) -> dict:
    result = {}
    try:
        response = garage_client.add_problem(car_id, problem)
        result["response"] = response
        result["success"] = True
    except Exception as err:
        msg = (
            f"Error while trying to add problem {repr(problem)} to car {repr(car_id)}!"
        )
        logger.error("msg: %s\nerr: %s\ntype(err): %s", msg, err, type(err))
        result["error"] = msg
        result["success"] = False
    result["timestamp"] = get_current_time()
    return result


def _fix_problems(car_id: str, garage_client: GarageClient) -> dict:
    result = {}
    try:
        response = garage_client.fix_problems(car_id)
        result["response"] = response
        result["success"] = True
    except Exception as err:
        msg = f"Error while trying to fix problems of car {repr(car_id)}!"
        logger.error("msg: %s\nerr: %s\ntype(err): %s", msg, err, type(err))
        result["error"] = msg
        result["success"] = False
    result["timestamp"] = get_current_time()
    return result


def _update_status(car_id: str, garage_client: GarageClient, max_tries_count: int = 3):
    result = {"attempts": []}
    counter = 0
    is_successful = False
    while counter < max_tries_count and not is_successful:
        counter += 1
        try:
            response = garage_client.update_status(car_id)
            result["response"] = response
            result["success"] = True
            is_successful = True
        except Exception as err:
            msg = f"Error while trying to update status of car {repr(car_id)}!"
            logger.error("msg: %s\nerr: %s\ntype(err): %s", msg, err, type(err))
            logger.info("attempts made: %s", counter)
            result["attempts"].append(
                {
                    "timestamp": get_current_time(),
                    "error": msg,
                    "attempt number": counter,
                }
            )
            if counter == max_tries_count:
                result["error"] = msg
                result["success"] = False
    result["timestamp"] = get_current_time()
    return result


#############
# run_steps #
#############


def run_steps(
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
    _ = update_task(task_id, data, session)
    return


######################
# Background actions #
######################


def background_check_car(
    car_id: str,
    garage_client: GarageClient,
    background_tasks: BackgroundTasks,
    session: sqlalchemy.orm.Session,
):
    name = f"check {repr(car_id)}"
    task = create_task_model(name, car_id)
    db_task = create_task(task, session)

    steps = [lambda: _check(car_id, garage_client)]
    background_tasks.add_task(run_steps, name, steps, db_task.id, session)
    return db_task


def background_send_for_repair(
    car_id: str,
    problem: str,
    garage_client: GarageClient,
    background_tasks: BackgroundTasks,
    session: sqlalchemy.orm.Session,
):
    name = f"send for repair {repr(car_id)} with problem {repr(problem)}"
    task = create_task_model(name, car_id)
    db_task = create_task(task, session)
    steps = [
        lambda: _check(car_id, garage_client),
        lambda: _get_problems(car_id, garage_client),
        lambda: _add_problem(car_id, problem, garage_client),
        lambda: _get_problems(car_id, garage_client),
        lambda: _update_status(car_id, garage_client),
    ][::-1]
    background_tasks.add_task(run_steps, name, steps, db_task.id, session)
    return db_task


def background_send_to_parking(
    car_id: str,
    garage_client: GarageClient,
    background_tasks: BackgroundTasks,
    session: sqlalchemy.orm.Session,
):
    name = f"send to parking car {repr(car_id)}"
    task = create_task_model(name, car_id)
    db_task = create_task(task, session)
    steps = [
        lambda: _check(car_id, garage_client),
        lambda: _get_problems(car_id, garage_client),
        lambda: _fix_problems(car_id, garage_client),
        lambda: _get_problems(car_id, garage_client),
        lambda: _update_status(car_id, garage_client),
    ][::-1]
    background_tasks.add_task(run_steps, name, steps, db_task.id, session)
    return db_task


################
# Task actions #
################


def create_task_model(name: str, car_id: str):
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


def create_task(
    task: schemas.Task,
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
