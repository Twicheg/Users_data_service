from typing import Any
# from fastapi.exceptions import HTTPException, RequestErrorModel
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from typing_extensions import Annotated
from fastapi import FastAPI, Response, Depends, Header, Request, HTTPException, Path, Query
from service.database import SessionLocal
from service.schemas import LoginModel, PrivateCreateUserModel, CurrentUserResponseModel, \
    PrivateDetailUserResponseModel, ErrorResponseModel, \
    CodelessErrorResponseModel, UsersListResponseModel, PrivateUsersListResponseModel, CitiesHintModel, \
    UsersListElementModel
from service.services import get_db, password_hash, \
    token_generator, get_current_user, get_arg, my_oauth2_scheme, get_user, paginator
from fastapi.responses import JSONResponse, RedirectResponse
from service.models import User, City

app = FastAPI()


@app.post("/login",
          tags=["auth"],
          summary='Вход в систему',
          response_model=CurrentUserResponseModel,
          )
async def login(response: Response, user: LoginModel, db: SessionLocal = Depends(get_db)):
    email = user.email
    password = user.password
    response.set_cookie(key="Bearer",
                        value=f"{token_generator(email, password)}",
                        httponly=True)
    user_from_db = get_current_user(email, db)
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
    user_from_db = get_current_user(commons.get("current_user_email"), commons.get("db"))
    return user_from_db


@app.patch("/users/current",
           tags=['user'])
async def edit_user(commons: Annotated[Any, Depends(get_arg)]):
    pass


@app.get("/users",
         tags=['user'],
         response_model=list[UsersListResponseModel],
         responses={
             400: {"model": ErrorResponseModel, "description": "Bad Request"},
             401: {"model": CodelessErrorResponseModel, "description": "Unauthorized"},
         }
         )
async def users(commons: Annotated[Any, Depends(get_arg)],
                page: int = Query(ge=1, default=1, title="Page"),
                size: int = Query(ge=1, le=100, title="Size")):
    query = await paginator(page, size, commons.get("db"))
    return query


@app.get("/private/users",
         tags=['admin'],
         response_model=list[PrivateUsersListResponseModel],
         responses={
             400: {"model": ErrorResponseModel, "description": "Bad Request"},
             401: {"model": CodelessErrorResponseModel, "description": "Unauthorized"},
         }
         )
async def private_users(commons: Annotated[Any, Depends(get_arg)],
                        page: int = Query(ge=1, default=1, title="Page"),
                        size: int = Query(ge=1, le=100, title="Size"), ):
    query = await paginator(page, size, commons.get("db"), convert_to_private_users=True)
    return query


@app.post("/private/users",

          tags=['admin'],
          response_model=PrivateDetailUserResponseModel,
          responses={
              400: {"model": ErrorResponseModel, "description": "Bad Request"},
              401: {"model": CodelessErrorResponseModel, "description": "Unauthorized"},
              403: {"model": CodelessErrorResponseModel, "description": "Forbidden"}, })
async def private_create_user(user: PrivateCreateUserModel, commons: Annotated[Any, Depends(get_arg)]):
    user_dict = user.dict()
    db = commons.get("db")
    get_current_user(commons.get("current_user_email"), db, check_perm=True)
    user_dict['hashed_password'] = await password_hash(user_dict.pop('password'))
    response = commons.get("response")
    response.status_code = 201
    user = User(**user_dict)
    db.add(user)
    db.commit()
    user = db.query(User).filter(User.email == user_dict.get("email")).first()
    return user


@app.get("/private/users/{pk}",
         tags=['admin'],
         )
async def private_get_user(pk: int, commons: Annotated[Any, Depends(get_arg)]):
    db = commons.get("db")
    get_current_user(commons.get("current_user_email"), db, check_perm=True)
    return get_user(pk, db)


@app.delete("/private/users/{pk}",
            tags=['admin'])
async def private_delete_user(pk: int, commons: Annotated[Any, Depends(get_arg)]):
    db = commons.get("db")
    get_current_user(commons.get("current_user_email"), db, check_perm=True)
    db.delete(get_user(pk, db))
    db.commit()
    return {"msg": "Successfully delete"}


@app.patch("/private/users/{pk}",
           tags=['admin']
           )
async def private_patch_user(pk: int, changes):
    pass


@app.post("/city")
def create_city(city: CitiesHintModel, db: SessionLocal = Depends(get_db)):
    city = City(**city.dict())
    db.add(city)
    db.commit()
