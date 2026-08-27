from sqlalchemy import Column,Integer,String
from .database import Base
from sqlalchemy import ForeignKey

class User(Base):
    __tablename__="users"

    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,unique=True)
    email = Column(String,unique=True)
    password = Column(String)
    role = Column(String,default="user")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )