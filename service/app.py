from typing import Any

from fastapi.exceptions import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from typing_extensions import Annotated
from fastapi import FastAPI, Response, Depends, Header, Request
from fastapi.encoders import jsonable_encoder
from service.database import SessionLocal
from service.schemas import LoginModel, PrivateCreate, CurrentUser, AfterCreate
from service.services import get_db, check_email, password_hash, check_email_with_password, \
    token_generator, get_current_user, get_arg
from fastapi.responses import JSONResponse, RedirectResponse
from service.services import my_oauth2_scheme
from service.users import User

app = FastAPI()


@app.post("/login",
          tags=["auth"],
          description="После успешного входа в систему необходимо установить Cookies для пользователя",
          summary='Вход в систему'
          )
async def login(response: Response, user: LoginModel, db: SessionLocal = Depends(get_db), ):
    check_email_with_password(user, db)
    response.set_cookie(key="Bearer",
                        value=f"{token_generator(user.email, user.password)}",
                        httponly=True)
    return {"msg": "Successfully login"}


@app.get("/logout",
         tags=['auth'],
         summary='Выход из системы')
async def logout(commons: Annotated[Any, Depends(get_arg)]):
    commons.get("response").delete_cookie(key="Bearer")
    return {"msg": "Successfully logout"}


@app.get("/users/current",
         tags=['user'],
         response_model=CurrentUser,
         responses={
             403:{"model":CurrentUser},
             401:{"model":CurrentUser}
         }
         )
async def current_user(commons: Annotated[Any, Depends(get_arg)]):
    try:
        user_from_db = await get_current_user(commons.get("user_JWT"), commons.get("db"))
    except Exception as e:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Session over , please re-login")
    return user_from_db


@app.patch("/users/current",
           tags=['user'])
async def edit_user():
    pass


@app.get("/users",
         tags=['user'],
         )
async def users(commons: Annotated[Any, Depends(get_arg)]):
    pass



@app.get("/private/users",
         tags=['admin'],
         )
async def private_users():
    pass


@app.post("/private/users",
          tags=['admin'],
          response_model=AfterCreate)
async def private_create_user(user: PrivateCreate, db: SessionLocal = Depends(get_db)):
    user_dict = user.dict()
    check_email(user_dict, db=db)
    password = user_dict.pop('password')
    user_dict['hashed_password'] = password_hash(password)
    user = User(**user_dict)
    db.add(User(**user_dict))
    db.commit()
    return user


@app.get("/private/users/{pk}",
         tags=['admin'],
         )
async def private_get_user(pk: int):
    pass


@app.delete("/private/users/{pk}",
            tags=['admin'])
async def private_delete_user(pk: int):
    pass


@app.patch("/private/users/{pk}",
           tags=['admin'])
async def private_patch_user(pk: int):
    pass
