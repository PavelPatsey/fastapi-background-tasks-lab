import logging
from functools import partial

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.garage import GarageClient
from app.repo import create_task

from ._garage import _add_problem, _check, _fix_problems, _get_problems, _update_status
from ._runner import _run_steps


class ActionsCarsError(Exception):
    pass


logger = logging.getLogger("uvicorn.error")


async def check_car(
    car_id: str,
    garage_client: GarageClient,
    background_tasks: BackgroundTasks,
    session: AsyncSession,
) -> models.Task:
    name = f"check {repr(car_id)}"
    task = await create_task(name, car_id, session)
    steps = [partial(_check, car_id, garage_client)]
    background_tasks.add_task(_run_steps, name, steps, task.id, session)
    return task


async def send_for_repair(
    car_id: str,
    problem: str,
    garage_client: GarageClient,
    background_tasks: BackgroundTasks,
    session: AsyncSession,
) -> models.Task:
    name = f"send car {repr(car_id)} for repair with problem {repr(problem)}"
    task = await create_task(name, car_id, session)
    steps = [
        partial(_check, car_id, garage_client),
        partial(_get_problems, car_id, garage_client),
        partial(_add_problem, car_id, problem, garage_client),
        partial(_get_problems, car_id, garage_client),
        partial(_update_status, car_id, garage_client),
    ][::-1]
    background_tasks.add_task(_run_steps, name, steps, task.id, session)
    return task


async def send_to_parking(
    car_id: str,
    garage_client: GarageClient,
    background_tasks: BackgroundTasks,
    session: AsyncSession,
) -> models.Task:
    name = f"send car {repr(car_id)} to parking"
    task = await create_task(name, car_id, session)
    steps = [
        partial(_check, car_id, garage_client),
        partial(_get_problems, car_id, garage_client),
        partial(_fix_problems, car_id, garage_client),
        partial(_get_problems, car_id, garage_client),
        partial(_update_status, car_id, garage_client),
    ][::-1]
    background_tasks.add_task(_run_steps, name, steps, task.id, session)
    return task
