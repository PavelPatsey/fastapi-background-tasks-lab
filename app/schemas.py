import enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Car(BaseModel):
    car_id: str
    status: str
    problems: list[str]


class CarList(BaseModel):
    cars: list[Car]


class MessageBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    body: str
    task_id: int


class MessageCreate(MessageBase):
    pass


class MessageUpdate(MessageBase):
    pass


class Message(MessageBase):
    id: int
    created_at: datetime


class MessageList(BaseModel):
    messages: list[Message]


class TaskStatuses(enum.StrEnum):
    completed = "completed"
    failed = "failed"
    in_progress = "in progress"


class TaskBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    car_id: str
    status: TaskStatuses


class TaskCreate(TaskBase):
    status: TaskStatuses = TaskStatuses.in_progress


class TaskUpdate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    messages: list[Message]


class TaskList(BaseModel):
    tasks: list[Task]
