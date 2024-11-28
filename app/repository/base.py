from sqlalchemy.orm import DeclarativeBase

from app.repository.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
