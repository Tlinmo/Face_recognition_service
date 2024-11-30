from uuid import UUID
from typing import List, Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    embeddings: List[List[float]]


class AuthUser(BaseModel):
    username: str
    password: str


class AuthFaceUser(BaseModel):
    embedding: List[float]


class SimilarityEmbedding(BaseModel):
    similarity: float


class FaceUser(BaseModel):
    id: Optional[UUID]
    username: str
    faces: List[SimilarityEmbedding]

    class Config:
        from_attributes = True
        

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

