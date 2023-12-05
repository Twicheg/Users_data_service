from typing import Any
# from fastapi.exceptions import HTTPException, RequestErrorModel
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from typing_extensions import Annotated
from fastapi import FastAPI, Response, Depends, Header, Request, HTTPException
from service.database import SessionLocal
from service.schemas import LoginModel, PrivateCreateUserModel, CurrentUserResponseModel, \
    PrivateDetailUserResponseModel, ErrorResponseModel, \
    CodelessErrorResponseModel
from service.services import get_db, check_email, password_hash, check_email_with_password, \
    token_generator, get_current_user, get_arg
from fastapi.responses import JSONResponse, RedirectResponse
from service.users import User

app = FastAPI()


@app.post("/login",
          tags=["auth"],
          summary='Вход в систему',
          response_model=CurrentUserResponseModel,
          )
async def login(response: Response, user: LoginModel, db: SessionLocal = Depends(get_db)):
    check_email_with_password(user, db)
    response.set_cookie(key="Bearer",
                        value=f"{token_generator(user.email, user.password)}",
                        httponly=True)
    user_from_db = await get_current_user(user.dict(), db)
    return user_from_db


@app.get("/logout",
         tags=['auth'],
         summary='Выход из системы')
async def logout(commons: Annotated[Any, Depends(get_arg)]):
    commons.get("response").delete_cookie(key="Bearer")
    return {"msg": "Successfully logout"}


@app.get("/users/current",
         tags=['user'],
         response_model=CurrentUserResponseModel,
         responses={
             401: {"model": CodelessErrorResponseModel, "description": "Unauthorized"},
             400: {"model": ErrorResponseModel, "description": "Bad Request"}
         },
         )
async def current_user(commons: Annotated[Any, Depends(get_arg)]):
    try:
        user_from_db = await get_current_user(commons.get("user_JWT"), commons.get("db"))
    except Exception:
        raise HTTPException(status_code=404, detail="Session over , please re-login")
    return user_from_db


@app.patch("/users/current",
           tags=['user'])
async def edit_user(commons: Annotated[Any, Depends(get_arg)]):
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


from fastapi.encoders import jsonable_encoder


@app.post("/private/users",
          tags=['admin'],
          response_model=PrivateDetailUserResponseModel,
          responses={
              400: {"model": ErrorResponseModel, "description": "Bad Request"},
              401: {"model": CodelessErrorResponseModel, "description": "Unauthorized"},
              403: {"model": CodelessErrorResponseModel, "description": "Forbidden"},
          })
async def private_create_user(user: PrivateCreateUserModel, commons: Annotated[Any, Depends(get_arg)]):
    user_dict = user.dict()
    db = commons.get("db")
    perm = await get_current_user(commons.get("user_JWT"), db)
    if not perm.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    response = commons.get("response")
    await check_email(user_dict, db)
    user_dict['hashed_password'] = password_hash(user_dict.pop('password'))
    user = User(**user_dict)
    db.add(user)
    db.commit()
    user = db.query(User).filter(User.email == user_dict.get("email")).first()
    response.status_code = 201
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
