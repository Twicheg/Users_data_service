from typing import Union

from pydantic_core._pydantic_core import ValidationError
from typing_extensions import Annotated
from fastapi import FastAPI, Response, Depends
from fastapi.encoders import jsonable_encoder
from service.database import SessionLocal
from service.schemas import LoginModel, PrivateCreateUserModel
from service.services import get_db, check_email, password_hash, check_email_with_password, ACCESS_TOKEN_EXPIRE_MINUTES, \
    token_generator, MyOAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.param_functions import Form

from service.services import oauth2_scheme
from service.users import User

app = FastAPI()


@app.post("/login",
          tags=["auth"],
          description="После успешного входа в систему необходимо установить Cookies для пользователя",
          summary='Вход в систему'
          )
async def login(response: Response, db: SessionLocal = Depends(get_db),
                request_form: MyOAuth2PasswordRequestForm = Depends()):
    check_email_with_password(request_form, db)
    response.set_cookie(key="Bearer",
                        value=f"{token_generator(request_form.username,
                                                 request_form.password)}",
                        httponly=True)
    return {"msg": "Successfully login"}


@app.get("/logout",
         tags=['auth'],
         summary='Вход в систему')
async def logout(response: Response, current_user: Annotated[str, Depends(oauth2_scheme)]):
    print(current_user)
    response.delete_cookie(key="Bearer")
    return {"msg": "Successfully logout"}


@app.get("/users/current")
async def current_user(current_user: Annotated[str, Depends(oauth2_scheme)]):
    print(current_user)
    return {1: 1}


@app.patch("/users/current")
async def edit_user():
    pass


@app.get("/users")
async def users():
    pass


@app.get("/private/users")
async def private_users():
    pass


@app.post("/private/users", tags=["admin"], response_model=PrivateCreateUserModel)
async def private_create_user(user: PrivateCreateUserModel, db: SessionLocal = Depends(get_db)):
    user_dict = user.dict()
    check_email(user_dict, db=db)
    password = user_dict.pop('password')
    user_dict['hashed_password'] = password_hash(password)
    db.add(User(**user_dict))
    db.commit()
    return user


@app.get("/private/users/{pk}")
async def private_get_user(pk: int):
    pass


@app.delete("/private/users/{pk}")
async def private_delete_user(pk: int):
    pass


@app.patch("/private/users/{pk}")
async def private_patch_user(pk: int):
    pass
