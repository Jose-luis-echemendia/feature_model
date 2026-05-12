"""Endpoints de análisis avanzado para Feature Models con soporte UVL/Flamapy."""

import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field

from app.api.deps import (
    AsyncCurrentUser,
    AsyncFeatureModelVersionRepoDep,
    get_verified_user,
)
from app.api.utils import resolve_version_id_or_latest
from app.enums import AnalysisType
from app.exceptions import FeatureModelVersionNotFoundException, ForbiddenException
from app.services.feature_model.fm_analysis_facade import (
    analyze_version,
    compare_versions,
)

router = APIRouter(
    prefix="/feature-models",
    tags=["Feature Models - Analysis"],
    dependencies=[Depends(get_verified_user)],
)


async def _get_complete_version(
    *,
    model_id: uuid.UUID,
    version_identifier: str,
    version_repo: AsyncFeatureModelVersionRepoDep,
):
    resolved_version_id = await resolve_version_id_or_latest(
        version_identifier,
        model_id,
        version_repo,
    )
    version = await version_repo.get_complete_with_relations(
        version_id=resolved_version_id,
        include_resources=False,
    )
    if not version or version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_identifier))
    return version


class AnalysisSummaryRequest(BaseModel):
    analysis_types: Optional[list[AnalysisType]] = Field(
        default=None,
        description="Tipos de análisis estructural a ejecutar (None = todos).",
    )
    max_solutions: int = Field(default=100, ge=1, le=1000)
    include_uvl_validation: bool = True


class AnalysisSummaryResponse(BaseModel):
    satisfiable: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    dead_features: list[str] = Field(default_factory=list)
    core_features: list[str] = Field(default_factory=list)
    commonality: dict[str, float] = Field(default_factory=dict)
    atomic_sets: list[list[str]] = Field(default_factory=list)
    estimated_configurations: int
    truncated: bool
    complexity_metrics: dict[str, Any] = Field(default_factory=dict)
    uvl_validation: Optional[dict[str, Any]] = None
    flamapy_engine_used: bool = False


class CompareRequest(BaseModel):
    target_version_id: uuid.UUID
    analysis_types: Optional[list[AnalysisType]] = Field(default=None)
    max_solutions: int = Field(default=100, ge=1, le=1000)


class CompareResponse(BaseModel):
    base: AnalysisSummaryResponse
    target: AnalysisSummaryResponse
    delta: dict[str, Any]


class BatchAnalysisRequest(BaseModel):
    analysis_types: Optional[list[AnalysisType]] = Field(default=None)
    max_solutions: int = Field(default=100, ge=1, le=1000)


class BatchAnalysisResponse(BaseModel):
    task_id: str


class BulkConfigurationsRequest(BaseModel):
    count: int = Field(default=50, ge=1, le=1000)
    strategy: str = Field(default="sat_enum")
    partial_selection: Optional[dict[uuid.UUID, bool]] = None


class ExportBundleRequest(BaseModel):
    formats: Optional[list[str]] = None


class CompareBatchRequest(BaseModel):
    target_version_id: uuid.UUID
    analysis_types: Optional[list[AnalysisType]] = Field(default=None)
    max_solutions: int = Field(default=100, ge=1, le=1000)


class TaskLaunchResponse(BaseModel):
    task_id: str


