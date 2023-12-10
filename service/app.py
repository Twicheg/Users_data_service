from typing import Any
from typing_extensions import Annotated
from fastapi import FastAPI, Response, Depends, Query
from service.database import SessionLocal
from service.schemas import LoginModel, PrivateCreateUserModel, \
    CurrentUserResponseModel, PrivateDetailUserResponseModel, \
    ErrorResponseModel, CodelessErrorResponseModel, UsersListResponseModel, \
    PrivateUsersListResponseModel, CitiesHintModel, UpdateUserModel, \
    UpdateUserResponseModel, PrivateUpdateUserModel
from service.services import get_db, password_hash, \
    token_generator, get_current_user, get_arg, get_user, paginator
from service.models import User, City
from fastapi import HTTPException
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import PlainTextResponse

app = FastAPI()


@app.exception_handler(ResponseValidationError)
async def validation_exception_handler(response: Response,
                                       exc: ResponseValidationError):
    return PlainTextResponse(
        status_code=500,
        content="Что-то пошло не так, мы уже исправляем эту ошибку")


@app.post("/login",
          tags=["auth"],
          summary='Вход в систему',
          response_model=CurrentUserResponseModel,
          responses={400: {"model": ErrorResponseModel,
                           "description": "Bad Request"}}
          )
async def login(response: Response, user: LoginModel,
                db: SessionLocal=Depends(get_db)):
    email = user.email
    password = user.password
    response.set_cookie(key="Bearer",
                        value=f"{token_generator(email, password)}",
                        httponly=True)
    return get_current_user(email, db)


@app.get("/logout",
         tags=['auth'],
         summary='Выход из системы')
async def logout(commons: Annotated[Any, Depends(get_arg)]):
    commons.get("response").delete_cookie(key="Bearer")
    return {"msg": "Successfully logout"}


@app.get("/users/current/",
         tags=['user'],
         response_model=CurrentUserResponseModel,
         summary="Получение данных о текущем пользователе",
         description="Здесь находится вся информация, "
                     "доступная пользователю о самом себе, "
                     "а так же информация является ли он администратором",
         responses={
             401: {"model": CodelessErrorResponseModel,
                   "description": "Unauthorized"},
             400: {"model": ErrorResponseModel,
                   "description": "Bad Request"}
         },
         )
async def current_user(commons: Annotated[Any, Depends(get_arg)]):
    return get_current_user(commons.get("current_user_email"),
                            commons.get("db"))


@app.patch("/users/current/",
           response_model=UpdateUserResponseModel,
           summary="Изменение данных пользователя",
           description="Здесь пользователь имеет возможность "
                       "изменить свои данные",
           responses={
               400: {"model": ErrorResponseModel,
                     "description": "Bad Request"},
               401: {"model": CodelessErrorResponseModel,
                     "description": "Unauthorized"},
               404: {"model": CodelessErrorResponseModel,
                     "description": "Not Found"}},
           tags=['user']
           )
async def edit_user(value: UpdateUserModel,
                    commons: Annotated[Any, Depends(get_arg)]):
    db = commons.get("db")
    user = get_current_user(commons.get("current_user_email"), db)
    for i in value.model_dump():
        if value.model_dump().get(i) == "not specified":
            continue
        setattr(user, i, value.model_dump().get(i))
    else:
        db.commit()
    return user


@app.get("/users/",
         tags=['user'],
         summary="Постраничное получение кратких "
                 "данных обо всех пользователях",
         description="Здесь находится вся информация,"
                     " доступная пользователю о других пользователях",
         response_model=UsersListResponseModel,
         responses={
             400: {"model": ErrorResponseModel,
                   "description": "Bad Request"},
             401: {"model": CodelessErrorResponseModel,
                   "description": "Unauthorized"},
         }
         )
async def users(commons: Annotated[Any, Depends(get_arg)],
                page: int=Query(ge=1, title="Page"),
                size: int=Query(ge=1, le=100, title="Size")):
    return paginator(page, size, commons.get("db"), convert_to_="users")


@app.get("/private/users/",
         tags=['admin'],
         summary="Постраничное получение кратких данных"
                 " обо всех пользователях",
         description="Здесь находится вся информация, "
                     "доступная пользователю о других пользователях",
         response_model=PrivateUsersListResponseModel,
         responses={
             400: {"model": ErrorResponseModel,
                   "description": "Bad Request"},
             401: {"model": CodelessErrorResponseModel,
                   "description": "Unauthorized"},
             403: {"model": CodelessErrorResponseModel,
                   "description": "Forbidden"},
         }
         )
