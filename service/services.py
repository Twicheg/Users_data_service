import os
from datetime import datetime, timedelta, time
from typing import Annotated
from service.manager import MyOAuth2PasswordBearer
from jose import jwt
from service.database import SessionLocal
from fastapi import HTTPException, Response, Depends
from passlib.context import CryptContext
from service.models import User, City
from starlette.requests import Request

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))
my_oauth2_scheme = MyOAuth2PasswordBearer(tokenUrl="Token")


def token_generator(email: str, password: str) -> str:
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow().replace(tzinfo=None) + access_token_expires
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


async def password_hash(password: str) -> str:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


async def paginator(page: int, size: int, db: SessionLocal, convert_to_private_users: bool = False) -> list[User]:
    page -= 1
    match page, size:
        case i, j if i < 0 or j < 1:
            raise HTTPException(status_code=400, detail="Bad request")
    query_users = db.query(User).all()
    query_return = [i for i in query_users[page * size:page * size + size]]
    if convert_to_private_users:
        total = len(query_users)
        for user in query_return:
            if user.city:
                city = db.query(City).get(user.city)
            else:
                city = None
            city = city if city else None
            user.data = {"id": user.id, "first_name": user.first_name, "last_name": user.last_name, "email": user.email}
            user.meta = {"pagination": {"total": total, "page": page + 1, "size": size},
                         "hint": {"city": {"id": user.city, "name": city}}}
    return query_return
