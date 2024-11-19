from typing import List

from loguru import logger
from app.repository.exceptions import UsernameError, DataBaseError

from app.repository.repository import UserRepository, EmbeddingRepository
from app.services.users.user import User
from app.services.exceptions import (
    AuthFaceError,
    AuthUsernameError,
    AuthPasswordError,
    ServiceDataBaseError,
)
from app.log import configure_logging

configure_logging()


class AuthService:
    def __init__(
        self, user_repository: UserRepository, embedding_repository: EmbeddingRepository
    ) -> None:
        self.user_repository = user_repository
        self.embedding_repository = embedding_repository

    async def register(self, user: User) -> str:
        try:
            _user = await self.user_repository.add(entity=user)
            logger.debug(_user.__dict__)

            # Если id к этому моменту нет, сработает исключение на уровне репозитория
            if _user.id:
                # return generate_jwt(id_=_user.id)
                return "Всё збс"
            else:
                return "Кажется всё пошло по ***** чекай логи"

        except UsernameError as error:
            logger.debug(error)
            raise AuthUsernameError()
        except DataBaseError as error:
            logger.debug(error)
            raise ServiceDataBaseError()

    async def authentication(self, username: str, password: str) -> str:
        _user = await self.user_repository.get(username=username)
        if _user:
            if _user.check_password(password):
                return "тут типа токен? а зач?"
            raise AuthPasswordError()
        raise AuthUsernameError()

    async def face_authentication(self, embedding: List[float]) -> User | str:
        _embedding = await self.embedding_repository.get(vector=embedding)
        if not _embedding:
            raise AuthFaceError

        user = await self.user_repository.get(_embedding.user_id)

        if not user:
            return "Кто ты, воин?"
        return user
