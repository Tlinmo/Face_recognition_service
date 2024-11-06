import uuid
from sqlalchemy import Boolean, Column, String
from sqlalchemy.types import TypeDecorator, CHAR
from app.repository.base import Base


class UUIDType(TypeDecorator):
    """Custom UUID type for SQLite."""

    impl = CHAR

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)

    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid.UUID(value)


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, index=True)
    is_superuser = Column(Boolean, default=False)

    def dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "hashed_password": self.hashed_password,
            "is_superuser": self.is_superuser,
        }
