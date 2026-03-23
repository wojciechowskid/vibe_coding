from dddesign.structure.infrastructure.repositories import Repository
from sqlmodel import select

from config.databases.postgres import Atomic

from app.auth_context.domains.entities.user import User, UserId
from app.auth_context.infrastructure.models.user import UserModel


class UserRepository(Repository):
    EXTERNAL_ALLOWED_METHODS: set[str] | None = {'get_by_email'}

    async def get(self, user_id: UserId) -> User | None:
        async with Atomic() as session:
            instance = await session.get(UserModel, user_id)
            return instance.to_entity() if instance else None

    async def get_by_email(self, email: str) -> User | None:
        async with Atomic() as session:
            statement = select(UserModel).where(UserModel.email == email)
            result = await session.execute(statement)
            instance = result.scalar_one_or_none()
            return instance.to_entity() if instance else None

    async def create(self, user: User) -> None:
        async with Atomic() as session:
            instance = UserModel.from_entity(user)
            session.add(instance)
            await session.flush()


user_repository_impl = UserRepository()
