"""
Endpoint para obtener estadísticas en tiempo real de un feature model.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import (
    AsyncFeatureModelVersionRepoDep,
    AsyncFeatureModelRepoDep,
    get_verified_user,
)
from app.schemas.feature_model_complete import FeatureModelStatistics

router = APIRouter(
    prefix="/feature-models",
    tags=["Feature Models - Statistics"],
    responses={
        404: {"description": "Feature model or version not found"},
        403: {"description": "Not enough permissions"},
    },
)


# ============================================================================
# IMPORTANTE: Las rutas más específicas (/latest/) deben ir ANTES que las
# rutas con parámetros variables (/{version_id}/) para evitar conflictos
# ============================================================================


@router.get(
    "/{model_id}/versions/latest/statistics",
    dependencies=[Depends(get_verified_user)],
    response_model=FeatureModelStatistics,
)
async def get_latest_feature_model_statistics(
    *,
    model_id: uuid.UUID,
    feature_model_repo: AsyncFeatureModelRepoDep,
    version_repo: AsyncFeatureModelVersionRepoDep,
) -> FeatureModelStatistics:
    """
    Obtener estadísticas de la última versión publicada de un feature model.

    Este endpoint es un atajo para obtener las estadísticas de la versión
    más reciente con estado PUBLISHED sin necesidad de conocer el version_id.

    **Caso de Uso**:
    - Dashboard principal que muestra métricas de la versión en producción
    - Reportes públicos basados en la versión estable
    - Integración con sistemas externos que solo consumen versiones publicadas

    Args:
        model_id: UUID del feature model
        feature_model_repo: Repository de feature models
        version_repo: Repository de versiones

    Returns:
        FeatureModelStatistics: Estadísticas de la última versión PUBLISHED

    Raises:
        HTTPException 404: Si no existe ninguna versión publicada

    Example:
        ```bash
        GET /api/v1/feature-models/{model_id}/versions/latest/statistics
        ```

    Note:
        - Solo considera versiones con estado PUBLISHED
        - Si hay múltiples versiones publicadas, devuelve la más reciente
        - Si solo hay versiones DRAFT o IN_REVIEW, retorna 404
    """
    from app.enums import ModelStatus

    # Verificar que el feature model existe
    feature_model = await feature_model_repo.get(model_id)
    if not feature_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature Model not found",
        )

    # Buscar la última versión publicada
    latest_version = None
    max_version_number = -1

    for version in feature_model.versions:
        if version.status == ModelStatus.PUBLISHED:
            if version.version_number > max_version_number:
                max_version_number = version.version_number
                latest_version = version

    if latest_version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No published version found for this Feature Model",
        )

    # Calcular estadísticas
    stats = await version_repo.get_statistics(latest_version.id)

    if stats is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not calculate statistics for this version",
        )

    return FeatureModelStatistics(**stats)


@router.get(
    "/{model_id}/versions/{version_id}/statistics",
    dependencies=[Depends(get_verified_user)],
    response_model=FeatureModelStatistics,
)
async def get_feature_model_statistics(
    *,
    model_id: uuid.UUID,
    version_id: uuid.UUID,
    feature_model_repo: AsyncFeatureModelRepoDep,
    version_repo: AsyncFeatureModelVersionRepoDep,
) -> FeatureModelStatistics:
    """
    Obtener estadísticas en tiempo real de un feature model.

    Este endpoint calcula y devuelve estadísticas actualizadas del feature model,
    incluyendo conteos de features, grupos, relaciones y profundidad del árbol.

    **Las estadísticas se calculan en tiempo real**, por lo que reflejan el estado
    actual del modelo incluso si se han realizado modificaciones recientes.

    **Caso de Uso**:
    - Mostrar dashboard con métricas del modelo
    - Validar complejidad antes de publicar una versión
    - Monitorear cambios durante la edición
    - Generar reportes de análisis del modelo

    Args:
        model_id: UUID del feature model
        version_id: UUID de la versión específica
        feature_model_repo: Repository de feature models
        version_repo: Repository de versiones

    Returns:
        FeatureModelStatistics: Estadísticas completas del modelo
            - total_features: Total de features en el modelo
            - mandatory_features: Número de features obligatorias
            - optional_features: Número de features opcionales
            - total_groups: Total de grupos (XOR + OR)
            - xor_groups: Grupos XOR (elegir exactamente una opción)
            - or_groups: Grupos OR (elegir una o más opciones)
            - total_relations: Total de relaciones entre features
            - requires_relations: Relaciones de prerequisito (A requiere B)
            - excludes_relations: Relaciones de exclusión (A excluye B)
            - total_constraints: Restricciones formales del modelo
            - total_configurations: Configuraciones válidas generadas
            - max_tree_depth: Profundidad máxima del árbol de features

    Raises:
        HTTPException 404: Si el feature model o la versión no existen
        HTTPException 403: Si el usuario no tiene permisos

    Performance:
        - Típico: 50-100ms para modelos pequeños (<100 features)
        - Moderado: 100-300ms para modelos medianos (100-500 features)
        - Grande: 300-800ms para modelos grandes (>500 features)

    Example:
        ```bash
        GET /api/v1/feature-models/{model_id}/versions/{version_id}/statistics
        ```

    Response Example:
        ```json
        {
            "total_features": 45,
            "mandatory_features": 32,
            "optional_features": 13,
            "total_groups": 5,
            "xor_groups": 3,
            "or_groups": 2,
            "total_relations": 18,
            "requires_relations": 15,
            "excludes_relations": 3,
            "total_constraints": 8,
            "total_configurations": 12,
            "max_tree_depth": 5
        }
        ```

    Note:
        Este endpoint NO usa caché ya que las estadísticas deben reflejar
        el estado actual del modelo en tiempo real. Si necesitas estadísticas
        pre-computadas y cacheadas, usa el endpoint `/complete` con
        `include_statistics=true`.
    """
    # Verificar que el feature model existe y está activo
    feature_model = await feature_model_repo.get(model_id)
    if not feature_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature Model not found",
        )

    if not feature_model.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feature Model is not active",
        )

    # Verificar que la versión existe y pertenece al modelo
    version = await version_repo.get(version_id)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature Model Version not found",
        )

    if version.feature_model_id != model_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Version does not belong to this Feature Model",
        )

    # Calcular estadísticas en tiempo real
    stats = await version_repo.get_statistics(version_id)

    if stats is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not calculate statistics for this version",
        )

    return FeatureModelStatistics(**stats)