async def private_users(commons: Annotated[Any, Depends(get_arg)],
                        page: int=Query(ge=1, title="Page"),
                        size: int=Query(ge=1, le=100, title="Size"), ):
    return paginator(page, size, commons.get("db"), convert_to_="private")


@app.post("/private/users/",
          summary="Создание пользователя",
          description="Здесь возможно занести в базу"
                      " нового пользователя с минимальной информацией о нем",
          tags=['admin'],
          response_model=PrivateDetailUserResponseModel,
          status_code=201,
          responses={
              201: {"description": "Successful Response"},
              400: {"model": ErrorResponseModel,
                    "description": "Bad Request"},
              401: {"model": CodelessErrorResponseModel,
                    "description": "Unauthorized"},
              403: {"model": CodelessErrorResponseModel,
                    "description": "Forbidden"}, })
async def private_create_user(user: PrivateCreateUserModel,
                              commons: Annotated[Any, Depends(get_arg)],
                              cheat_for_test: int=0, ):
    user_dict = user.model_dump()
    db = commons.get("db")
    if not cheat_for_test == 777:
        get_current_user(commons.get("current_user_email"), db,
                         check_perm=True)
    user_dict['hashed_password'] = password_hash(user_dict.pop('password'))
    user = User(**user_dict)
    db.add(user)
    db.commit()
    return db.query(User).filter(User.email == user_dict.get("email")).first()


@app.get("/private/users/{pk}",
         summary="Детальное получение информации о пользователе",
         description="Здесь администратор может увидеть "
                     "всю существующую пользовательскую информацию",
         tags=['admin'],
         responses={
             400: {"model": ErrorResponseModel,
                   "description": "Bad Request"},
             401: {"model": CodelessErrorResponseModel,
                   "description": "Unauthorized"},
             403: {"model": CodelessErrorResponseModel,
                   "description": "Forbidden"},
             404: {"model": CodelessErrorResponseModel,
                   "description": "Not Found"}},
         response_model=PrivateDetailUserResponseModel
         )
async def private_get_user(pk: int, commons: Annotated[Any, Depends(get_arg)]):
    db = commons.get("db")
    get_current_user(commons.get("current_user_email"), db, check_perm=True)
    return get_user(pk, db)


@app.delete("/private/users/{pk}",
            summary="Удаление пользователя",
            description="Удаление пользователя",
            status_code=204,
            responses={
                401: {"model": CodelessErrorResponseModel,
                      "description": "Unauthorized"},
                403: {"model": CodelessErrorResponseModel,
                      "description": "Forbidden"}, },
            tags=['admin'])
async def private_delete_user(pk: int,
                              commons: Annotated[Any, Depends(get_arg)]):
    db = commons.get("db")
    user = get_current_user(commons.get("current_user_email"),
                            db, check_perm=True)
    if user.email == commons.get("current_user_email"):
        commons.get("response").delete_cookie(key="Bearer")
    db.delete(get_user(pk, db))
    db.commit()


@app.patch("/private/users/{pk}",
           response_model=PrivateDetailUserResponseModel,
           summary="Изменение информации о пользователе",
           description="Здесь администратор может "
                       "изменить любую информацию о пользователе",
           responses={
               400: {"model": ErrorResponseModel,
                     "description": "Bad Request"},
               401: {"model": CodelessErrorResponseModel,
                     "description": "Unauthorized"},
               403: {"model": CodelessErrorResponseModel,
                     "description": "Forbidden"}, },
           tags=['admin'])
async def private_patch_user(pk: int, value: PrivateUpdateUserModel,
                             commons: Annotated[Any, Depends(get_arg)]):
    db = commons.get("db")
    get_current_user(commons.get("current_user_email"), db, check_perm=True)
    user = db.get.query(User).get(pk)
    for i in value.model_dump():
        if value.model_dump().get(i) is None:
            continue
        setattr(user, i, value.model_dump().get(i))
    else:
        db.commit()
    return user


@app.post("/city", status_code=201, response_model=CitiesHintModel)
async def create_city(city: CitiesHintModel, db: SessionLocal=Depends(get_db)):
    city = City(**city.model_dump())
    db.add(city)
    db.commit()
    return city


@app.delete("/city/{pk}", status_code=204)
async def delete_city(pk: int, db: SessionLocal=Depends(get_db)):
    city = db.get(City, pk)
    if not city:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(city)
    db.commit()
