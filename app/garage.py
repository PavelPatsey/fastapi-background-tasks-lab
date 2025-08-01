import asyncio
import random

from app.schemas import Car, CarList


class GarageClientError(Exception):
    pass


def _random_with_probability(probability: int) -> bool:
    """
    Probability - the chance in percent (an integer from 0 to 100) with which the function will return True.
    """
    return random.randint(0, 100) <= probability


class GarageClient:
    UPDATE_STATUS_PROBABILITY = 70
    SLEEP_DURATION = 1

    car_db = {
        "car_1": {"car_id": "car_1", "status": "ok", "problems": []},
        "car_2": {"car_id": "car_2", "status": "ok", "problems": []},
        "car_3": {"car_id": "car_3", "status": "ok", "problems": []},
        "car_4": {"car_id": "car_4", "status": "ok", "problems": []},
    }

    async def get_car_list(self) -> CarList:
        await asyncio.sleep(self.SLEEP_DURATION)
        cars = [
            Car(
                car_id=car["car_id"],
                status=car["status"],
                problems=car["problems"],
            )
            for car in self.car_db.values()
        ]
        return CarList(cars=cars)

    async def check(self, car_id: str) -> dict:
        await asyncio.sleep(self.SLEEP_DURATION)
        if car_id in self.car_db:
            return {car_id: True}
        raise GarageClientError(f"Car {car_id} does not exist!")

    async def get_problems(self, car_id: str) -> dict:
        await asyncio.sleep(self.SLEEP_DURATION)
        if car_id in self.car_db:
            car = self.car_db[car_id]
            return {car_id: car["problems"]}
        raise GarageClientError(f"Car {car_id} does not exist!")

    async def add_problem(self, car_id: str, problem: str) -> dict:
        await asyncio.sleep(self.SLEEP_DURATION)
        if car_id in self.car_db:
            car = self.car_db[car_id]
            car["problems"].append(problem)
            return {car_id: car["problems"]}
        raise GarageClientError(f"Car {car_id} does not exist!")

    async def fix_problems(self, car_id: str) -> dict:
        await asyncio.sleep(self.SLEEP_DURATION)
        if car_id in self.car_db:
            car = self.car_db[car_id]
            car["problems"] = []
            return {car_id: car["problems"]}
        raise GarageClientError(f"Car {car_id} does not exist!")

    async def update_status(self, car_id: str) -> dict:
        await asyncio.sleep(self.SLEEP_DURATION)
        if _random_with_probability(self.UPDATE_STATUS_PROBABILITY):
            car = self.car_db[car_id]
            car["status"] = "under repair" if car["problems"] else "ok"
            return {car_id: car["status"]}
        raise GarageClientError(f"Error while updating status of car {car_id}!")
