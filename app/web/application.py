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

from app.log import configure_logging
from app.web.api.router import api_router
from app.web.lifespan import lifespan_setup
from app.settings import settings

configure_logging()

APP_ROOT = Path(__file__).parent.parent


class AuthorizeRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not settings.auth_on:
            request.state.user_id = "73e509f9-d46e-46b9-8002-75e44d5be09e" # Теперь он моя лабораторная крыса
            return await call_next(request)

        logger.debug(request.url.path)
        
        # Разрешаем ендпоинты, которые будет доступны без авторизации
        if request.url.path.startswith("/api/docs"):
            return await call_next(request)

        if request.url.path.startswith("/api/openapi.json"):
            return await call_next(request)
        
        if request.url.path.startswith("/api/auth"):
            return await call_next(request)
        
        if request.url.path.startswith("/api/ai"):
            return await call_next(request)
        
        if request.method == "OPTIONS":
            return await call_next(request)
        
        bearer_token = request.headers.get("Authorization")
        if not bearer_token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Missing access token",
                    "body": "Missing access token",
                },
            )
        try:
            auth_token = bearer_token.split()[1].strip()
            token_payload = f"Как будто тут параментры токена {auth_token}"
        except Exception as error:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                  "detail": str(error),
                  "body": str(error),  
                },
            )
        else:
            request.state.user_id = f"{token_payload} и из них вытащили id юзера"
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
