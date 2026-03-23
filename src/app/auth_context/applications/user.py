from pydantic import EmailStr

from dddesign.structure.applications import Application

from app.auth_context.domains.entities.user import User, UserId
from app.auth_context.infrastructure.repositories.user import UserRepository, user_repository_impl


class UserApp(Application):
    repo: UserRepository = user_repository_impl

    async def get(self, user_id: UserId) -> User | None:
        return await self.repo.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        return await self.repo.get_by_email(email)

    async def create(self, email: EmailStr, hashed_password: str) -> User:
        user = User.factory(email=email, hashed_password=hashed_password)
        await self.repo.create(user)
        return user


user_app_impl = UserApp()
