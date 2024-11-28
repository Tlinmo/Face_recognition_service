from typing import List
import numpy as np

from loguru import logger

from app.settings import settings
from app.repository.exceptions import UsernameError, DataBaseError
from app.repository.repository import UserRepository, FaceRepository
from app.services.interface.face import IFace
from app.services.interface.user import IUser
from app.services.exceptions import (
    AuthFaceError,
    ServiceUsernameError,
    AuthPasswordError,
    ServiceDataBaseError,
)
from app.log import configure_logging

configure_logging()


class AuthService:
    def __init__(
        self, user_repository: UserRepository, face_repository: FaceRepository
    ) -> None:
        self.user_repository = user_repository
        self.face_repository = face_repository

    async def register(self, user: IUser) -> str:
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
            raise ServiceUsernameError()
        except DataBaseError as error:
            logger.debug(error)
            raise ServiceDataBaseError()

    async def authentication(self, username: str, password: str) -> str:
        _user = await self.user_repository.get(username=username)
        if _user:
            if _user.check_password(password):
                return "тут типа токен? а зач?"
            raise AuthPasswordError()
        raise ServiceUsernameError()

    async def face_authentication(self, face: IFace) -> IUser:
        _face = await self.face_repository.get(embedding=face.embedding)

        if not _face:
            raise AuthFaceError

        user = await self.user_repository.get(_face.user_id)

        if not user:
            raise AuthFaceError

        # Узнаем схожесть с Faces пользователя
        # Что лучше, использовать это, или __debug__? хм..
        if settings.environment == "dev":
            logger.debug(f"Узнается схожесть с embeddings пользователя")
            for user_face in user.faces:
                similarity = np.linalg.norm(
                    np.array(user_face.embedding) - np.array(face.embedding)
                )
                user_face.similarity = similarity

                logger.debug(f"Схожесть пользователя: {similarity}")

        return user
