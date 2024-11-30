from typing import List
import uuid

from loguru import logger

from app.services.exceptions import EmbeddingVectorSizeError
from app.services.interface.face import IFace
from app.log import configure_logging

configure_logging()


class Face(IFace):
    def __init__(
        self,
        embedding: List[float] = [],
        user_id: uuid.UUID | None = None,
        id: uuid.UUID | None = None,
        similarity: float | None = None,
    ) -> None:
        self.__embedding: List[float] = []
        self.id = id
        self.embedding = embedding
        self.user_id = user_id
        self.similarity = similarity

    @property
    def embedding(self):
        return self.__embedding

    @embedding.setter
    def embedding(self, value: List[float]):
        try:
            logger.debug(f"Количество элементов в embedding {len(value)}")
            if len(value) == 512:
                self.__embedding = value
            else:
                raise EmbeddingVectorSizeError(
                    "Требуется использовать 512 мерный вектор"
                )
        except TypeError:
            raise ValueError("Тип не поддеживается")
