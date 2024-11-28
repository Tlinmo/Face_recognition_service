from typing import List
import uuid
from abc import ABC, abstractmethod

from app.services.interface.face import IFace


class IUser(ABC):
    @abstractmethod
    def __init__(
        self,
        username: str | None = None,
        hashed_password: str | None = None,
        id: uuid.UUID | None = None,
        is_superuser: bool = False,
        faces: List[List[float]] | List[IFace] = [],
    ) -> None:
        self.id = id
        self.username = username
        self.hashed_password = hashed_password
        self.is_superuser = is_superuser
        self.faces = faces

    @staticmethod
    @abstractmethod
    def hash_password(password: str) -> str:
        pass
    @abstractmethod
    def check_password(self, password: str) -> bool:
        pass