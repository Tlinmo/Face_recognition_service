from typing import List
import uuid


class Embedding:
    def __init__(
        self,
        vector: List[float] | None = None,
        user_id:uuid.UUID | None = None,
        id: uuid.UUID | None = None,
    ) -> None:
        self.id = id
        self.vector = vector
        self.user_id = user_id
        
        
        
class User:
    def __init__(
        self,
        username: str | None = None,
        hashed_password: str | None = None,
        id: uuid.UUID | None = None,
        is_superuser: bool = False,
        embeddings: List[List[float]] = [],
    ) -> None:
        self.id = id
        self.username = username
        self.hashed_password = hashed_password
        self.is_superuser = is_superuser
        self.embeddings = embeddings
