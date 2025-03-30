import logging
from datetime import datetime

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


def _check(car_id: str, garage_client: GarageClient) -> dict | bool:
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


def _get_problems(car_id: str, garage_client: GarageClient) -> list[str]:
    try:
        response = garage_client.get_problems(car_id)
    except Exception as err:
        msg = f"Error while trying to get problems of car {repr(car_id)}!"
        logger.error("msg: %s\nerr: %s\ntype(err): %s", msg, err, type(err))
        raise CarActionsError(msg)
    problems = response.get("problems", [])
    logger.info("car get problems response: %s", response)
    return problems


def _add_problem(car_id: str, problem: str, garage_client: GarageClient):
    try:
        response = garage_client.add_problem(car_id, problem)
    except Exception as err:
        msg = (
            f"Error while trying to add problem {repr(problem)} to car {repr(car_id)}!"
        )
        logger.error("msg: %s\nerr: %s\ntype(err): %s", msg, err, type(err))
        raise CarActionsError(msg)
    logger.info("car add problem response: %s", response)


def _fix_problems(car_id: str, garage_client: GarageClient):
    try:
        response = garage_client.fix_problems(car_id)
    except Exception as err:
        msg = f"Error while trying to fix problems of car {repr(car_id)}!"
        logger.error("msg: %s\nerr: %s\ntype(err): %s", msg, err, type(err))
        raise CarActionsError(msg)
    logger.info("car fix problems response: %s", response)


def _update_status(car_id: str, garage_client: GarageClient, max_tries_count: int = 3):
    counter = 0
    is_successful = False
    response = None
    while counter < max_tries_count and not is_successful:
        try:
            response = garage_client.update_status(car_id)
            is_successful = True
        except Exception as err:
            msg = f"Error while trying to updute status of car {repr(car_id)}!"
            logger.error("msg: %s\nerr: %s\ntype(err): %s", msg, err, type(err))
            counter += 1
            logger.info("attempts made: %s", counter)
            if counter == max_tries_count:
                raise CarActionsError(msg)
    logger.info("car update response: %s", response)


###########
# actions #
###########


def check_car(
    car_id: str,
    task_id: int,
    garage_client: GarageClient,
    session: sqlalchemy.orm.Session,
):
    messages = []
    status = "completed"
    steps = [lambda: _check(car_id, garage_client)]

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
            "msg": f"finish check {repr(car_id)}",
        }
    )
    data = {"status": status, "messages": messages}
    _ = update_task(task_id, data, session)
    return


def send_for_repair(car_id: str, problem: str, garage_client: GarageClient):
    logger.info("Started send for repair car %s", repr(car_id))
    _check(car_id, garage_client)
    _get_problems(car_id, garage_client)
    _add_problem(car_id, problem, garage_client)
    problems = _get_problems(car_id, garage_client)
    _update_status(car_id, garage_client)

    logger.info("Send car for repair %s completed successfully", repr(car_id))
    return schemas.SendForRepairCar(
        car_id=car_id,
        result=True,
        problems=problems,
        message="ok",
    )


def send_to_parking(car_id: str, garage_client: GarageClient):
    logger.info("Started send for repair car %s", repr(car_id))
    _check(car_id, garage_client)
    _get_problems(car_id, garage_client)
    _fix_problems(car_id, garage_client)
    _get_problems(car_id, garage_client)
    _update_status(car_id, garage_client)

    logger.info("Send car for repair %s completed successfully", repr(car_id))
    return schemas.SendToParkingCar(
        car_id=car_id,
        result=True,
        message="ok",
    )


######################
# Background actions #
######################


def background_check_car(
    car_id: str,
    garage_client: GarageClient,
    background_tasks: BackgroundTasks,
    session: sqlalchemy.orm.Session,
):
    task = schemas.Task(
        name=f"check {repr(car_id)}",
        car_id=car_id,
        status="in progress",
        messages=[
            {
                "timestamp": get_current_time(),
                "msg": f"start check {repr(car_id)}",
            }
        ],
    )
    db_task = create_task(task, session)
    background_tasks.add_task(check_car, car_id, db_task.id, garage_client, session)
    return db_task


################
# Task actions #
################


def create_task(
    model_task: schemas.Task,
    session: sqlalchemy.orm.Session,
) -> models.Task:
    task_data = model_task.model_dump()
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
