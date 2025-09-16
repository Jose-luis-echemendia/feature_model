from fastapi import APIRouter

from app.core.config import settings
from app.api.v1.endpoints import items, login, private, users, utils, appointments

api_router = APIRouter()

# Incluir cada router con su prefijo y etiquetas
# Esto agrupará las rutas en la documentación de Swagger UI
api_router.include_router(login.router, tags=["Login"])
api_router.include_router(users.router, tags=["Users"])
api_router.include_router(items.router, tags=["Items"])
api_router.include_router(utils.router, tags=["Utils"]) # Root
api_router.include_router(appointments.router, tags=["Appointments"]) #  prefix="/appointments",


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router, tags=["Private"])