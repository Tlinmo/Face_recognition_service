from uuid import UUID
from typing import List, Optional

from pydantic import BaseModel


class UpdateUser(BaseModel):
    username: str | None = None
    embeddings: Optional[List[List[float]]] = [[]]

    class Config:
        from_attributes = True


class User(BaseModel):
    id: Optional[UUID]
    username: str
    is_superuser: bool
    embeddings: Optional[List[List[float]]]

    class Config:
        from_attributes = True
