from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from starlette.requests import Request
from loguru import logger

from app.log import configure_logging

configure_logging()


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Create and get database session.

    :param request: current request.
    :yield: database session.
    """
    session: AsyncSession = request.app.state.db_session_factory()

    try:
        logger.debug("Выдается сессия базы данных")
        yield session
    except SQLAlchemyError as error:
        error_type = type(error)
        logger.error(f" {error_type} | {error}")

        await session.rollback()
    finally:
        logger.debug("Сессия базы данных закрывается")
        await session.close()
