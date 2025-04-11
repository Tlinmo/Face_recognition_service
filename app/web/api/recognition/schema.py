from typing import List

from pydantic import BaseModel


class FaceEmbedding(BaseModel):
    embedding: List[float]
