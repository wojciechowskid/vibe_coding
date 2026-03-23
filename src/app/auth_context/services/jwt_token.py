from datetime import timedelta

import jwt

from dddesign.structure.services import Service
from ddutils.datetime_helpers import utc_now

from app.auth_context.domains.dto.auth import TokenPayloadDTO
from app.auth_context.domains.errors.auth import InvalidTokenError


class GenerateTokenService(Service):
    user_id: str
    token_type: str
    secret_key: str
    algorithm: str
    expire_minutes: int

    def handle(self) -> str:
        expire = utc_now() + timedelta(minutes=self.expire_minutes)
        payload = {
            'user_id': self.user_id,
            'token_type': self.token_type,
            'exp': expire,
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)


class DecodeTokenService(Service):
    token: str
    secret_key: str
    algorithm: str

    def handle(self) -> TokenPayloadDTO:
        try:
            payload = jwt.decode(self.token, self.secret_key, algorithms=[self.algorithm])
            return TokenPayloadDTO(
                user_id=payload['user_id'],
                token_type=payload['token_type'],
            )
        except (jwt.InvalidTokenError, KeyError):
            raise InvalidTokenError()
