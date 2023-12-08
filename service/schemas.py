from datetime import datetime
from fastapi import HTTPException
from pydantic import BaseModel, field_validator, model_validator, Extra
from service.models import User
from service.services import get_db
from passlib.context import CryptContext


class CurrentUserResponseModel(BaseModel):
    first_name: str
    last_name: str
    other_name: str | None
    email: str
    phone: str | None
    birthday: datetime | None
    is_admin: bool
    city: int | None
    additional_info: str | None


class PrivateCreateUserModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    is_admin: bool
    city: int

    @field_validator("email")
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

    @field_validator("password")
    def password(cls, password):
        if len(password) < 5:
            raise HTTPException(status_code=400, detail="Enter valid password")
        return password


class PrivateDetailUserResponseModel(BaseModel):
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


class UsersListResponseModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


class PaginatedMetaDataModel(BaseModel):
    total: int
    page: int
    size: int


class CitiesHintModel(BaseModel):
    id: int | None
    name: str | None


class PrivateUsersListHintMetaModel(BaseModel):
    city: CitiesHintModel


class PrivateUsersListMetaDataModel(BaseModel):
    pagination: PaginatedMetaDataModel
    hint: PrivateUsersListHintMetaModel


class UsersListElementModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


class PrivateUsersListResponseModel(BaseModel):
    data: UsersListElementModel
    meta: PrivateUsersListMetaDataModel


class LoginModel(BaseModel):
    email: str
    password: str

    @model_validator(mode="before")
    def check_email_with_password(cls, value) -> None:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        for i in next(get_db()).query(User).all():
            if value.get("email") == i.email and pwd_context.verify(value.get("password"), i.hashed_password):
                return value
        raise HTTPException(status_code=401, detail="Bad username or password")


class ErrorResponseModel(BaseModel):
    code: int = 400
    message: str


class UserUpdate(BaseModel):
    first_name: str | None
    last_name: str | None
    other_name: str | None
    email: str | None
    phone: str | None
    birthday: datetime | None


class UpdateUserResponseModel(BaseModel):
    first_name: str
    last_name: str
    other_name: str
    email: str
    phone: str
    birthday: datetime


class CodelessErrorResponseModel(BaseModel):
    message: str
