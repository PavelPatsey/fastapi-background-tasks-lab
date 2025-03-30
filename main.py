import logging
from typing import Annotated

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, status
from sqlalchemy import create_engine

import actions
import dependencies
import models
import schemas
import settings

logger = logging.getLogger("uvicorn.error")

app = FastAPI()


engine = create_engine(settings.SQLITE_URL, connect_args=settings.CONNECT_ARGS)
models.Base.metadata.create_all(engine)


@app.get("/")
async def root():
    return {
        "message": "Hello World",
        "current_time": actions.get_current_time(),
    }


@app.get("/cars", response_model=schemas.CarList)
def get_cars(garage_client: dependencies.GarageClientDepends):
    return garage_client.get_car_list()


@app.post("/cars/{car_id}/actions/check", response_model=schemas.CheckCar)
async def check_car(
    car_id: str,
    garage_client: dependencies.GarageClientDepends,
    background_tasks: BackgroundTasks,
    session: dependencies.SQLSessionDepends,
):
    try:
        db_task = actions.background_check_car(
            car_id,
            garage_client,
            background_tasks,
            session,
        )
    except actions.CarActionsError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    return schemas.CheckCar(
        car_id=car_id,
        task_id=db_task.id,
        message="ok",
    )


@app.post(
    "/cars/{car_id}/actions/send_for_repair", response_model=schemas.SendForRepairCar
)
async def send_for_repair_car(
    car_id: str,
    problem: str,
    garage_client: dependencies.GarageClientDepends,
    background_tasks: BackgroundTasks,
    session: dependencies.SQLSessionDepends,
):
    try:
        db_task = actions.background_send_for_repair(
            car_id,
            problem,
            garage_client,
            background_tasks,
            session,
        )
    except actions.CarActionsError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    return schemas.CheckCar(
        car_id=car_id,
        task_id=db_task.id,
        message="ok",
    )


@app.post(
    "/cars/{car_id}/actions/send_to_parking", response_model=schemas.SendToParkingCar
)
async def send_to_parking(car_id: str, garage_client: dependencies.GarageClientDepends):
    try:
        result = actions.send_to_parking(car_id, garage_client)
    except actions.CarActionsError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    return result


@app.get("/tasks/", response_model=schemas.TaskList)
def read_tasks(
    session: dependencies.SQLSessionDepends,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> schemas.TaskList:
    db_tasks = session.query(models.Task).offset(offset).limit(limit).all()
    tasks = [schemas.Task.model_validate(task) for task in reversed(db_tasks)]
    return schemas.TaskList(tasks=tasks)


@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, session: dependencies.SQLSessionDepends) -> schemas.Task:
    task = session.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id={task_id} not found")
    return schemas.Task.model_validate(task)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
