from typing import List
import uuid

from sqlalchemy import Boolean, Column, String, ForeignKey, UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from loguru import logger

from app.repository.base import Base
from app.log import configure_logging


configure_logging()


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, index=True)
    is_superuser = Column(Boolean, default=False)
    faces = relationship("Face", back_populates="user")

    def dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "hashed_password": self.hashed_password,
            "is_superuser": self.is_superuser,
            "faces": [face.embedding for face in self.faces],
        }

    def set_embeddings(self, embeddings: List[List[float]]):
        if embeddings:
            for embedding in embeddings:
                # Ну, мало ли кто захочет пустой список в списке отправить?
                if embedding:
                    self.faces.append(Face(embedding=embedding))
                else:
                    self.faces = []
        else:
            self.faces = []


class Face(Base):
    __tablename__ = "faces"

    id = Column(UUID, primary_key=True, default=generate_uuid)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    embedding = Column(Vector(512), nullable=False)
    user = relationship("User", back_populates="faces")

    def dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "embedding": self.embedding,
        }
