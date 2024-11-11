from typing import List
from abc import ABC, abstractmethod
import uuid

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError

from app.log import configure_logging
from app.services.users.user import User
from app.repository.models.users import User as db_User
from app.repository.exceptions import UsernameError, UpdateError

configure_logging()


class IUserRepository(ABC):
    @abstractmethod
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        super().__init__()

    @abstractmethod
    async def add(self, user: User) -> User:
        pass

    @abstractmethod
    async def get(
        self,
        id_: uuid.UUID | None = None,
        username: str | None = None,
    ) -> User | None:
        pass

    @abstractmethod
    async def list(self, offset: int, limit: int = 10) -> List[User]:
        pass

    @abstractmethod
    async def update(self, user: User):
        pass

    @abstractmethod
    async def save(self):
        pass

class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def add(self, user: User) -> User:
        db_user = db_User(
            username=user.username,
            hashed_password=user.hashed_password,
            is_superuser=user.is_superuser,
        )
        db_user.set_embeddings(user.embeddings)

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

        sql = select(db_User)

        filters = []
        if id_:
            filters.append(db_User.id == str(id_))
        if username:
            filters.append(db_User.username == username)

        sql = sql.filter(or_(*filters))

        user = await self.session.execute(sql)
        user = user.scalars().one_or_none()

        if user:
            return User(**user.dict(), embeddings=user.get_embeddings())
        
    async def list(self, offset: int, limit: int = 10) -> List[User]:
        sql = select(db_User).offset(offset).limit(limit)
        users = await self.session.execute(sql)
        users = users.scalars().all()

        return [User(**user.dict(), embeddings=user.get_embeddings()) for user in users]


    async def update(self, user: User):
        # Юзаем sqlite, а он не может в UUID так что вот так вот
        sql = select(db_User).where(db_User.id == str(user.id))
        _user = await self.session.execute(sql)
        _user = _user.scalars().one_or_none()

        if _user is None:
            raise UpdateError("User не найден")

        if user.username:
            logger.debug(
                f"Изменяем имя пользователя {_user.username} на {user.username}"
            )
            _user.username = user.username

        if user.embeddings:
            logger.debug(
                f"Изменяем embeddings пользователя {_user.embeddings} на {user.embeddings}"
            )
            _user.set_embeddings(user.embeddings)

        self.session.add(_user)
        await self.save()

    async def save(self):
        try:
            logger.debug("Производится commit")
            await self.session.commit()
        except IntegrityError as error:
            logger.error(error)
            raise UsernameError("Username уже занят")
        except Exception as error:
            logger.error(error)
            await self.session.rollback()
