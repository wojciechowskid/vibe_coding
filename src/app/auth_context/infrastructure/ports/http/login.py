from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

from app.auth_context.applications.auth import auth_app_impl

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


@router.post('/')
async def auth_login(body: LoginRequest) -> TokenResponse:
    token_pair = await auth_app_impl.login(email=body.email, password=body.password)
    return TokenResponse(access_token=token_pair.access_token, refresh_token=token_pair.refresh_token)
