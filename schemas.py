import enum

from pydantic import BaseModel, ConfigDict


class Car(BaseModel):
    car_id: str
    status: str
    problems: list[str]


class CarList(BaseModel):
    cars: list[Car]


class CheckCar(BaseModel):
    car_id: str
    task_id: int
    message: str


class SendForRepairCar(BaseModel):
    car_id: str
    task_id: int
    message: str


class SendToParkingCar(BaseModel):
    car_id: str
    task_id: int
    message: str


class MessageBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    body: dict
    task_id: int


class MessageCreate(MessageBase):
    pass


class MessageUpdate(MessageBase):
    pass


class Message(MessageBase):
    id: int


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
    messages: list[Message] = []


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class Task(TaskBase):
    id: int


class TaskList(BaseModel):
    tasks: list[Task]
