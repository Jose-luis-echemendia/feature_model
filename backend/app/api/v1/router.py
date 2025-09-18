from fastapi import APIRouter

from app.core.config import settings
from app.api.v1.endpoints import user, login, private, utils

api_router = APIRouter()

# Incluir cada router con su prefijo y etiquetas
api_router.include_router(utils.router, tags=["Utils"])  # Root
api_router.include_router(login.router, tags=["Login"])
api_router.include_router(user.router, tags=["Users"])


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router, tags=["Private"])
