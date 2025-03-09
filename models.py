from sqlmodel import Field, SQLModel


class TaskBase(SQLModel):
    name: str = ""
    car_id: str
    status: str = ""
    extra_info: str = ""


class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class TaskPublic(TaskBase):
    id: int


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass
