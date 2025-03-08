import logging
from typing import Annotated

import uvicorn
from fastapi import FastAPI, HTTPException, Query, status
from sqlmodel import SQLModel, create_engine, select

import actions
import dependencies
import models
import schemas
import settings
from models import Task

logger = logging.getLogger("uvicorn.error")

app = FastAPI()

engine = create_engine(settings.SQLITE_URL, connect_args=settings.CONNECT_ARGS)
SQLModel.metadata.create_all(engine)


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


@app.post("/tasks/", response_model=models.TaskPublic)
def create_task(task: models.TaskCreate, session: dependencies.SQLSessionDepends):
    db_task = Task.model_validate(task)
    return actions.create_task(db_task, session)


@app.get("/tasks/", response_model=list[models.TaskPublic])
def read_tasks(
    session: dependencies.SQLSessionDepends,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    tasks = session.exec(select(Task).offset(offset).limit(limit)).all()
    return tasks


@app.get("/tasks/{task_id}", response_model=models.TaskPublic)
def read_task(task_id: int, session: dependencies.SQLSessionDepends):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/tasks/{task_id}", response_model=models.Task)
def update_task(
    task_id: int, task: models.TaskUpdate, session: dependencies.SQLSessionDepends
):
    task_db = session.get(Task, task_id)
    if not task_db:
        raise HTTPException(status_code=404, detail="Task not found")
    task_data = task.model_dump(exclude_unset=True)
    task_db.sqlmodel_update(task_data)
    session.add(task_db)
    session.commit()
    session.refresh(task_db)
    return task_db


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: dependencies.SQLSessionDepends):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
