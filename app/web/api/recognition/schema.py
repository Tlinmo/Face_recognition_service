from typing import List

from pydantic import BaseModel


class VectorEmbedding(BaseModel):
    embedding: List[float]
