from uuid import UUID
from typing import List, Optional

from pydantic import BaseModel


class UpdateUser(BaseModel):
    username: str
    faces: List[List[float]]

    class Config:
        from_attributes = True


class FaceEmbedding(BaseModel):
    embedding: List[float]


class User(BaseModel):
    id: Optional[UUID]
    username: str
    is_superuser: bool
    faces: List[FaceEmbedding]

    class Config:
        from_attributes = True


class Users(BaseModel):
    id: Optional[UUID]
    username: str
    is_superuser: bool

    class Config:
        from_attributes = True
