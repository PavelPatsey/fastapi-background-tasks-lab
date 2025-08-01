from pydantic import BaseModel


class Car(BaseModel):
    car_id: str
    status: str
    problems: list[str]


class CarList(BaseModel):
    cars: list[Car]
