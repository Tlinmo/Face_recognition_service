import numpy as np
from datetime import datetime, UTC, timedelta
from uuid import UUID

from loguru import logger
import jwt

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


def generate_jwt(id_: UUID) -> str:
    now = datetime.now(UTC)
    payload = {
        "iss": settings.base_url,
        "sub": str(id_),
        "aud": f"{settings.base_url}/api/",
        "iat": now.timestamp(),
        "exp": (now + timedelta(hours=24)).timestamp(),
        "scope": "bopenid",
    }

    return jwt.encode(payload, settings.secret_key, algorithm="RS256")


def decode_and_validate_token(access_token):
    return jwt.decode(
        access_token,
        key=settings.public_key,
        algorithms=["RS256"],
        audience=[f"{settings.base_url}/api/"],
    )


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
                return generate_jwt(id_=_user.id)
            else:
                return "Кажется всё пошло по ***** чекай логи"

        except UsernameError as error:
            logger.debug(error)
            raise ServiceUsernameError()
        except DataBaseError as error:
            logger.debug(error)
            raise ServiceDataBaseError()

    async def authentication(self, user: IUser, password: str) -> str:
        _user = await self.user_repository.get(username=user.username)
        if _user:
            if _user.check_password(password):
                return generate_jwt(id_=_user.id)
            raise AuthPasswordError()
        raise ServiceUsernameError()

    async def face_authentication(self, face: IFace) -> IUser:
        _face = await self.face_repository.get(embedding=face.embedding)

        if not _face:
            raise AuthFaceError

        user = await self.user_repository.get(_face.user_id)

        if not user:
            raise AuthFaceError

        logger.debug(f"Узнается схожесть с embeddings пользователя")
        for user_face in user.faces:
            similarity = np.linalg.norm(
                np.array(user_face.embedding) - np.array(face.embedding)
            )
            user_face.similarity = similarity

            logger.debug(f"Схожесть пользователя: {similarity}")

        return user
