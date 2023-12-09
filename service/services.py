import os
import datetime as dt
from typing import Annotated
from service.manager import MyOAuth2PasswordBearer
from jose import jwt
from service.database import SessionLocal
from fastapi import HTTPException, Response, Depends
from passlib.context import CryptContext
from service.models import User, City
from starlette.requests import Request
from fastapi import FastAPI

app = FastAPI()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))
my_oauth2_scheme = MyOAuth2PasswordBearer(tokenUrl="Token")


def token_generator(email: str, password: str) -> str:
    access_token_expires = dt.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = dt.datetime.now(dt.UTC).replace(tzinfo=None) + access_token_expires
    data = {"sub": email, "pas": password, "exp": expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


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
        raise HTTPException(status_code=403, detail="Session over , please re-login")
    return {"response": response, "db": db, "request": request, "current_user_email": user_email}


def get_current_user(user_email: str, db: SessionLocal, check_perm: bool = False) -> User:
    user = db.query(User).filter(User.email == user_email).first()
    if check_perm and not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


def get_user(user_id: int, db: SessionLocal) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return user


async def password_hash(password: str) -> str:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def paginator(page: int, size: int, db: SessionLocal, convert_to_: str = "") -> dict:
    page -= 1
    query_users = db.query(User).all()
    query_return = [i for i in query_users[page * size:page * size + size]]
    total = len(query_users)

    if convert_to_ == "users":
        object_to_return = {"meta": {"pagination": {"total": total, "page": page + 1, "size": size}},
                            "data": []}
        for user in query_return:
            object_to_return["data"].append(
                {"id": user.id, "first_name": user.first_name, "last_name": user.last_name, "email": user.email})
        return object_to_return

    if convert_to_ == "private":
        object_to_return = {"meta": {"pagination": {"total": total, "page": page + 1, "size": size},
                                     "hint": {"city": []}},
                            "data": []}
        for user in query_return:
            city = db.get(City, user.city)
            object_to_return["data"].append(
                {"id": user.id, "first_name": user.first_name, "last_name": user.last_name, "email": user.email})
            if {"id": user.city, "name": city.name} in object_to_return["meta"]["hint"]["city"]:
                continue
            object_to_return["meta"]["hint"]["city"].append({"id": user.city, "name": city.name})
        return object_to_return


