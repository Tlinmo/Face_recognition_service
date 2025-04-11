from typing import List
import uuid
from abc import ABC, abstractmethod

from app.services.interface.face import IFace


class IUser(ABC):
    @abstractmethod
    def __init__(
        self,
        username: str,
        first_name: str,
        second_name: str,
        hashed_password: str = "",
        id: uuid.UUID | None = None,
        is_superuser: bool = False,
        faces: List[List[float]] | List[IFace] = [],
    ) -> None:
        self.id = id
        self.username = username
        self.first_name = first_name
        self.second_name = second_name
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
