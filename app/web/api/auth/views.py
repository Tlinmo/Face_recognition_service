from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger


from app.log import configure_logging
from app.repository.dependencies import get_db_session
from app.repository.repository import EmbeddingRepository, UserRepository
from app.services.auth.auth import AuthService
from app.services.users.user import User
from app.services.exceptions import (
    AuthUsernameError,
    AuthPasswordError,
    AuthFaceError,
    ServiceDataBaseError,
)
from app.web.api.auth import schema

configure_logging()

router = APIRouter()


@router.post("/create", status_code=201)
async def register(
    _user: schema.UserCreate, session: AsyncSession = Depends(get_db_session)
) -> str:
    """Cоздание пользователя"""

    logger.debug("Создание пользователя")

    user_repo = UserRepository(session=session)
    embedding_repo = EmbeddingRepository(session=session)
    auth = AuthService(user_repository=user_repo, embedding_repository=embedding_repo)
    user = User(
        username=_user.username,
        hashed_password=User.hash_password(_user.password),
        embeddings=_user.embeddings,
    )
    try:
        token = await auth.register(user)
        return token
    except AuthUsernameError:
        raise HTTPException(status_code=409, detail="Такой пользователь уже есть")
    except ServiceDataBaseError:
        raise HTTPException(status_code=503, detail="База данных недоступна")


@router.post("/login", status_code=200)
async def authentication(
    _user: schema.AuthUser, session: AsyncSession = Depends(get_db_session)
) -> str:
    """Авторизация пользователя"""
    logger.debug("Авторизация пользователя")

    user_repo = UserRepository(session=session)
    embedding_repo = EmbeddingRepository(session=session)
    auth = AuthService(user_repository=user_repo, embedding_repository=embedding_repo)

    try:
        token = await auth.authentication(
            username=_user.username, password=_user.password
        )
        return token
    except AuthPasswordError:
        raise HTTPException(status_code=401, detail="Пароль не верный")
    except AuthUsernameError:
        raise HTTPException(status_code=401, detail="Логин не верный")
    except ServiceDataBaseError:
        raise HTTPException(status_code=503, detail="База данных недоступна")


@router.post("/face", response_model=schema.FaceUser, status_code=200)
async def face_authentication(
    _user: schema.AuthFaceUser, session: AsyncSession = Depends(get_db_session)
) -> User:
    """Аунтификация пользователя по лицу"""
    logger.debug("Аунтификация пользователя по лицу")

    user_repo = UserRepository(session=session)
    embedding_repo = EmbeddingRepository(session=session)
    auth = AuthService(user_repository=user_repo, embedding_repository=embedding_repo)

    try:
        user = await auth.face_authentication(embedding=_user.embedding)
        for _embd in user.embeddings:
            logger.debug(f"{_embd.similarity} TEST")
            logger.debug(f"{_embd.similarity} TEST")
            logger.debug(f"{_embd.similarity} TEST")
            logger.debug(f"{_embd.similarity} TEST")
        return user
    except AuthFaceError:
        raise HTTPException(status_code=401, detail="Лицо не найдено в базе данных")
    except ServiceDataBaseError:
        raise HTTPException(status_code=503, detail="База данных недоступна")
