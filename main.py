from fastapi import Cookie, FastAPI, Header
from typing import Annotated, Union, Any

from fastapi import Depends, FastAPI, Response, Form
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel

app = FastAPI()


class LoginModel(BaseModel):
    login: str
    password: str


class LogoutModel(BaseModel):
    login: str
    password: str


@app.post("/login")
async def login(login: LoginModel):
    return Response(False)


@app.get("/logout", response_model={})
async def logout():
    return Response(status_code=200)


@app.get("/users/current")
async def current_user(current: int):
    pass


@app.patch("/users/current")
async def edit_user():
    pass


@app.get("/users")
async def users():
    pass


@app.get("private/users")
async def private_users():
    pass


@app.post("private/users")
async def private_create_user():
    pass


@app.get("/private/users/{pk}")
async def private_get_user(pk: int):
    pass


@app.delete("/private/users/{pk}")
async def private_get_user(pk: int):
    pass


@app.patch("/private/users/{pk}")
async def private_get_user(pk: int):
    pass



