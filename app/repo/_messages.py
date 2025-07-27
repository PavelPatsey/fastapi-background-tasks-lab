from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas


async def create_message(
    body: str, task_id: int, session: AsyncSession
) -> models.Message:
    msg_in = schemas.MessageCreate(body=body, task_id=task_id)
    data = msg_in.model_dump()
    message = models.Message(**data)
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message
