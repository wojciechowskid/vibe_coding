from dddesign.structure.applications import Application

from config.entrypoints.dramatiq import dramatiq_facade_impl
from config.settings import settings

from app.auth_context.applications.user import UserApp, user_app_impl
from app.auth_context.domains.constants.token import TokenType
from app.auth_context.domains.dto.auth import RegisterUserDTO, TokenPayloadDTO
from app.auth_context.domains.errors.auth import (
    InvalidCredentialsError,
    InvalidTokenTypeError,
    UserAlreadyExistsError,
)
from app.auth_context.domains.value_objects.token import TokenPair
from app.auth_context.services.jwt_token import DecodeTokenService, GenerateTokenService
from app.auth_context.services.password_hasher import HashPasswordService, VerifyPasswordService


class AuthApp(Application):
    user_app: UserApp = user_app_impl

    def _generate_token_pair(self, user_id: str) -> TokenPair:
        access_token = GenerateTokenService(
            user_id=user_id,
            token_type=TokenType.ACCESS,
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        ).handle()
        refresh_token = GenerateTokenService(
            user_id=user_id,
            token_type=TokenType.REFRESH,
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            expire_minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
        ).handle()
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def register(self, data: RegisterUserDTO) -> TokenPair:
        existing_user = await self.user_app.get_by_email(data.email)
        if existing_user:
            raise UserAlreadyExistsError()

        hashed_password = HashPasswordService(password=data.password).handle()
        user = await self.user_app.create(email=data.email, hashed_password=hashed_password)

        dramatiq_facade_impl.send_task('email_notification_send_registration_email_task', email=data.email)

        return self._generate_token_pair(user_id=str(user.user_id))

    async def login(self, email: str, password: str) -> TokenPair:
        user = await self.user_app.get_by_email(email)
        if not user:
            raise InvalidCredentialsError()

        is_valid = VerifyPasswordService(password=password, hashed_password=user.hashed_password).handle()
        if not is_valid:
            raise InvalidCredentialsError()

        return self._generate_token_pair(user_id=str(user.user_id))

    async def refresh(self, refresh_token: str) -> TokenPair:
        payload = DecodeTokenService(
            token=refresh_token,
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        ).handle()

        if payload.token_type != TokenType.REFRESH:
            raise InvalidTokenTypeError()

        return self._generate_token_pair(user_id=payload.user_id)

    async def verify_token(self, access_token: str) -> TokenPayloadDTO:
        payload = DecodeTokenService(
            token=access_token,
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        ).handle()

        if payload.token_type != TokenType.ACCESS:
            raise InvalidTokenTypeError()

        return payload


auth_app_impl = AuthApp()
