from fastapi import APIRouter

from app.core.config import settings
from app.api.v1.routes import (
    health,
    user,
    login,
    private,
    utils,
    domain,
    # --- Estructuras básicas ---
    feature,
    feature_relation,
    feature_group,
    constraint,
    # --- FMs ---
    feature_model,
    feature_model_version,
    feature_model_complete,
    feature_model_statistics,
    feature_model_statistics_ws,
    feature_model_export,
    feature_model_uvl,
    validation,
)

# ========================================================================
#           --- ROUTER PRINCIPAL PARA LA API RESTful V1 ---
# ========================================================================
api_router = APIRouter()

# Incluir cada router
api_router.include_router(health.router)  # Health check
api_router.include_router(utils.router)  # Root
api_router.include_router(login.router)
api_router.include_router(user.router)
api_router.include_router(domain.router)
# --- Estructuras básicas ---
api_router.include_router(feature.router)
api_router.include_router(feature_relation.router)
api_router.include_router(feature_group.router)
api_router.include_router(constraint.router)
# --- FMs ---
api_router.include_router(feature_model.router)
api_router.include_router(feature_model_version.router)
api_router.include_router(feature_model_complete.router)
api_router.include_router(feature_model_statistics.router)
api_router.include_router(feature_model_statistics_ws.router)  # WebSocket
api_router.include_router(feature_model_export.router)  # Export
api_router.include_router(feature_model_uvl.router)  # UVL sync/edit
api_router.include_router(validation.router)  # Validations

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
