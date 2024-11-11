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
    embeddings: Optional[List[List[float]]]
