from typing import Optional
from fastapi.exceptions import HTTPException
from starlette.requests import Request
from fastapi.security import OAuth2PasswordBearer


class MyOAuth2PasswordBearer(OAuth2PasswordBearer):

    def __init__(self, tokenUrl):
        super().__init__(tokenUrl)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.cookies
        if "Bearer" in list(authorization):
            scheme = "Bearer"
        else:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        param = request.cookies.get(scheme)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=401,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param
