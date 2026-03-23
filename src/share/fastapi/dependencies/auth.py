from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth_context.infrastructure.adapters.internal.auth import auth_adapter_impl
from app.auth_context.domains.dto.auth import TokenPayloadDTO

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenPayloadDTO:
    return await auth_adapter_impl.verify_token(credentials.credentials)
