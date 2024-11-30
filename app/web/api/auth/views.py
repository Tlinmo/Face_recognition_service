from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from app.log import configure_logging
from app.repository.dependencies import get_db_session
from app.repository.repository import FaceRepository, UserRepository
from app.services.auth.auth import AuthService
from app.services.interface.user import IUser
from app.services.models.user import User
from app.services.models.face import Face
from app.services.exceptions import (
    ServiceUsernameError,
    AuthPasswordError,
    AuthFaceError,
    ServiceDataBaseError,
    EmbeddingVectorSizeError,
)
from app.web.api.auth import schema


configure_logging()

router = APIRouter()


@router.post("/create", status_code=201, response_model=schema.TokenResponse)
async def register(
    _user: schema.UserCreate, session: AsyncSession = Depends(get_db_session)
):
    """Cоздание пользователя"""

    logger.debug("Создание пользователя")

    try:
        user_repo = UserRepository(session=session)
        face_repo = FaceRepository(session=session)
        auth = AuthService(user_repository=user_repo, face_repository=face_repo)
        user = User(
            username=_user.username,
            hashed_password=User.hash_password(_user.password),
            faces=_user.embeddings,
        )
        token = await auth.register(user)
        return {
            "access_token": token,
            "token_type": "Bearer",
        }

    except ServiceUsernameError:
        raise HTTPException(status_code=409, detail="Такой пользователь уже есть")
    except ServiceDataBaseError:
        raise HTTPException(status_code=503, detail="База данных недоступна")
    except EmbeddingVectorSizeError:
        raise HTTPException(status_code=400, detail="Вы использовали неверный размер вектора")


@router.post("/login", status_code=200, response_model=schema.TokenResponse)
async def authentication(
    _user: schema.AuthUser, session: AsyncSession = Depends(get_db_session)
):
    """Авторизация пользователя"""
    logger.debug("Авторизация пользователя")

    try:
        user_repo = UserRepository(session=session)
        face_repo = FaceRepository(session=session)
        auth = AuthService(user_repository=user_repo, face_repository=face_repo)

        token = await auth.authentication(
            username=_user.username, password=_user.password
        )
        return {
            "access_token": token,
            "token_type": "Bearer",
        }
    except AuthPasswordError:
        raise HTTPException(status_code=401, detail="Пароль не верный")
    except ServiceUsernameError:
        raise HTTPException(status_code=401, detail="Логин не верный")
    except ServiceDataBaseError:
        raise HTTPException(status_code=503, detail="База данных недоступна")


@router.post("/face", response_model=schema.FaceUser, status_code=200)
async def face_embeddings_authentication(
    _user: schema.AuthFaceUser, session: AsyncSession = Depends(get_db_session)
):
    """Аунтификация пользователя по Face"""
    logger.debug("Аунтификация пользователя по лицу")

    try:
        user_repo = UserRepository(session=session)
        face_repo = FaceRepository(session=session)
        auth = AuthService(user_repository=user_repo, face_repository=face_repo)
        face = Face(embedding=_user.embedding)
        user = await auth.face_authentication(face=face)
        return user
    except AuthFaceError:
        raise HTTPException(status_code=401, detail="Лицо не найдено в базе данных")
    except ServiceDataBaseError:
        raise HTTPException(status_code=503, detail="База данных недоступна")
    except EmbeddingVectorSizeError:
        raise HTTPException(status_code=400, detail="Вы использовали неверный размер вектора")
