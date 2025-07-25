import enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ._messages import Message


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


# todo: use it in repo
class TaskUpdate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    messages: list[Message]


class TaskList(BaseModel):
    tasks: list[Task]
