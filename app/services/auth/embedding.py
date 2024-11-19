from typing import List
import uuid


class Embedding:
    def __init__(
        self,
        vector: List[float] | None = None,
        user_id: uuid.UUID | None = None,
        id: uuid.UUID | None = None,
    ) -> None:
        self.id = id
        self.vector = vector
        self.user_id = user_id
