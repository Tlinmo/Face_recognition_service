from typing import List
import numpy as np
import uuid

from loguru import logger
import bcrypt

from app.services.auth.embedding import Embedding


class User:
    def __init__(
        self,
        username: str | None = None,
        hashed_password: str | None = None,
        id: uuid.UUID | None = None,
        is_superuser: bool = False,
        embeddings: List[List[float]] | List[Embedding] = [],
    ) -> None:
        self.__embeddings = []
        self.id = id
        self.username = username
        self.hashed_password = hashed_password
        self.is_superuser = is_superuser
        self.embeddings = embeddings
        

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"), self.hashed_password.encode("utf-8")
        )
        
    @property
    def embeddings(self) -> List[Embedding]:
        return self.__embeddings

    
    @embeddings.setter
    def embeddings(self, _embeddings: List[List[float]] | List[Embedding] = []):
        logger.debug("Пользователю задется его embedding")
        
        # А ты что думал? в сказку попал? а я слов больше не знаю
        for embedding in _embeddings:
            if isinstance(embedding, Embedding):
                logger.debug("Добавление Embedding в список")
                
                self.__embeddings.append(embedding)
            elif isinstance(embedding, (np.ndarray, List)):
                logger.debug("Создания объектов Embedding из списка")
                
                _embedding = Embedding(vector=embedding)
                if self.id:  _embedding.user_id = self.id
                self.__embeddings.append(_embedding)
            else:
                raise ValueError(f"Элементы должны быть либо списками чисел, либо объектами Embedding. На вход было получено {type(embedding)}")