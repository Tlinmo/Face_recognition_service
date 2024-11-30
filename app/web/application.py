from importlib import metadata
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from fastapi.staticfiles import StaticFiles
from starlette import status
from starlette.middleware.base import (
    RequestResponseEndpoint,
    BaseHTTPMiddleware,
)
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from loguru import logger
import jwt

from app.log import configure_logging
from app.web.api.router import api_router
from app.web.lifespan import lifespan_setup
from app.settings import settings
from app.services.auth.auth import decode_and_validate_token

configure_logging()

APP_ROOT = Path(__file__).parent.parent


class AuthorizeRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if not settings.auth_on:
            request.state.user_id = "73e509f9-d46e-46b9-8002-75e44d5be09e"  # Теперь он моя лабораторная крыса
            return await call_next(request)

        logger.debug(request.url.path)

        # Разрешаем ендпоинты, которые будет доступны без авторизации
        open_endpoints = [
            "/api/docs",
            "/api/openapi.json",
            "/static/docs",
            "/api/auth",
            "/api/ai",
        ]

        if any(request.url.path.startswith(endpoint) for endpoint in open_endpoints):
            return await call_next(request)

        if request.method == "OPTIONS":
            return await call_next(request)

        bearer_token = request.headers.get("Authorization")
        if not bearer_token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Missing access token",
                },
            )
        try:
            auth_token = bearer_token.split()[1].strip()
            token_payload = decode_and_validate_token(auth_token)
            request.state.user_id = token_payload["sub"]
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token has expired"},
            )
        except jwt.InvalidTokenError as e:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": str(e)},
            )
        except Exception as error:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": str(error)},
            )

        return await call_next(request)


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    configure_logging()
    app = FastAPI(
        title="app",
        version=metadata.version("app"),
        lifespan=lifespan_setup,
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    # Add middleware
    app.add_middleware(AuthorizeRequestMiddleware)

    # Adds static directory.
    # This directory is used to access swagger files.
    app.mount("/static", StaticFiles(directory=APP_ROOT / "static"), name="static")

    return app
