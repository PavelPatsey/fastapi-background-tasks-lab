import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import models, schemas
from app.repo import create_task, create_task_model


def test_create_task_model():
    name = "test task name"
    car_id = "test car id"
    task = create_task_model(name, car_id)
    assert isinstance(task, schemas.TaskCreate)
    assert task.model_dump() == {
        "name": "test task name",
        "car_id": "test car id",
        "status": "in progress",
        "messages": [],
    }


def test_create_task_model_invalid_car_id():
    name = "test task name"
    car_id = 1

    with pytest.raises(ValidationError) as exc_info:
        create_task_model(name, car_id)

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("car_id",)
    assert errors[0]["type"] == "string_type"
    assert errors[0]["msg"] == "Input should be a valid string"


def test_create_task(session: Session):
    name = "test task name"
    car_id = "test car id"
    task_in = create_task_model(name, car_id)

    task = create_task(task=task_in, session=session)
    assert isinstance(task, models.Task)
    assert hasattr(task, "id")
    assert hasattr(task, "name")
    assert hasattr(task, "car_id")
    assert hasattr(task, "status")
    assert hasattr(task, "messages")
    assert task.id == 1
    assert task.name == name
    assert task.car_id == car_id
    assert task.status == "in progress"
    assert task.messages == []
