from uuid import UUID
from typing import List, Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    embeddings: Optional[List[List[float]]]


class AuthUser(BaseModel):
    username: str
    password: str


class AuthFaceUser(BaseModel):
    embedding: Optional[List[float]]
    
    
class SimilarityEmbedding(BaseModel):
    similarity: float
    
class FaceUser(BaseModel):
    id: Optional[UUID]
    username: str
    embeddings: List[SimilarityEmbedding]

    class Config:
        from_attributes = True