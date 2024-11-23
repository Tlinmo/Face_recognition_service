from typing import List

from pydantic import BaseModel

class VectorEmbedding(BaseModel):
    vector: List[float]