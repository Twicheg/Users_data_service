from pydantic_core._pydantic_core import ValidationError
from typing_extensions import Annotated
from fastapi import FastAPI, Response, Depends
from fastapi.encoders import jsonable_encoder

from service.schemas import LoginModel, PrivateCreateUserModel

app = FastAPI()


async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


CommonsDep = Annotated[dict, Depends(common_parameters)]

@app.get("/userss/")
async def read_users(commons: CommonsDep):
    return commons


@app.post("/login",
          tags=["auth"],
          description="После успешного входа в систему необходимо установить Cookies для пользователя",
          summary='Вход в систему'
          )
async def login(item: LoginModel):
    update_data = item.dict(exclude_unset=True)
    # updated_item = stored_item_model.copy(update=update_data) Using Pydantic's update

    return jsonable_encoder(login)


@app.get("/logout",
         tags=['auth'],
         response_model={},
         response_description='',
         summary='Вход в систему')
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
async def private_create_user(user: PrivateCreateUserModel):
    print(user)
    pass


@app.get("/private/users/{pk}")
async def private_get_user(pk: int):
    pass


@app.delete("/private/users/{pk}")
async def private_delete_user(pk: int):
    pass


@app.patch("/private/users/{pk}")
async def private_patch_user(pk: int):
    pass
