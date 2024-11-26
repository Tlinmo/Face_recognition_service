from typing import List
import uuid
from abc import ABC, abstractmethod

from app.services.interface.embedding import IEmbedding


class IUser(ABC):
    @abstractmethod
    def __init__(
        self,
        username: str | None = None,
        hashed_password: str | None = None,
        id: uuid.UUID | None = None,
        is_superuser: bool = False,
        embeddings: List[List[float]] | List[IEmbedding] = [],
    ) -> None:
        self.id = id
        self.username = username
        self.hashed_password = hashed_password
        self.is_superuser = is_superuser
        self.embeddings = embeddings

    @staticmethod
    @abstractmethod
    def hash_password(password: str) -> str:
        pass
    @abstractmethod
    def check_password(self, password: str) -> bool:
        pass