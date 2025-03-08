from pydantic import BaseModel


class Car(BaseModel):
    car_id: str
    status: str
    problems: list[str]


class CarList(BaseModel):
    cars: list[Car]


class CheckCar(BaseModel):
    car_id: str
    result: bool
    message: str


class SendForRepairCar(BaseModel):
    car_id: str
    result: bool
    problems: list[str]
    message: str


class SendToParkingCar(BaseModel):
    car_id: str
    result: bool
    message: str
