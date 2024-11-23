import imghdr

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from loguru import logger
import numpy as np
import cv2

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
async def embedding_face_authentication(
    _user: schema.AuthFaceUser, session: AsyncSession = Depends(get_db_session)
) -> User:
    """Аунтификация пользователя по embedding"""
    logger.debug("Аунтификация пользователя по лицу")

    user_repo = UserRepository(session=session)
    embedding_repo = EmbeddingRepository(session=session)
    auth = AuthService(user_repository=user_repo, embedding_repository=embedding_repo)

    try:
        user = await auth.face_authentication(embedding=_user.embedding)
        return user
    except AuthFaceError:
        raise HTTPException(status_code=401, detail="Лицо не найдено в базе данных")
    except ServiceDataBaseError:
        raise HTTPException(status_code=503, detail="База данных недоступна")
    
@router.post("/", response_model=schema.VectorEmbedding)
async def image_face_authentication(file: UploadFile = File(...)):
    """Аунтификация пользователя по image"""
    
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Загруженный файл не является изображением.")

    contents = await file.read()
    
    if imghdr.what(None, contents) is None:
        raise HTTPException(status_code=400, detail="Загруженный файл не является изображением.")

    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(status_code=400, detail="Не удалось декодировать изображение.")

    embedding = reco.get_embedding(img=image)
    
    
    return Embedding(vector=embedding.tolist())
