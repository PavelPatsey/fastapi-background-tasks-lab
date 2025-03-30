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


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    name: str
    car_id: str
    status: str
    messages: list = []


class TaskList(BaseModel):
    tasks: list[Task]
