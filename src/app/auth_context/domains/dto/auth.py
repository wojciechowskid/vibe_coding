from pydantic import EmailStr

from dddesign.structure.domains.dto import DataTransferObject


class RegisterUserDTO(DataTransferObject):
    email: EmailStr
    password: str


class TokenPairDTO(DataTransferObject):
    access_token: str
    refresh_token: str


class TokenPayloadDTO(DataTransferObject):
    user_id: str
    token_type: str
