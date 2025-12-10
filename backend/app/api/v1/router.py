from fastapi import APIRouter

from app.core.config import settings
from app.api.v1.endpoints import user, login, private, utils, domain, feature_model

# ========================================================================
#           --- ROUTER PRINCIPAL PARA LA API RESTful V1 ---
# ========================================================================
api_router = APIRouter()

# Incluir cada router 
api_router.include_router(utils.router)  # Root
api_router.include_router(login.router)
api_router.include_router(user.router)
api_router.include_router(domain.router)
api_router.include_router(feature_model.router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
