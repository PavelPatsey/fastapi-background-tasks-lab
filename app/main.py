import logging
from datetime import datetime
from typing import Annotated

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, status
from sqlalchemy import select

from app import actions, dependencies, helpers, models, schemas

logger = logging.getLogger("uvicorn.error")


app = FastAPI(lifespan=helpers.lifespan)
app_launch_time = datetime.now()


@app.get("/", tags=["common"])
async def root() -> dict:
    uptime = (datetime.now() - app_launch_time).total_seconds()
    return {
        "message": "Hello World",
        "current_time": helpers.get_current_time(),
        "current_uptime": int(uptime),
    }


@app.get("/cars", tags=["cars"], response_model=schemas.CarList)
async def get_cars(garage_client: dependencies.GarageClientDepends) -> schemas.CarList:
    return await garage_client.get_car_list()


@app.post(
    "/cars/{car_id}/actions/check",
    tags=["cars"],
    response_model=schemas.Task,
)
async def check_car(
    car_id: str,
    garage_client: dependencies.GarageClientDepends,
    background_tasks: BackgroundTasks,
    session: dependencies.SessionDepends,
) -> models.Task:
    try:
        task = await actions.check_car(
            car_id,
            garage_client,
            background_tasks,
            session,
        )
    except actions.ActionsCarsError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    return task


@app.post(
    "/cars/{car_id}/actions/send_for_repair",
    tags=["cars"],
    response_model=schemas.Task,
)
async def send_for_repair_car(
    car_id: str,
    problem: str,
    garage_client: dependencies.GarageClientDepends,
    background_tasks: BackgroundTasks,
    session: dependencies.SessionDepends,
) -> models.Task:
    try:
        task = await actions.send_for_repair(
            car_id,
            problem,
            garage_client,
            background_tasks,
            session,
        )
    except actions.ActionsCarsError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    return task


@app.post(
    "/cars/{car_id}/actions/send_to_parking",
    tags=["cars"],
    response_model=schemas.Task,
)
async def send_to_parking(
    car_id: str,
    garage_client: dependencies.GarageClientDepends,
    background_tasks: BackgroundTasks,
    session: dependencies.SessionDepends,
) -> models.Task:
    try:
        task = await actions.send_to_parking(
            car_id,
            garage_client,
            background_tasks,
            session,
        )
    except actions.ActionsCarsError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    return task


@app.get("/tasks", tags=["tasks"], response_model=schemas.TaskList)
async def read_tasks(
    session: dependencies.SessionDepends,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> schemas.TaskList:
    stmt = (
        select(models.Task).order_by(models.Task.id.desc()).offset(offset).limit(limit)
    )
    result = await session.execute(stmt)
    tasks = result.scalars().all()
    tasks = [schemas.Task.model_validate(task) for task in tasks]
    return schemas.TaskList(tasks=tasks)


@app.get("/tasks/{task_id}", tags=["tasks"], response_model=schemas.Task)
async def read_task(task_id: int, session: dependencies.SessionDepends) -> schemas.Task:
    stmt = select(models.Task).where(models.Task.id == task_id)
    result = await session.execute(stmt)
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id={task_id} not found")
    return schemas.Task.model_validate(task)


@app.get("/messages", tags=["messages"], response_model=schemas.MessageList)
async def read_messages(
    session: dependencies.SessionDepends,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> schemas.MessageList:
    stmt = (
        select(models.Message)
        .order_by(models.Message.id.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(stmt)
    messages = result.scalars().all()
    messages = [schemas.Message.model_validate(task) for task in messages]
    return schemas.MessageList(messages=messages)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
