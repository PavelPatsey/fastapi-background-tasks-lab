import sqlalchemy

from app import models, schemas


def create_message(
    body: str, task_id: int, session: sqlalchemy.orm.Session
) -> models.Message:
    msg_in = schemas.MessageCreate(body=body, task_id=task_id)
    data = msg_in.model_dump()
    body = models.Message(**data)
    session.add(body)
    session.commit()
    session.refresh(body)
    return body
