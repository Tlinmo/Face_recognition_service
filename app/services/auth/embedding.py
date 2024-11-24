from typing import List
import uuid

from app.services.exceptions import EmbeddingVectorSizeError

class Embedding:
    def __init__(
        self,
        vector: List[float] = [],
        user_id: uuid.UUID | None = None,
        id: uuid.UUID | None = None,
        similarity: float | None = None,
    ) -> None:
        self.__vector: List[float] = []
        self.id = id
        self.vector = vector
        self.user_id = user_id
        self.similarity = similarity


    @property
    def vector(self):
        return self.__vector

    @vector.setter
    def vector(self, value: List[float]):
        try:
            if len(value) == 512:
                self.__vector = value
            else:
                raise EmbeddingVectorSizeError("Требуется использовать 512 мерный вектор")
        except TypeError:
                raise ValueError("Тип не поддеживается")