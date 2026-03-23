from typing import Self

from pydantic import EmailStr, Field

from dddesign.components.domains.value_objects import AutoUUID
from dddesign.structure.domains.entities import Entity


class UserId(AutoUUID):
    ...


class User(Entity):
    user_id: UserId = Field(default_factory=UserId)
    email: EmailStr
    hashed_password: str

    @classmethod
    def factory(cls, email: EmailStr, hashed_password: str) -> Self:
        return cls(email=email, hashed_password=hashed_password)
