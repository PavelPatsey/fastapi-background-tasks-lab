import logging

from app.garage import GarageClient
from app.helpers import get_current_time

logger = logging.getLogger("uvicorn.error")


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
