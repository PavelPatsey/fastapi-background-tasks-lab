from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    car_id = Column(String)
    status = Column(String)
    extra_info = Column(JSON, default=[])
