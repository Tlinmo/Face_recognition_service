from typing import List
from uuid import UUID

from loguru import logger

from app.repository.auth_repository import IUserRepository
from app.services.users.user import User
from app.repository.exceptions import UpdateError
from app.services.exceptions import UserUpdateError
from app.log import configure_logging

configure_logging()


class UserService:
    def __init__(self, user_repository: IUserRepository) -> None:
        self.user_repository = user_repository

    async def lst(self, offset: int, limit: int) -> List[User]:
        _users = await self.user_repository.list(offset=offset, limit=limit)
        return _users

    async def show(self, id_: UUID) -> User | None:
        _user = await self.user_repository.get(id_=id_)
        if _user:
            return _user

    async def update(self, user: User):
        try:
            await self.user_repository.update(user=user)
        except UpdateError:
            raise UserUpdateError()
