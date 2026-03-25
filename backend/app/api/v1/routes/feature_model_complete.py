"""
Endpoint para obtener la estructura completa de un Feature Model.
Optimizado para renderizado de árbol en frontend.
"""

import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from fastapi_cache.decorator import cache

from sqlmodel import select

from app.api.deps import (
    AsyncCurrentUser,
    get_verified_user,
    AsyncFeatureModelVersionRepoDep,
)
from app.models import FeatureModelVersion
from app.schemas import FeatureModelCompleteResponse
from app.services.feature_model import FeatureModelTreeBuilder
from app.enums import ModelStatus
from app.exceptions import (
    NoPublishedVersionException,
    FeatureModelVersionNotFoundException,
    InvalidTreeStructureException,
    UnauthorizedException,
    ForbiddenException,
    BusinessLogicException,
)


router = APIRouter(
    prefix="/feature-models",
    tags=["Feature Models - Complete Structure"],
    dependencies=[Depends(get_verified_user)],
)


# ============================================================================
# IMPORTANTE: Las rutas más específicas (/latest/) deben ir ANTES que las
# rutas con parámetros variables (/{version_id}/) para evitar conflictos
# ============================================================================


@cache(
    expire=lambda version: (
        3600
        if version.status == ModelStatus.PUBLISHED
        else 300 if version.status == ModelStatus.DRAFT else 1800
    )
)
@router.get(
    "/{model_id}/versions/latest/complete/",
    response_model=FeatureModelCompleteResponse,
    summary="Get complete structure of the latest published version",
    description="""
    Convenience endpoint to get the complete structure of the latest PUBLISHED
    version of a feature model without needing to know the version ID.
    
    This endpoint automatically finds the most recent published version and
    returns its complete structure.
    
    **Use this when:**
    - You want to display the "current" version of a model
    - You don't want to track version IDs in your frontend
    - You always want the latest published content
    
    **Note:** Only returns PUBLISHED versions. If no published version exists,
    returns 404.
    """,
)
async def get_latest_complete_feature_model(
    *,
    model_id: uuid.UUID,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
    include_resources: bool = Query(default=True),
    include_statistics: bool = Query(default=True),
) -> FeatureModelCompleteResponse:
    """Get the complete structure of the latest published version."""
    # Buscar la última versión publicada
    stmt = (
        select(FeatureModelVersion)
        .where(
            FeatureModelVersion.feature_model_id == model_id,
            FeatureModelVersion.status == ModelStatus.PUBLISHED,
        )
        .order_by(FeatureModelVersion.version_number.desc())
        .limit(1)
    )

    result = await version_repo.session.execute(stmt)
    latest_version = result.scalar_one_or_none()

    if not latest_version:
        raise NoPublishedVersionException(model_id=str(model_id))

    # Redirigir a la función principal
    return await get_complete_feature_model(
        model_id=model_id,
        version_id=latest_version.id,
        version_repo=version_repo,
        current_user=current_user,
        include_resources=include_resources,
        include_statistics=include_statistics,
    )


@cache(
    expire=lambda version: (
        3600
        if version.status == ModelStatus.PUBLISHED
        else 300 if version.status == ModelStatus.DRAFT else 1800
    )
)
@router.get(
    "/{model_id}/versions/{version_id}/complete/",
    response_model=FeatureModelCompleteResponse,
    summary="Get complete feature model structure for tree rendering",
    description="""
    Retrieve the complete feature model structure in a single request.
    
    This endpoint returns EVERYTHING needed to render the feature model tree
    in the frontend, including:
    - Hierarchical feature structure (nested tree)
    - Groups (XOR, OR) with cardinalities
    - Relations (REQUIRES, EXCLUDES) between features
    - Formal constraints with expressions
    - Associated resources and tags
    - Pre-computed statistics
    
    **Performance Characteristics:**
    - Single optimized database query with eager loading
    - Aggressive caching for published versions (1 hour)
    - Typical response time: 200-500ms for models with <2000 features
    - Response size: ~10-50KB for typical models
    
    **Caching Strategy:**
    - PUBLISHED versions: Cached for 1 hour (immutable)
    - IN_REVIEW versions: Cached for 30 minutes
    - DRAFT versions: Cached for 5 minutes
    
    **When to use this endpoint:**
    - Initial load of feature model tree viewer
    - Displaying complete model structure
    - Exporting model to external formats
    
    **When NOT to use this endpoint:**
    - Very large models (>5000 features) - use paginated endpoint instead
    - Editing individual features - use specific CRUD endpoints
    - Real-time collaborative editing - use WebSocket API
    """,
    responses={
        200: {
            "description": "Complete feature model structure",
            "content": {
                "application/json": {
                    "example": {
                        "feature_model": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "Ingeniería en Ciencias Informáticas",
                            "domain_name": "Ingeniería Informática",
                        },
                        "tree": {
                            "name": "Plan de Estudios",
                            "type": "MANDATORY",
                            "children": [],
                        },
                        "statistics": {"total_features": 45, "max_tree_depth": 5},
                    }
                }
            },
        },
        404: {"description": "Feature model or version not found"},
        403: {"description": "Not enough permissions to view this model"},
    },
)
async def get_complete_feature_model(
    *,
    model_id: uuid.UUID,
    version_id: uuid.UUID,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
    include_resources: bool = Query(
        default=True,
        description="Include full resource objects in the response. Set to false to reduce payload size.",
    ),
    include_statistics: bool = Query(
        default=True,
        description="Include pre-computed statistics. Set to false for faster response.",
    ),
) -> FeatureModelCompleteResponse:
    """
    Get complete feature model structure for tree rendering.

    This is the main endpoint for retrieving the full feature model structure.
    It returns a nested tree with all features, groups, relations, and constraints
    in a format optimized for frontend tree rendering components.
    """
    # Verificar que el usuario está autenticado
    if not current_user:
        raise UnauthorizedException(detail="Authentication required")

    # Obtener la versión completa con todas las relaciones
    version = await version_repo.get_complete_with_relations(
        version_id=version_id, include_resources=include_resources
    )

    if not version:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

    # Verificar que la versión pertenece al feature model solicitado
    if version.feature_model_id != model_id:
        raise BusinessLogicException(
            detail="Version does not belong to the specified feature model"
        )

    # Verificar permisos (el modelo debe estar activo o el usuario debe ser owner/admin)
    feature_model = version.feature_model
    if not feature_model.is_active:
        # Solo el owner o superuser pueden ver modelos inactivos
        if feature_model.owner_id != current_user.id and not current_user.is_superuser:
            raise ForbiddenException(
                detail="This feature model is inactive and you don't have permission to view it"
            )

    # Determinar si viene del caché y cuándo expira
    cached = False  # El decorador @cache manejará esto
    cache_expires_at = None

    # Calcular tiempo de expiración del caché según el estado
    if version.status == ModelStatus.PUBLISHED:
        cache_expires_at = datetime.utcnow() + timedelta(hours=1)
    elif version.status == ModelStatus.IN_REVIEW:
        cache_expires_at = datetime.utcnow() + timedelta(minutes=30)
    else:  # DRAFT
        cache_expires_at = datetime.utcnow() + timedelta(minutes=5)

    # Construir la respuesta usando el TreeBuilder
    builder = FeatureModelTreeBuilder(
        version=version, include_resources=include_resources
    )

    response = builder.build_complete_response(
        cached=cached, cache_expires_at=cache_expires_at
    )

    # Si no se solicitan estadísticas, eliminarlas
    if not include_statistics:
        response.statistics = None

    return response
