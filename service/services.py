import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, cast, Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from fastapi.param_functions import Form
from service.database import SessionLocal
from fastapi import Response, HTTPException
from passlib.context import CryptContext
from service.users import User
from starlette.requests import Request
from fastapi.security.utils import get_authorization_scheme_param
from starlette.status import HTTP_401_UNAUTHORIZED

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))


def token_generator(email, password):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"sub": email}
    expire = datetime.utcnow() + access_token_expires
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(JWT, db):
    user = jwt.decode(JWT, key=SECRET_KEY)
    user = db.query(User).filter(User.email == user.get("sub")).first()
    return user


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_email(user, db):
    if user.get("email") in [i.email for i in db.query(User).all()]:
        raise HTTPException(status_code=400, detail="Email already used")


def password_hash(password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def check_email_with_password(user, db):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    for i in db.query(User).all():
        if user.username == i.email and pwd_context.verify(user.password, i.hashed_password):
            return 0
    raise HTTPException(status_code=401, detail="Bad username or password")


class MyOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
    def __init__(
            self,
            email: Annotated[str, Form()] = None,
            password: Annotated[str, Form()] = None,
    ):
        super().__init__(
            username=email,
            password=password,
        )


class MyOAuth2PasswordBearer(OAuth2PasswordBearer):
    def __init__(self, tokenUrl):
        super().__init__(tokenUrl)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Cookie")
        if authorization:
            authorization = authorization.replace('=', ' ')
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != ("bearer"):
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


my_oauth2_scheme = MyOAuth2PasswordBearer(tokenUrl="Token")
