from uuid import UUID

from sqlmodel import Field

from share.sqlmodel.models.base import BaseSQLModel
from share.sqlmodel.models.mixins.dates import DatesMixin

from app.auth_context.domains.entities.user import User


class UserModel(BaseSQLModel[User], DatesMixin, table=True):
    user_id: UUID = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