@router.post(
    "/{model_id}/versions/{version_id}/analysis/summary",
    response_model=AnalysisSummaryResponse,
    summary="Análisis avanzado del modelo",
    description="""
    Ejecuta un análisis estructural completo del feature model para la versión indicada.

    Use cases:
    - Obtener resumen de satisfiability, features muertas/core y métricas de complejidad.
    - Validación UVL opcional y generación de métricas para reports.

    Permissions required: authenticated (owner or project contributor) or superuser.
    Performance: operación intensiva para modelos grandes; usar `max_solutions` para limitar coste.
    """,
    responses={
        200: {
            "description": "Resumen de análisis",
            "content": {
                "application/json": {
                    "example": {
                        "satisfiable": True,
                        "errors": [],
                        "warnings": [],
                        "dead_features": [],
                        "core_features": [],
                        "estimated_configurations": 12345,
                        "truncated": False,
                    }
                }
            },
        },
        400: {"description": "Solicitud inválida"},
        404: {"description": "Versión del modelo no encontrada"},
        403: {"description": "Acceso denegado"},
    },
)
async def feature_model_analysis_summary(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: str = Path(..., description="Version UUID or the literal 'latest'"),
    payload: AnalysisSummaryRequest,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> AnalysisSummaryResponse:
    version = await _get_complete_version(
        model_id=model_id,
        version_identifier=version_id,
        version_repo=version_repo,
    )

    if (
        version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
        and not version.feature_model.is_active
    ):
        raise ForbiddenException(detail="Not enough permissions to analyze model")

    summary = analyze_version(
        version=version,
        analysis_types=payload.analysis_types,
        max_solutions=payload.max_solutions,
        include_uvl_validation=payload.include_uvl_validation,
    )
    return AnalysisSummaryResponse(**summary.__dict__)


@router.post(
    "/{model_id}/versions/{version_id}/analysis/compare",
    response_model=CompareResponse,
    summary="Comparar dos versiones del modelo",
    description="""
    Compara la versión base (path) con la versión objetivo indicada en el payload.

    Use cases: revisar cambios estructurales entre versiones, validar impactos en configuraciones.
    Permissions required: authenticated (owner or project contributor) o superuser.
    Performance: operación dependiente del tamaño del modelo y `max_solutions`.
    """,
    responses={
        200: {
            "description": "Resultado de la comparación",
            "content": {
                "application/json": {
                    "example": {
                        "base": {"satisfiable": True},
                        "target": {"satisfiable": True},
                        "delta": {
                            "dead_features_added": [],
                            "core_features_removed": [],
                        },
                    }
                }
            },
        },
        400: {"description": "Solicitud inválida"},
        404: {"description": "Alguna de las versiones no encontrada"},
        403: {"description": "Acceso denegado"},
    },
)
async def feature_model_analysis_compare(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: str = Path(
        ..., description="Base Version UUID or the literal 'latest'"
    ),
    payload: CompareRequest,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> CompareResponse:
    base_version = await _get_complete_version(
        model_id=model_id,
        version_identifier=version_id,
        version_repo=version_repo,
    )
    target_version = await version_repo.get_complete_with_relations(
        version_id=payload.target_version_id,
        include_resources=False,
    )

    if not base_version or base_version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))
    if not target_version or target_version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(
            version_id=str(payload.target_version_id)
        )

    if (
        base_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
        and not base_version.feature_model.is_active
    ):
        raise ForbiddenException(detail="Not enough permissions to compare models")

    result = compare_versions(
        base_version=base_version,
        target_version=target_version,
        analysis_types=payload.analysis_types,
        max_solutions=payload.max_solutions,
    )

    return CompareResponse(
        base=AnalysisSummaryResponse(**result["base"].__dict__),
        target=AnalysisSummaryResponse(**result["target"].__dict__),
        delta=result["delta"],
    )


