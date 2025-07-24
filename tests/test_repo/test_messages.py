import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import models, schemas
from app.repo import create_message, create_task, create_task_model


def test_message_schema():
    body = {"msg": "test message"}
    task_id = 1
    message = schemas.MessageCreate(body=body, task_id=task_id)
    assert isinstance(message, schemas.MessageCreate)
    assert hasattr(message, "body")
    assert hasattr(message, "task_id")
    assert message.model_dump() == {"body": {"msg": "test message"}, "task_id": 1}


def test_create_message_model_invalid_task_id():
    body = {"msg": "test message"}
    task_id = "string"

    with pytest.raises(ValidationError) as exc_info:
        schemas.MessageCreate(body=body, task_id=task_id)

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("task_id",)
    assert errors[0]["type"] == "int_parsing"
    assert (
        errors[0]["msg"]
        == "Input should be a valid integer, unable to parse string as an integer"
    )


def test_create_message(session: Session):
    name = "test task name"
    car_id = "test car id"
    task_in = create_task_model(name, car_id)
    task = create_task(task=task_in, session=session)

    body = {"msg": "test message for create"}
    task_id = task.id
    message = create_message(body=body, task_id=task_id, session=session)

    assert isinstance(message, models.Message)
    assert hasattr(message, "id")
    assert hasattr(message, "body")
    assert hasattr(message, "task_id")
    assert hasattr(message, "task")
    assert message.id == 1
    assert message.body == body
    assert message.task_id == task_id
    assert message.task == task
