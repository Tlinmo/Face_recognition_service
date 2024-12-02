from typing import List
import numpy as np
import uuid
import string

from loguru import logger
import bcrypt

from app.services.interface.face import IFace
from app.services.models.face import Face
from app.services.interface.user import IUser


class User(IUser):
    def __init__(
        self,
        username: str,
        hashed_password: str = "",
        id: uuid.UUID | None = None,
        is_superuser: bool = False,
        faces: List[List[float]] | List[IFace] = [],
    ) -> None:
        self.__faces = []
        self.__username = None
        self.id = id
        self.username = username
        self.hashed_password = hashed_password
        self.is_superuser = is_superuser
        self.faces = faces

    @staticmethod
    def hash_password(password: str) -> str:
        if not password:
            raise ValueError(
                    f"Пароль пользователя не может быть пустым. На вход было получено {type(password)}"
            )
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    def check_password(self, password: str) -> bool:
        if self.hashed_password:
            return bcrypt.checkpw(
                password.encode("utf-8"), self.hashed_password.encode("utf-8")
            )
        return False

    @property
    def faces(self) -> List[IFace]:
        return self.__faces

    @faces.setter
    def faces(self, _faces: List[List[float]] | List[IFace] = []):
        logger.debug("Пользователю задется его faces")

        for embedding in _faces:
            if isinstance(embedding, IFace):
                logger.debug("Добавление Face в список")

                self.__faces.append(embedding)
            elif isinstance(embedding, (np.ndarray, List)):
                logger.debug("Создания объектов Face из списка")

                _face = Face(embedding=embedding)
                if self.id:
                    _face.user_id = self.id
                self.__faces.append(_face)
            else:
                raise ValueError(
                    f"Элементы должны быть либо списками чисел, либо объектами Embedding. На вход было получено {type(embedding)}"
                )
    
    @property
    def username(self) -> str | None:
        return self.__username
    
    @username.setter
    def username(self, value: str):
        if not value:
            raise ValueError(
                    f"Имя пользователя не может быть пустым. На вход было получено {type(value)}"
            )
        for char in value:
            if char not in (string.ascii_letters + string.digits):
                raise ValueError(
                    f"Имя пользователя может содержать только цифры и латиницу. На вход было получено {type(value)}"
            )
        self.__username = value