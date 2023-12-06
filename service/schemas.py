from datetime import datetime
from typing import Union

from pydantic import BaseModel


class CurrentUserResponseModel(BaseModel):
    first_name: str
    last_name: str
    other_name: str | None
    email: str
    phone: str | None
    birthday: datetime | None
    is_admin: bool

    class Config:
        orm_mode = True


class PrivateCreateUserModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    is_admin: bool

    class Config:
        orm_mode = True


class PrivateDetailUserResponseModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    other_name: str | None
    email: str
    phone: str | None
    birthday: datetime | None
    city: str | None
    additional_info: str | None
    is_admin: bool

    class Config:
        orm_mode = True


class UsersListResponseModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


class UsersListElementModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


class PaginatedMetaDataModel(BaseModel):
    total: int
    page: int
    size: int
#

class CitiesHintModel(BaseModel):

    name: str


class PrivateUsersListHintMetaModel(BaseModel):
    pass
    #city: CitiesHintModel


class PrivateUsersListMetaDataModel(BaseModel):
    pagination: PaginatedMetaDataModel
    hint: PrivateUsersListHintMetaModel


class PrivateUsersListResponseModel(BaseModel):
    #data: {UsersListElementModel}
    meta: PrivateUsersListMetaDataModel


class UserUpdate(BaseModel):
    pass


class LoginModel(BaseModel):
    email: str
    password: str


class ErrorResponseModel(BaseModel):
    code: int = 400
    message: str


class CodelessErrorResponseModel(BaseModel):
    message: str
