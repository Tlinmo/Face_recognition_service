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
    embeddings = relationship("Embedding", back_populates="user")

    def dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "hashed_password": self.hashed_password,
            "is_superuser": self.is_superuser,
            "embeddings": [embedding.vector for embedding in self.embeddings],
        }


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(UUID, primary_key=True, default=generate_uuid)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    vector = Column(Vector(512), nullable=False)
    user = relationship("User", back_populates="embeddings")
