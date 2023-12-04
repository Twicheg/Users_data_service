from datetime import datetime
from typing import Union

from pydantic import BaseModel


class CurrentUser(BaseModel):
    first_name: str
    last_name: str
    other_name: str | None
    email: str
    phone: str | None
    birthday: datetime | None
    is_admin: bool

    class Config:
        orm_mode = True


class PrivateCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    is_admin: bool

    class Config:
        orm_mode = True


class AfterCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    is_admin: bool

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    pass


class LoginModel(BaseModel):
    email: str
    hashed_password: str

