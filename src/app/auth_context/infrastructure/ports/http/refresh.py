from fastapi import APIRouter
from pydantic import BaseModel

from app.auth_context.applications.auth import auth_app_impl

router = APIRouter()


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


@router.post('/')
async def auth_refresh(body: RefreshRequest) -> TokenResponse:
    token_pair = await auth_app_impl.refresh(refresh_token=body.refresh_token)
    return TokenResponse(access_token=token_pair.access_token, refresh_token=token_pair.refresh_token)
