from uuid import UUID
from typing import List, Optional

from pydantic import BaseModel


class UpdateUser(BaseModel):
    username: str | None = None
    embeddings: Optional[List[List[float]]] = [[]]

    class Config:
        from_attributes = True


class VectorEmbedding(BaseModel):
    vector: List[float]


class User(BaseModel):
    id: Optional[UUID]
    username: str
    is_superuser: bool
    embeddings: List[VectorEmbedding]

    class Config:
        from_attributes = True


class Users(BaseModel):
    id: Optional[UUID]
    username: str
    is_superuser: bool

    class Config:
        from_attributes = True
