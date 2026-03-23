from dddesign.structure.infrastructure.adapters.internal import InternalAdapter

from app.auth_context.applications.auth import auth_app_impl
from app.auth_context.domains.dto.auth import TokenPayloadDTO


class AuthAdapter(InternalAdapter):
    @staticmethod
    async def verify_token(access_token: str) -> TokenPayloadDTO:
        return await auth_app_impl.verify_token(access_token)


auth_adapter_impl = AuthAdapter()
