import logging

import uvicorn
from fastapi import FastAPI, HTTPException, status

import actions
import dependencies
import schemas

logger = logging.getLogger("uvicorn.error")

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/cars", response_model=schemas.CarList)
def get_cars(garage_client: dependencies.GarageClientDepends):
    return garage_client.get_car_list()


@app.post("/cars/{car_id}/actions/check", response_model=schemas.CheckCar)
async def check_car(car_id: str, garage_client: dependencies.GarageClientDepends):
    try:
        result = actions.check_car(car_id, garage_client)
    except actions.CarActionsError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        )
    except Exception as err:
        logger.error("Unexpected error: %s\ntype(err): %s", err, type(err))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return result


@app.post(
    "/cars/{car_id}/actions/send_for_repair", response_model=schemas.SendForRepairCar
)
async def send_for_repair_car(
    car_id: str, problem: str, garage_client: dependencies.GarageClientDepends
):
    try:
        result = actions.send_for_repair(car_id, problem, garage_client)
    except actions.CarActionsError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        )
    except Exception as err:
        logger.error("Unexpected error: %s\ntype(err): %s", err, type(err))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return result


@app.post(
    "/cars/{car_id}/actions/send_to_parking", response_model=schemas.SendToParkingCar
)
async def send_to_parking(car_id: str, garage_client: dependencies.GarageClientDepends):
    try:
        result = actions.send_to_parking(car_id, garage_client)
    except actions.CarActionsError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        )
    except Exception as err:
        logger.error("Unexpected error: %s\ntype(err): %s", err, type(err))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
