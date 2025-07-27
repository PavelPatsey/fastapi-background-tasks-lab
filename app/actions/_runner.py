from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.repo import create_message, update_task

from ._garage import ActionsGarageError


async def _run_steps(
    name: str, steps: list[Callable], task_id: int, session: AsyncSession
):
    status = schemas.TaskStatuses.completed
    is_successful = True
    _msg = await create_message(f"Start {name}", task_id, session)
    while steps and is_successful:
        step_func = steps.pop()
        msg = None
        try:
            _res, msg = await step_func()
        except ActionsGarageError as err:
            status = schemas.TaskStatuses.failed
            is_successful = False
            msg = str(err)
        finally:
            _msg = await create_message(msg, task_id, session)
    _msg = await create_message(f"End {name}", task_id, session)
    return await update_task(task_id, {"status": status}, session)
