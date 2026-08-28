from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

#user request reponse
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role:str

#to show only necessary details
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: Optional[str] = None

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str
    description: str

#task response schema
class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    user_id: int
    status: str

    class Config:
        from_attributes = True

    #update
class TaskUpdate(BaseModel):
    title: str
    description: str
    status: str