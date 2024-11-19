from typing import List, TypeVar, Generic
from abc import ABC, abstractmethod
import uuid

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, func, select, or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload
from pgvector.sqlalchemy.functions import avg

from app.log import configure_logging
from app.services.users.user import User
from app.services.auth.embedding import Embedding
from app.repository.models.users import User as db_User
from app.repository.models.users import Embedding as db_Embedding
from app.repository.exceptions import UsernameError, UpdateError, DataBaseError

configure_logging()


T = TypeVar("T")


class IRepository(Generic[T], ABC):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        super().__init__()

    @abstractmethod
    async def add(self, entity: T) -> T:
        pass

    @abstractmethod
    async def get(self, id_: uuid.UUID | None = None) -> T | None:
        pass

    @abstractmethod
    async def list(self, offset: int, limit: int = 10) -> List[T]:
        pass

    @abstractmethod
    async def update(self, entity: T):
        pass

    async def save(self):
        try:
            logger.debug("Производится commit")
            await self.session.commit()
        except IntegrityError as error:
            logger.error(error)
            raise UsernameError("Username уже занят")
        except SQLAlchemyError as error:
            error_type = type(error)
            logger.error(f" {error_type} | {error}")
            await self.session.rollback()
            raise DataBaseError()
        except Exception as error:
            logger.error(error)
            await self.session.rollback()


class UserRepository(IRepository):
    async def add(self, entity: User) -> User:
        db_user = db_User(
            username=entity.username,
            hashed_password=entity.hashed_password,
            is_superuser=entity.is_superuser,
        )
        db_user.set_embeddings(entity.embeddings)

        self.session.add(db_user)
        await self.save()
        _user = User(**db_user.dict())
        return _user

    async def get(
        self,
        id_: uuid.UUID | None = None,
        username: str | None = None,
    ) -> User | None:

        if id_ is None and username is None:
            return None

        sql = select(db_User).options(selectinload(db_User.embeddings))

        filters = []
        if id_:
            filters.append(db_User.id == str(id_))
        if username:
            filters.append(db_User.username == username)

        sql = sql.filter(or_(*filters))

        user = await self.session.execute(sql)
        user = user.scalars().one_or_none()

        if user:
            return User(**user.dict())

    async def list(self, offset: int, limit: int = 10) -> List[User]:
        sql = (
            select(db_User)
            .options(selectinload(db_User.embeddings))
            .offset(offset)
            .limit(limit)
        )
        users = await self.session.execute(sql)
        users = users.scalars().all()
        return [User(**user.dict()) for user in users]

    async def update(self, entity: User):
        sql = (
            select(db_User)
            .options(selectinload(db_User.embeddings))
            .where(db_User.id == entity.id)
        )
        _user = await self.session.execute(sql)
        _user = _user.scalars().one_or_none()

        if _user is None:
            raise UpdateError("User не найден")

        if entity.username:
            logger.debug(
                f"Изменяем имя пользователя {_user.username} на {entity.username}"
            )
            _user.username = entity.username

        if entity.embeddings:
            logger.debug(f"Изменяем embeddings пользователя")

            await self.session.execute(
                delete(db_Embedding).where(db_Embedding.user_id == entity.id)
            )
            _user.set_embeddings(entity.embeddings)

        await self.save()


class EmbeddingRepository(IRepository):
    async def add(self, entity: Embedding) -> Embedding:
        db_embedding = db_Embedding(
            vector=entity.vector,
            user_id=entity.user_id,
        )

        self.session.add(db_embedding)
        await self.save()

        _embedding = Embedding(**db_embedding.dict())
        return _embedding

    async def get(
        self,
        id_: uuid.UUID | None = None,
        vector: List[float] = [],
    ) -> Embedding | None:
        embedding = None

        if not id_ and not vector:
            return None

        if id_:
            sql = (
                select(db_Embedding)
                .options(selectinload(db_Embedding.user))
                .where(db_Embedding.id == id_)
            )
            embedding = await self.session.execute(sql)
            embedding = embedding.scalars().one_or_none()
        if vector:
            sql = (
                select(db_Embedding)
                .where(
                    (db_Embedding.vector.l2_distance(vector)) < 0.90
                )  # Порог схожести
                .order_by(db_Embedding.vector.l2_distance(vector))
                .limit(1)
            )
            embedding = await self.session.execute(sql)
            embedding = embedding.scalars().one_or_none()

        if embedding:
            return Embedding(**embedding.dict())

    async def list(self, offset: int, limit: int = 10) -> List[Embedding]:
        sql = (
            select(db_Embedding)
            .options(selectinload(db_Embedding.user))
            .offset(offset)
            .limit(limit)
        )
        embeddings = await self.session.execute(sql)
        embeddings = embeddings.scalars().all()
        return [Embedding(**embedding.dict()) for embedding in embeddings]

    async def update(self, entity: Embedding):
        sql = (
            select(db_Embedding)
            .options(selectinload(db_Embedding.user))
            .where(db_Embedding.id == entity.id)
        )
        _embedding = await self.session.execute(sql)
        _embedding = _embedding.scalars().one_or_none()

        if _embedding is None:
            raise UpdateError("Embedding не найден")

        if entity.vector:
            _embedding.vector = entity.vector

        await self.save()
