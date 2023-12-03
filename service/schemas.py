from datetime import datetime

from pydantic import BaseModel
from fastapi_users import schemas


class CurrentUserResponseModel(schemas.BaseUser[int]):
    first_name: str
    last_name: str
    other_name: str|None
    email: str
    phone: str|None
    birthday: datetime|None
    is_admin: bool

    class Config:
        orm_mode = True


class PrivateCreateUserModel(schemas.BaseUserCreate):
    first_name: str
    last_name: str
    email: str
    password: str
    is_admin: bool

    class Config:
        orm_mode = True


class UserUpdate(schemas.BaseUserUpdate):
    pass


class LoginModel(BaseModel):
    login: str
    password: str
