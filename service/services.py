import os
from datetime import datetime, timedelta, time
from typing import Any, Dict, List, Optional, Union, cast, Annotated
from service.manager import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from fastapi.param_functions import Form
from service.database import SessionLocal
from fastapi import Response, HTTPException, FastAPI, Response, Depends, Header, Request
from passlib.context import CryptContext
from service.users import User
from starlette.requests import Request
from fastapi.security.utils import get_authorization_scheme_param
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))
my_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="Token")


def token_generator(email, password):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"sub": email, "pas": password}
    expire = datetime.utcnow().replace(tzinfo=None) + access_token_expires
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_arg(response: Response = None, request: Request = None, db: SessionLocal = Depends(get_db),
                  JWT: Annotated[str, Depends(my_oauth2_scheme)] = None):
    return {"response": response, "db": db, "request": request, "user_JWT": JWT}


async def get_current_user(User_or_JWT: dict or str, db) -> User:
    match type(User_or_JWT).__name__:
        case str.__name__:
            user = jwt.decode(User_or_JWT, key=SECRET_KEY)
            user = db.query(User).filter(User.email == user.get("sub")).first()
            return user
        case dict.__name__:
            user = db.query(User).filter(User.email == User_or_JWT.get("email")).first()
            return user


async def check_email(user, db):
    email = user.get("email")
    if len({"@", "."}.intersection(set(email))) < 2:
        raise HTTPException(status_code=400, detail="Enter valid email")
    if 'mail' not in email:
        raise HTTPException(status_code=400, detail="Enter valid email")
    if email.find("@") < 4:
        raise HTTPException(status_code=400, detail="Enter valid email")
    if user.get("email") in [i.email for i in db.query(User).all()]:
        raise HTTPException(status_code=400, detail="Email already used")


async def password_hash(password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


async def check_email_with_password(user, db: SessionLocal = Depends(get_db)):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    for i in db.query(User).all():
        if user.email == i.email and pwd_context.verify(user.password, i.hashed_password):
            return 0
    raise HTTPException(status_code=401, detail="Bad username or password")



