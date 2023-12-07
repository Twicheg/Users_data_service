import os
from datetime import datetime, timedelta, time
from typing import Any, Dict, List, Optional, Union, cast, Annotated
from service.manager import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from fastapi.param_functions import Form
from service.database import SessionLocal
from fastapi import Response, HTTPException, FastAPI, Response, Depends, Header, Request
from passlib.context import CryptContext
from service.models import User, City
from starlette.requests import Request
from fastapi.security.utils import get_authorization_scheme_param
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))
my_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="Token")


def token_generator(email: str, password: str) -> str:
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"sub": email, "pas": password}
    expire = datetime.utcnow().replace(tzinfo=None) + access_token_expires
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_db() -> SessionLocal:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_arg(response: Response = None, request: Request = None, db: SessionLocal = Depends(get_db),
            JWT: Annotated[str, Depends(my_oauth2_scheme)] = None) -> dict:
    try:
        user_email = jwt.decode(JWT, key=SECRET_KEY).get("sub")
    except Exception:
        raise HTTPException(status_code=404, detail="Session over , please re-login")
    return {"response": response, "db": db, "request": request, "current_user_email": user_email}


def get_current_user(user_email: str, db: SessionLocal, check_perm: bool = False) -> User:
    user = db.query(User).filter(User.email == user_email).first()
    if check_perm and not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


def get_user(user_id: int, db: SessionLocal) -> User:
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return user


def user_create_validation(user_dict: dict, db: SessionLocal) -> None:
    password = user_dict.get("password")
    email = user_dict.get("email")
    if len(password) < 5:
        raise HTTPException(status_code=400, detail="Enter valid password")
    if len({"@", "."}.intersection(set(email))) < 2:
        raise HTTPException(status_code=400, detail="Enter valid email")
    if 'mail' not in email:
        raise HTTPException(status_code=400, detail="Enter valid email")
    if email.find("@") < 4:
        raise HTTPException(status_code=400, detail="Enter valid email")
    if email in [i.email for i in db.query(User).all()]:
        raise HTTPException(status_code=400, detail="Email already used")


async def password_hash(password: str) -> str:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def check_email_with_password(email: str, password: str, db: SessionLocal) -> None:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    for i in db.query(User).all():
        if email == i.email and pwd_context.verify(password, i.hashed_password):
            return 0
    raise HTTPException(status_code=401, detail="Bad username or password")


def paginator(page, size, db, convert_to_private_users=False):
    page -= 1
    query_users = db.query(User).all()
    city = db.query(City)
    list_to_return = [i for i in query_users[page * size:page * size + size]]
    if convert_to_private_users:
        total = len(query_users)
        for i in list_to_return:
            i.data = {"id": i.id, "first_name": i.first_name, "last_name": i.last_name, "email": i.email}
            i.meta = {"pagination": {"total": total, "page": page + 1, "size": size},
                      "hint": {"city": {"id": i.city, "name": city.get(i.city).name if city.get(i.city) else None}}}
    return list_to_return
