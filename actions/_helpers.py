from datetime import datetime


class CarActionsError(Exception):
    pass


def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
