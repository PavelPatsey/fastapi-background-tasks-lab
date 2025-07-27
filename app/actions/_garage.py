import logging

from app.garage import GarageClient

logger = logging.getLogger("uvicorn.error")


class ActionsGarageError(Exception):
    pass


async def _check(car_id: str, garage_client: GarageClient) -> tuple[dict, str]:
    try:
        result = await garage_client.check(car_id)
    except Exception as err:
        msg = f"Error while trying to check car {repr(car_id)}!"
        logger.error("msg: %s, err: %s, type(err): %s", msg, err, type(err))
        raise ActionsGarageError(msg)
    return result, f"Ping {repr(car_id)}: Ok"


async def _get_problems(car_id: str, garage_client: GarageClient) -> tuple[dict, str]:
    try:
        result = await garage_client.get_problems(car_id)
    except Exception as err:
        msg = f"Error while trying to get problems of car {repr(car_id)}!"
        logger.error("msg: %s, err: %s, type(err): %s", msg, err, type(err))
        raise ActionsGarageError(msg)
    return result, f"Car {repr(car_id)} problems: {result.get(car_id)}"


async def _add_problem(
    car_id: str, problem: str, garage_client: GarageClient
) -> tuple[dict, str]:
    try:
        result = await garage_client.add_problem(car_id, problem)
    except Exception as err:
        msg = (
            f"Error while trying to add problem {repr(problem)} to car {repr(car_id)}!"
        )
        logger.error("msg: %s, err: %s, type(err): %s", msg, err, type(err))
        raise ActionsGarageError(msg)
    return result, f"Car {repr(car_id)} problems after adding: {result.get(car_id)}"


async def _fix_problems(car_id: str, garage_client: GarageClient) -> tuple[dict, str]:
    try:
        result = await garage_client.fix_problems(car_id)
    except Exception as err:
        msg = f"Error while trying to fix problems of car {repr(car_id)}!"
        logger.error("msg: %s, err: %s, type(err): %s", msg, err, type(err))
        raise ActionsGarageError(msg)
    return result, f"Car {repr(car_id)} problems after fixing: {result.get(car_id)}"


async def _update_status(
    car_id: str, garage_client: GarageClient, max_tries_count: int = 3
) -> tuple[dict, str]:
    result = {}
    counter = 0
    is_successful = False
    while counter < max_tries_count and not is_successful:
        try:
            result = await garage_client.update_status(car_id)
            is_successful = True
        except Exception as err:
            msg = f"Error while trying to update status of car {repr(car_id)}!"
            logger.error("msg: %s, err: %s, type(err): %s", msg, err, type(err))
            logger.info("attempts made: %s", counter)
            if counter >= max_tries_count:
                raise ActionsGarageError(msg)
        finally:
            counter += 1
    return result, f"Car {repr(car_id)} status after update: {result.get(car_id)}"
