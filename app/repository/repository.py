from typing import List, TypeVar, Generic
from abc import ABC, abstractmethod
import uuid

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, DBAPIError
from sqlalchemy.orm import selectinload


from app.log import configure_logging
from app.services.interface.user import IUser
from app.services.interface.face import IFace
from app.services.models.user import User
from app.services.models.face import Face
from app.repository.models.users import User as db_User
from app.repository.models.users import Face as db_Face
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
            error_type = type(error)
            logger.error(f" {error_type} | {error}")
            raise UsernameError("Username уже занят")
        except SQLAlchemyError as error:
            error_type = type(error)
            logger.error(f" {error_type} | {error}")
            await self.session.rollback()
            raise DataBaseError()
        except Exception as error:
            error_type = type(error)
            logger.error(f" {error_type} | {error}")
            await self.session.rollback()


class UserRepository(IRepository):
    async def add(self, entity: IUser) -> IUser:
        db_user = db_User(
            username=entity.username,
            hashed_password=entity.hashed_password,
            is_superuser=entity.is_superuser,
        )
        # Итс нот гуд да? блять..
        db_user.set_embeddings([f.embedding for f in entity.faces])

        self.session.add(db_user)
        await self.save()
        _user = User(**db_user.dict())
        return _user

    async def get(
        self,
        id_: uuid.UUID | None = None,
        username: str | None = None,
    ) -> IUser | None:

        if id_ is None and username is None:
            return None

        sql = select(db_User).options(selectinload(db_User.faces))

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

    async def list(self, offset: int, limit: int = 10) -> List[IUser]:
        sql = (
            select(db_User)
            .options(selectinload(db_User.faces))
            .offset(offset)
            .limit(limit)
        )
        try:
            users = await self.session.execute(sql)
            users = users.scalars().all()
            return [User(**user.dict()) for user in users]
        except DBAPIError:
            return []

    async def update(self, entity: IUser) -> None:
        try:
            sql = (
                select(db_User)
                .options(selectinload(db_User.faces))
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

            if entity.faces:
                logger.debug(f"Изменяем faces пользователя")

                await self.session.execute(
                    delete(db_Face).where(db_Face.user_id == entity.id)
                )
                _user.set_embeddings([f.embedding for f in entity.faces])
        except IntegrityError as error:
            raise UsernameError("Username уже занят")

        await self.save()


class FaceRepository(IRepository):
    async def add(self, entity: IFace) -> IFace:
        db_face = db_Face(
            embedding=entity.embedding,
            user_id=entity.user_id,
        )

        self.session.add(db_Face)
        await self.save()

        _face = Face(**db_face.dict())
        return _face

    async def get(
        self,
        id_: uuid.UUID | None = None,
        embedding: List[float] = [],
    ) -> IFace | None:
        face = None

        if not id_ and not embedding:
            return None

        if id_:
            sql = (
                select(db_Face)
                .options(selectinload(db_Face.user))
                .where(db_Face.id == id_)
            )
            face = await self.session.execute(sql)
            face = face.scalars().one_or_none()
        if embedding:
            sql = (
                select(db_Face)
                .where(
                    (db_Face.embedding.l2_distance(embedding)) < 1.2  # Порог схожести
                )
                .order_by(db_Face.embedding.l2_distance(embedding))
                .limit(1)
            )
            face = await self.session.execute(sql)
            face = face.scalars().one_or_none()

        if face:
            return Face(**face.dict())

    async def list(self, offset: int, limit: int = 10) -> List[IFace]:
        sql = (
            select(db_Face)
            .options(selectinload(db_Face.user))
            .offset(offset)
            .limit(limit)
        )
        faces = await self.session.execute(sql)
        faces = faces.scalars().all()
        return [Face(**face.dict()) for face in faces]

    async def update(self, entity: IFace) -> None:
        sql = (
            select(db_Face)
            .options(selectinload(db_Face.user))
            .where(db_Face.id == entity.id)
        )
        _face = await self.session.execute(sql)
        _face = _face.scalars().one_or_none()

        if _face is None:
            raise UpdateError("Face не найден")

        if entity.embedding:
            _face.embedding = entity.embedding

        await self.save()
