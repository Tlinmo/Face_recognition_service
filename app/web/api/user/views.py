from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger


from app.log import configure_logging
from app.repository.dependencies import get_db_session
from app.repository.repository import UserRepository
from app.services.users.users import UserService
from app.services.exceptions import UserUpdateError, ServiceDataBaseError
from app.services.users.user import User
from app.web.api.user import schema

configure_logging()

router = APIRouter()


@router.get("/", response_model=List[schema.Users], status_code=200)
async def list_users(
    offset: int = 0, limit: int = 10, session: AsyncSession = Depends(get_db_session)
) -> List[User]:
    """Получение списка с дынными о пользователях"""
    logger.debug("Получаем список пользователей")

    repo = UserRepository(session=session)
    user_service = UserService(user_repository=repo)

    try:
        users = await user_service.lst(offset=offset, limit=limit)

        return users
    except ServiceDataBaseError:
        raise HTTPException(status_code=503, detail="База данных недоступна")


@router.get("/{id_:str}", response_model=schema.User, status_code=200)
async def user_info(id_: UUID, session: AsyncSession = Depends(get_db_session)) -> User:
    """Получение дынных о пользователе"""
    logger.debug(f"Получаем данные пользователя c id {id_}")

    repo = UserRepository(session=session)
    user_service = UserService(user_repository=repo)

    try:
        user = await user_service.show(id_=id_)
        if user:
            return user
        raise HTTPException(status_code=404, detail="Не найдено")
    except ServiceDataBaseError:
        raise HTTPException(status_code=503, detail="База данных недоступна")


@router.put("/{id_:str}", status_code=204)
async def update(
    id_: UUID, _user: schema.UpdateUser, session: AsyncSession = Depends(get_db_session)
):
    """Изменение данных о пользователе"""
    logger.debug(f"Обновляем данные пользователя c id {id_}")

    repo = UserRepository(session=session)
    user_service = UserService(user_repository=repo)

    user = User(id=id_, username=_user.username, embeddings=_user.embeddings)

    try:
        await user_service.update(user)
    except UserUpdateError:
        raise HTTPException(status_code=404, detail="Не найдено")
    except ServiceDataBaseError:
        raise HTTPException(status_code=503, detail="База данных недоступна")
