from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import APIKeyHeader
from loguru import logger

from app.log import configure_logging
from app.settings import settings
from app.repository.dependencies import get_db_session
from app.repository.repository import UserRepository
from app.services.users.users import UserService
from app.services.exceptions import (
    UserUpdateError,
    ServiceDataBaseError,
    EmbeddingVectorSizeError,
    ServiceUsernameError,
)
from app.services.models.user import User
from app.services.interface.user import IUser
from app.web.api.user import schema

configure_logging()

auth_header = APIKeyHeader(name="Authorization", auto_error=False)

router = APIRouter()

#  Тут везде кастыль который нужен для того что бы из swagger ui можно было делать авторизованные запросы.
# Возможно если вручную прописать спецификацию, добавив туда зависимость заголовка Authorization,
# то возможно swagger ui поймет что нужно добавлять заголовок, и + добавит возможность его добавить через свой ui


@router.get("/", response_model=List[schema.Users], status_code=200)
async def list_users(
    request: Request,
    offset: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_db_session),
    token: str = Depends(auth_header),
) -> List[IUser]:
    """Получение списка с дынными о пользователях"""
    logger.debug("Получаем список пользователей")
    logger.debug(request.state.user_id)  # Тут id который был присвоен в middleware

    if limit <= 0 or offset < 0:
        raise HTTPException(
            status_code=400, detail="offset и limit должны быть положительны"
        )
    
    try:
        repo = UserRepository(session=session)
        user_service = UserService(user_repository=repo)

        users = await user_service.lst(offset=offset, limit=limit)

        return users
    except ServiceDataBaseError:
        raise HTTPException(status_code=503, detail="База данных недоступна")


@router.get("/{id_:str}", response_model=schema.User, status_code=200)
async def user_info(
    id_: UUID,
    session: AsyncSession = Depends(get_db_session),
    token: str = Depends(auth_header),
) -> IUser:
    """Получение дынных о пользователе"""
    logger.debug(f"Получаем данные пользователя c id {id_}")

    try:
        repo = UserRepository(session=session)
        user_service = UserService(user_repository=repo)

        user = await user_service.show(id_=id_)
        if user:
            return user
        raise HTTPException(status_code=404, detail="Не найдено")
    except ServiceDataBaseError:
        raise HTTPException(status_code=503, detail="База данных недоступна")


@router.put("/{id_:str}", status_code=204)
async def update(
    id_: UUID,
    _user: schema.UpdateUser,
    session: AsyncSession = Depends(get_db_session),
    token: str = Depends(auth_header),
):
    """Изменение данных о пользователе"""
    logger.debug(f"Обновляем данные пользователя c id {id_}")

    try:
        repo = UserRepository(session=session)
        user_service = UserService(user_repository=repo)
        user = User(id=id_, username=_user.username, faces=_user.embeddings)

        await user_service.update(user)
    except UserUpdateError:
        raise HTTPException(status_code=404, detail="Не найдено")
    except ServiceUsernameError:
        raise HTTPException(status_code=401, detail="Такой логин уже есть")
    except ServiceDataBaseError:
        raise HTTPException(status_code=503, detail="База данных недоступна")
    except EmbeddingVectorSizeError:
        raise HTTPException(
            status_code=400, detail="Вы использовали неверный размер вектора"
        )
