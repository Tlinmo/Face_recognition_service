from typing import List
import uuid
from abc import ABC, abstractmethod


class IFace(ABC):
    @abstractmethod
    def __init__(
        self,
        embedding: List[float] = [],
        user_id: uuid.UUID | None = None,
        id: uuid.UUID | None = None,
        similarity: float | None = None,
    ) -> None:
        self.id = id
        self.embedding = embedding
        self.user_id = user_id
        self.similarity = similarity
