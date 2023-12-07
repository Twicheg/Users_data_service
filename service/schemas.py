from datetime import datetime
from fastapi import HTTPException
from pydantic import BaseModel, validator, root_validator
from service.models import User
from service.services import get_db
from passlib.context import CryptContext


class MyBaseModel(BaseModel):
    class Config:
        orm_mode = True


class CurrentUserResponseModel(MyBaseModel):
    first_name: str
    last_name: str
    other_name: str | None
    email: str
    phone: str | None
    birthday: datetime | None
    is_admin: bool
    city: int | None
    additional_info: str | None

    class Config:
        orm_mode = True


class PrivateCreateUserModel(MyBaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    is_admin: bool
    city: int

    @validator("email")
    def first_name(cls, email):
        if len({"@", "."}.intersection(set(email))) < 2:
            raise HTTPException(status_code=400, detail="Enter valid email")
        if 'mail' not in email:
            raise HTTPException(status_code=400, detail="Enter valid email")
        if email.find("@") < 4:
            raise HTTPException(status_code=400, detail="Enter valid email")
        if email in [i.email for i in next(get_db()).query(User).all()]:
            raise HTTPException(status_code=400, detail="Email already used")
        return email

    @validator("password")
    def password(cls, password):
        if len(password) < 5:
            raise HTTPException(status_code=400, detail="Enter valid password")
        return password


class PrivateDetailUserResponseModel(MyBaseModel):
    id: int
    first_name: str
    last_name: str
    other_name: str | None
    email: str
    phone: str | None
    birthday: datetime | None
    city: int | None
    additional_info: str | None
    is_admin: bool


class UsersListResponseModel(MyBaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


class PaginatedMetaDataModel(MyBaseModel):
    total: int
    page: int
    size: int


class CitiesHintModel(MyBaseModel):
    id: int | None
    name: str | None


class PrivateUsersListHintMetaModel(MyBaseModel):
    city: CitiesHintModel


class PrivateUsersListMetaDataModel(MyBaseModel):
    pagination: PaginatedMetaDataModel
    hint: PrivateUsersListHintMetaModel


class UsersListElementModel(MyBaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


class PrivateUsersListResponseModel(MyBaseModel):
    data: UsersListElementModel
    meta: PrivateUsersListMetaDataModel

    class Config:
        orm_mode = False


class LoginModel(MyBaseModel):
    email: str
    password: str

    @root_validator(skip_on_failure=True)
    def check_email_with_password(cls, value) -> None:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        for i in next(get_db()).query(User).all():
            if value.get("email") == i.email and pwd_context.verify(value.get("password"), i.hashed_password):
                return value
        raise HTTPException(status_code=401, detail="Bad username or password")


class ErrorResponseModel(MyBaseModel):
    code: int = 400
    message: str


class UserUpdate(MyBaseModel):
    first_name: str
    last_name: str
    other_name: str
    email: str
    phone: str | None = None
    birthday: datetime | None = None


class UpdateUserResponseModel(MyBaseModel):
    first_name: str
    last_name: str
    other_name: str
    email: str
    phone: str
    birthday: datetime


class CodelessErrorResponseModel(MyBaseModel):
    message: str