@router.post(
    "/{model_id}/versions/{version_id}/analysis/batch",
    response_model=BatchAnalysisResponse,
    summary="Análisis asíncrono (Celery)",
    description="""
    Lanza un job asíncrono que ejecuta el análisis y devuelve un `task_id` para consultar el estado.

    Use cases: análisis programados o pesados que deben ejecutarse en background.
    Permissions required: authenticated (owner or project contributor) o superuser.
    Notes: El resultado se consulta con `/analysis/tasks/{task_id}`.
    """,
    responses={
        200: {
            "description": "Análisis encolado",
            "content": {"application/json": {"example": {"task_id": "abcd-1234"}}},
        },
        400: {"description": "Solicitud inválida"},
        404: {"description": "Versión del modelo no encontrada"},
        403: {"description": "Acceso denegado"},
    },
)
async def feature_model_analysis_batch(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: str = Path(..., description="Version UUID or the literal 'latest'"),
    payload: BatchAnalysisRequest,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> BatchAnalysisResponse:
    resolved_version_id = await resolve_version_id_or_latest(
        version_id,
        model_id,
        version_repo,
    )
    version = await version_repo.get(resolved_version_id)
    if not version or version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

    if (
        version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
        and not version.feature_model.is_active
    ):
        raise ForbiddenException(detail="Not enough permissions to analyze model")

    from app.tasks.feature_model_analysis import run_feature_model_analysis

    task = run_feature_model_analysis.delay(
        model_id=str(model_id),
        version_id=str(resolved_version_id),
        analysis_types=[t.value for t in (payload.analysis_types or [])],
        max_solutions=payload.max_solutions,
    )

    return BatchAnalysisResponse(task_id=str(task.id))


@router.post(
    "/{model_id}/versions/{version_id}/analysis/batch/bulk-configurations",
    response_model=TaskLaunchResponse,
    summary="Generación masiva asíncrona",
    description="""
    Lanza una tarea para generar múltiples configuraciones válidas en background.

    Use cases: generación por lotes para dataset/benchmarking o export masivo.
    Performance: operación intensiva; controlar `count` para evitar sobrecarga.
    Permissions required: authenticated (owner) o superuser.
    """,
    responses={
        200: {
            "description": "Tarea encolada",
            "content": {"application/json": {"example": {"task_id": "task-1234"}}},
        },
        400: {"description": "Solicitud inválida"},
        404: {"description": "Versión del modelo no encontrada"},
        403: {"description": "Acceso denegado"},
    },
)
async def feature_model_bulk_configurations(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: str = Path(..., description="Version UUID or the literal 'latest'"),
    payload: BulkConfigurationsRequest,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> TaskLaunchResponse:
    resolved_version_id = await resolve_version_id_or_latest(
        version_id,
        model_id,
        version_repo,
    )
    version = await version_repo.get(resolved_version_id)
    if not version or version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

    if (
        version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
        and not version.feature_model.is_active
    ):
        raise ForbiddenException(
            detail="Not enough permissions to generate configurations"
        )

    from app.tasks.feature_model_analysis import generate_bulk_configurations

    partial = (
        {str(k): v for k, v in payload.partial_selection.items()}
        if payload.partial_selection
        else None
    )

    task = generate_bulk_configurations.delay(
        model_id=str(model_id),
        version_id=str(resolved_version_id),
        count=payload.count,
        strategy=payload.strategy,
        partial_selection=partial,
    )

    return TaskLaunchResponse(task_id=str(task.id))


@router.post(
    "/{model_id}/versions/{version_id}/analysis/batch/export-bundle",
    response_model=TaskLaunchResponse,
    summary="Exportación masiva asíncrona",
    description="""
    Lanza una tarea para exportar múltiples formatos del modelo (bundle) en background.

    Use cases: generar paquetes de artefactos (xml, uvl, dimacs) para compartir o análisis.
    Permissions required: authenticated (owner) o superuser.
    """,
    responses={
        200: {
            "description": "Tarea encolada para exportación",
            "content": {"application/json": {"example": {"task_id": "task-5678"}}},
        },
        400: {"description": "Solicitud inválida"},
        404: {"description": "Versión del modelo no encontrada"},
        403: {"description": "Acceso denegado"},
    },
)
async def feature_model_export_bundle(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: str = Path(..., description="Version UUID or the literal 'latest'"),
    payload: ExportBundleRequest,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> TaskLaunchResponse:
    resolved_version_id = await resolve_version_id_or_latest(
        version_id,
        model_id,
        version_repo,
    )
    version = await version_repo.get(resolved_version_id)
    if not version or version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

    if (
        version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
        and not version.feature_model.is_active
    ):
        raise ForbiddenException(detail="Not enough permissions to export bundle")

    from app.tasks.feature_model_analysis import export_feature_model_bundle

    task = export_feature_model_bundle.delay(
        model_id=str(model_id),
        version_id=str(resolved_version_id),
        formats=payload.formats,
    )

    return TaskLaunchResponse(task_id=str(task.id))


@router.post(
    "/{model_id}/versions/{version_id}/analysis/batch/compare",
    response_model=TaskLaunchResponse,
    summary="Comparación asíncrona de versiones",
    description="""
    Encola una tarea que compara la versión base con la objetivo y devuelve un `task_id`.

    Use cases: comparación programada entre ramas o releases.
    Permissions required: authenticated (owner) o superuser.
    """,
    responses={
        200: {
            "description": "Tarea de comparación encolada",
            "content": {"application/json": {"example": {"task_id": "task-9999"}}},
        },
        400: {"description": "Solicitud inválida"},
        404: {"description": "Alguna de las versiones no encontrada"},
        403: {"description": "Acceso denegado"},
    },
)
async def feature_model_compare_batch(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: str = Path(
        ..., description="Base Version UUID or the literal 'latest'"
    ),
    payload: CompareBatchRequest,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> TaskLaunchResponse:
    resolved_version_id = await resolve_version_id_or_latest(
        version_id,
        model_id,
        version_repo,
    )
    base_version = await version_repo.get(resolved_version_id)
    target_version = await version_repo.get(payload.target_version_id)

    if not base_version or base_version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))
    if not target_version or target_version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(
            version_id=str(payload.target_version_id)
        )

    if (
        base_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
        and not base_version.feature_model.is_active
    ):
        raise ForbiddenException(detail="Not enough permissions to compare models")

    from app.tasks.feature_model_analysis import compare_feature_model_versions

    task = compare_feature_model_versions.delay(
        model_id=str(model_id),
        base_version_id=str(resolved_version_id),
        target_version_id=str(payload.target_version_id),
        analysis_types=[t.value for t in (payload.analysis_types or [])],
        max_solutions=payload.max_solutions,
    )

    return TaskLaunchResponse(task_id=str(task.id))


@router.post(
    "/{model_id}/versions/{version_id}/analysis/batch/recompute-stats",
    response_model=TaskLaunchResponse,
    summary="Recomputar estadísticas asíncronas",
    description="""
    Encola una tarea para recomputar estadísticas derivadas del modelo (caches, métricas).

    Use cases: mantener métricas actualizadas tras cambios masivos en el modelo.
    Permissions required: authenticated (owner) o superuser.
    """,
    responses={
        200: {
            "description": "Tarea encolada para recomputar stats",
            "content": {"application/json": {"example": {"task_id": "task-stats-1"}}},
        },
        400: {"description": "Solicitud inválida"},
        404: {"description": "Versión del modelo no encontrada"},
        403: {"description": "Acceso denegado"},
    },
)
async def feature_model_recompute_stats(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: str = Path(..., description="Version UUID or the literal 'latest'"),
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> TaskLaunchResponse:
    resolved_version_id = await resolve_version_id_or_latest(
        version_id,
        model_id,
        version_repo,
    )
    version = await version_repo.get(resolved_version_id)
    if not version or version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

    if (
        version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
        and not version.feature_model.is_active
    ):
        raise ForbiddenException(detail="Not enough permissions to recompute stats")

    from app.tasks.feature_model_analysis import recompute_version_statistics

    task = recompute_version_statistics.delay(version_id=str(resolved_version_id))
    return TaskLaunchResponse(task_id=str(task.id))


@router.get(
    "/analysis/tasks/{task_id}",
    summary="Estado de análisis asíncrono",
)
async def feature_model_analysis_task_status(
    *,
    task_id: str,
) -> dict[str, Any]:
    from app.core.celery import celery_app

    async_result = celery_app.AsyncResult(task_id)
    if async_result is None:
        raise HTTPException(status_code=404, detail="Task not found")

    response: dict[str, Any] = {
        "task_id": task_id,
        "status": async_result.status,
    }
    if async_result.successful():
        response["result"] = async_result.result
    elif async_result.failed():
        response["error"] = str(async_result.result)
    return response
