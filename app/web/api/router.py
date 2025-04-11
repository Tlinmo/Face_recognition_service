from fastapi.routing import APIRouter

from app.web.api import docs, monitoring, auth, user, recognition

api_router = APIRouter()
api_router.include_router(monitoring.router, prefix="/monitoring")
api_router.include_router(docs.router, prefix="/docs")
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(user.router, prefix="/users")
api_router.include_router(recognition.router, prefix="/ai")
