import random
import time


class GarageClientError(Exception):
    pass


def _random_with_probability(probability: int) -> bool:
    """
    Probability - the chance in percent (an integer from 0 to 100) with which the function will return True.
    """
    return random.randint(0, 100) <= probability


class GarageClient:
    UPDATE_STATUS_PROBABILITY = 70
    SLEEP_DURATION = 3

    def __init__(self):
        self.car_db = {
            "car_1": {"status": "ok", "problems": []},
            "car_2": {"status": "ok", "problems": []},
            "car_3": {"status": "ok", "problems": []},
            "car_4": {"status": "ok", "problems": []},
        }

    def car_list(self):
        return

    def is_exists(self, car_id: str):
        time.sleep(self.SLEEP_DURATION)
        if car_id in self.car_db:
            return {car_id: True}
        raise GarageClientError(f"Car {car_id} does not exist!")

    def get_problems(self, car_id: str):
        time.sleep(self.SLEEP_DURATION)
        if car_id in self.car_db:
            car = self.car_db[car_id]
            return {car_id: True, "problems": car["problems"]}
        raise GarageClientError(f"Car {car_id} does not exist!")

    def add_problem(self, car_id: str, problem: str):
        time.sleep(self.SLEEP_DURATION)
        if car_id in self.car_db:
            car = self.car_db[car_id]
            car["problems"].append(problem)
            return {car_id: True, "problems": car["problems"]}
        raise GarageClientError(f"Car {car_id} does not exist!")

    def fix_problems(self, car_id: str):
        time.sleep(self.SLEEP_DURATION)
        if car_id in self.car_db:
            car = self.car_db[car_id]
            car["problems"] = []
            return {car_id: True, "problems": car["problems"]}
        raise GarageClientError(f"Car {car_id} does not exist!")

    def update_status(self, car_id: str):
        time.sleep(self.SLEEP_DURATION)
        if _random_with_probability(self.UPDATE_STATUS_PROBABILITY):
            car = self.car_db[car_id]
            car["status"] = "under repair" if car["problems"] else "ok"
            return {car_id: True, "status": car["status"]}
        raise GarageClientError(f"Error while updating status of car {car_id}!")
