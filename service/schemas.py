from datetime import date
from fastapi import HTTPException
from pydantic import BaseModel, field_validator, model_validator
from service.models import User, City
from service.services import get_db
from passlib.context import CryptContext

from typing import Annotated


class CurrentUserResponseModel(BaseModel):

    first_name: str
    last_name: str
    other_name: str
    email: str
    phone: str
    birthday: Annotated[date, str]
    is_admin: bool


class PrivateCreateUserModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    is_admin: bool
    city: int = 1
    other_name: str = "not specified"
    phone: str = "not specified"
    birthday: Annotated[date, str] = date.fromisoformat("2000-01-01")
    additional_info: str = "not specified"

    @field_validator("email")
    def check_first_name(cls, email):
        if len({"@", "."}.intersection(set(email))) < 2:
            raise HTTPException(status_code=400, detail="Enter valid email")
        if 'mail' not in email:
            raise HTTPException(status_code=400, detail="Enter valid email")
        if email.find("@") < 4:
            raise HTTPException(status_code=400, detail="Enter valid email")
        if email in [i.email for i in next(get_db()).query(User).all()]:
            raise HTTPException(status_code=400, detail="Email already used")
        return email

    @field_validator("city")
    def check_cities_name(cls, city):
        if city not in [i.id for i in next(get_db()).query(City).all()]:
            raise HTTPException(status_code=400, detail="Enter valid city")
        return city

    @field_validator("password")
    def check_password(cls, password):
        if len(password) < 5:
            raise HTTPException(status_code=400, detail="Enter valid password")
        return password


class PrivateDetailUserResponseModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    other_name: str
    email: str
    phone: str
    birthday: Annotated[date, str]
    city: int
    additional_info: str
    is_admin: bool


class PaginatedMetaDataModel(BaseModel):
    total: int
    page: int
    size: int


class CitiesHintModel(BaseModel):
    id: int
    name: str


class PrivateUsersListHintMetaModel(BaseModel):
    city: list[CitiesHintModel]


class PrivateUsersListMetaDataModel(BaseModel):
    pagination: PaginatedMetaDataModel
    hint: PrivateUsersListHintMetaModel


class UsersListElementModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


class PrivateUsersListResponseModel(BaseModel):
    meta: PrivateUsersListMetaDataModel
    data: list[UsersListElementModel]


class LoginModel(BaseModel):
    email: str
    password: str

    @model_validator(mode="before")
    def check_email_with_password(cls, value) -> None:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        for i in next(get_db()).query(User).all():
            if value.get("email") == i.email and pwd_context.verify(value.get("password"), i.hashed_password):
                return value
        raise HTTPException(status_code=401, detail="Bad email or password")


class ErrorResponseModel(BaseModel):
    code: int
    message: str


class UpdateUserModel(BaseModel):
    first_name: str = "not specified"
    last_name: str = "not specified"
    other_name: str = "not specified"
    email: str = "not specified"
    phone: str = "not specified"
    birthday: Annotated[date, str] = date.fromisoformat("2000-01-01")

    @field_validator("first_name", mode="before")
    def check_first_name(cls, first_name):
        print(first_name)
        if len(first_name) < 3:
            raise HTTPException(status_code=400, detail="Enter valid first name")
        return first_name

    @field_validator("email")
    def check_email(cls, email):
        if len({"@", "."}.intersection(set(email))) < 2:
            raise HTTPException(status_code=400, detail="Enter valid email")
        if 'mail' not in email:
            raise HTTPException(status_code=400, detail="Enter valid email")
        if email.find("@") < 4:
            raise HTTPException(status_code=400, detail="Enter valid email")
        if email in [i.email for i in next(get_db()).query(User).all()]:
            raise HTTPException(status_code=400, detail="Email already used")
        return email


class UsersListMetaDataModel(BaseModel):
    pagination: PaginatedMetaDataModel


class UsersListResponseModel(BaseModel):
    meta: UsersListMetaDataModel
    data: list[UsersListElementModel]


class PrivateUpdateUserModel(BaseModel):
    id: int
    first_name: str = None
    last_name: str = None
    other_name: str = None
    email: str = None
    phone: str = None
    birthday: Annotated[date, str] = date.fromisoformat("2000-01-01")
    city: int = None
    additional_info: str = None
    is_admin: bool = None


class UpdateUserResponseModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    other_name: str
    email: str
    phone: str
    birthday: Annotated[date, str]


class CodelessErrorResponseModel(BaseModel):
    message: str
