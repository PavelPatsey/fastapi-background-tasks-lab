import logging
from typing import Annotated

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, status
from sqlalchemy import create_engine

import actions
import dependencies
import helpers
import models
import schemas
import settings

logger = logging.getLogger("uvicorn.error")

app = FastAPI()


engine = create_engine(settings.DB_URL, connect_args=settings.CONNECT_ARGS)
models.Base.metadata.create_all(engine)


@app.get("/", tags=["common"])
async def root():
    return {
        "message": "Hello World",
        "current_time": helpers.get_current_time(),
    }


@app.get("/cars", tags=["cars"], response_model=schemas.CarList)
def get_cars(garage_client: dependencies.GarageClientDepends):
    return garage_client.get_car_list()


@app.post(
    "/cars/{car_id}/actions/check",
    tags=["cars"],
    response_model=schemas.CheckCar,
)
async def check_car(
    car_id: str,
    garage_client: dependencies.GarageClientDepends,
    background_tasks: BackgroundTasks,
    session: dependencies.SessionDepends,
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
    "/cars/{car_id}/actions/send_for_repair",
    tags=["cars"],
    response_model=schemas.SendForRepairCar,
)
async def send_for_repair_car(
    car_id: str,
    problem: str,
    garage_client: dependencies.GarageClientDepends,
    background_tasks: BackgroundTasks,
    session: dependencies.SessionDepends,
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
    "/cars/{car_id}/actions/send_to_parking",
    tags=["cars"],
    response_model=schemas.SendToParkingCar,
)
async def send_to_parking(
    car_id: str,
    garage_client: dependencies.GarageClientDepends,
    background_tasks: BackgroundTasks,
    session: dependencies.SessionDepends,
):
    try:
        db_task = actions.background_send_to_parking(
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


@app.get("/tasks/", tags=["tasks"], response_model=schemas.TaskList)
def read_tasks(
    session: dependencies.SessionDepends,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> schemas.TaskList:
    db_tasks = session.query(models.Task).offset(offset).limit(limit).all()
    tasks = [schemas.Task.model_validate(task) for task in reversed(db_tasks)]
    return schemas.TaskList(tasks=tasks)


@app.get("/tasks/{task_id}", tags=["tasks"], response_model=schemas.Task)
def read_task(task_id: int, session: dependencies.SessionDepends) -> schemas.Task:
    task = session.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id={task_id} not found")
    return schemas.Task.model_validate(task)


@app.get("/messages/", tags=["messages"], response_model=schemas.MessageList)
def read_tasks(
    session: dependencies.SessionDepends,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> schemas.MessageList:
    db_tasks = session.query(models.Message).offset(offset).limit(limit).all()
    messages = [schemas.Message.model_validate(task) for task in reversed(db_tasks)]
    return schemas.MessageList(messages=messages)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
