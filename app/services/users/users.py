from typing import List
from uuid import UUID

from loguru import logger

from app.repository.repository import UserRepository
from app.services.interface.user import IUser
from app.repository.exceptions import UpdateError, UsernameError
from app.services.exceptions import UserUpdateError, ServiceUsernameError
from app.log import configure_logging

configure_logging()


class UserService:
    def __init__(self, user_repository: UserRepository, user_id: UUID) -> None:
        self.user_repository = user_repository
        self.user_id = user_id # Для более гибкого управления правами, и отделение авторизации от уровня представления

    async def lst(self, offset: int, limit: int) -> List[IUser]:
        _users = await self.user_repository.list(offset=offset, limit=limit)
        return _users

    async def show(self, id_: UUID) -> IUser | None:
        _user = await self.user_repository.get(id_=id_)
        if _user:
            return _user

    async def update(self, user: IUser):
        try:
            _user = await self.user_repository.get(id_=self.user_id)
            if self.user_id == user.id or _user.is_superuser:
                await self.user_repository.update(entity=user)
            else:
                raise UserUpdateError("Доступ к запрашиваемому ресурсу запрещен")
        except UpdateError:
            raise UserUpdateError()
        except UsernameError:
            raise ServiceUsernameError()
