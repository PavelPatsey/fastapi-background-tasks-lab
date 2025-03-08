import logging
from garage import GarageClient
import schemas


logger = logging.getLogger(__name__)


class CarActionsError(Exception):
    pass


def _check(car_id: str, garage_client: GarageClient):
    try:
        response = garage_client.check(car_id)
    except Exception as err:
        msg = f"Error while trying to check car {repr(car_id)}!"
        logger.error("msg: %s\nerr: %s\ntype(err): %s", msg, err, type(err))
        raise CarActionsError(msg)
    logger.info("car check response: %s", response)


def check_car(car_id: str, garage_client: GarageClient):
    logger.info("Started check car %s", repr(car_id))
    _check(car_id, garage_client)
    logger.info("Check car %s completed successfully", repr(car_id))
    return schemas.CheckCar(car_id=car_id, result=True, message="ok")
