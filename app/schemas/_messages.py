from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MessageBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    body: str
    task_id: int


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    id: int
    created_at: datetime


class MessageList(BaseModel):
    messages: list[Message]
