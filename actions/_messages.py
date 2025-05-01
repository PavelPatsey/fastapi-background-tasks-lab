import sqlalchemy

import models
import schemas

from ._helpers import get_current_time


def _create_message(
    msg: schemas.MessageCreate,
    session: sqlalchemy.orm.Session,
) -> models.Message:
    message_data = msg.model_dump()
    db_msg = models.Message(**message_data)
    session.add(db_msg)
    session.commit()
    session.refresh(db_msg)
    return db_msg


def create_message(
    body: dict,
    task_id: int,
    session: sqlalchemy.orm.Session,
) -> models.Message:
    if not body.get("timestamp"):
        body["timestamp"] = get_current_time()
    msg_model = schemas.MessageCreate(body=body, task_id=task_id)
    db_msg = _create_message(msg_model, session)
    return db_msg
