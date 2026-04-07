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
)
async def feature_model_analysis_summary(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: uuid.UUID = Path(..., description="Version UUID"),
    payload: AnalysisSummaryRequest,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> AnalysisSummaryResponse:
    version = await version_repo.get_complete_with_relations(
        version_id=version_id,
        include_resources=False,
    )

    if not version or version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

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
)
async def feature_model_analysis_compare(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: uuid.UUID = Path(..., description="Base Version UUID"),
    payload: CompareRequest,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> CompareResponse:
    base_version = await version_repo.get_complete_with_relations(
        version_id=version_id,
        include_resources=False,
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
)
async def feature_model_analysis_batch(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: uuid.UUID = Path(..., description="Version UUID"),
    payload: BatchAnalysisRequest,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> BatchAnalysisResponse:
    version = await version_repo.get(version_id)
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
        version_id=str(version_id),
        analysis_types=[t.value for t in (payload.analysis_types or [])],
        max_solutions=payload.max_solutions,
    )

    return BatchAnalysisResponse(task_id=str(task.id))


@router.post(
    "/{model_id}/versions/{version_id}/analysis/batch/bulk-configurations",
    response_model=TaskLaunchResponse,
    summary="Generación masiva asíncrona",
)
async def feature_model_bulk_configurations(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: uuid.UUID = Path(..., description="Version UUID"),
    payload: BulkConfigurationsRequest,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> TaskLaunchResponse:
    version = await version_repo.get(version_id)
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
        version_id=str(version_id),
        count=payload.count,
        strategy=payload.strategy,
        partial_selection=partial,
    )

    return TaskLaunchResponse(task_id=str(task.id))


@router.post(
    "/{model_id}/versions/{version_id}/analysis/batch/export-bundle",
    response_model=TaskLaunchResponse,
    summary="Exportación masiva asíncrona",
)
async def feature_model_export_bundle(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: uuid.UUID = Path(..., description="Version UUID"),
    payload: ExportBundleRequest,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> TaskLaunchResponse:
    version = await version_repo.get(version_id)
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
        version_id=str(version_id),
        formats=payload.formats,
    )

    return TaskLaunchResponse(task_id=str(task.id))


@router.post(
    "/{model_id}/versions/{version_id}/analysis/batch/compare",
    response_model=TaskLaunchResponse,
    summary="Comparación asíncrona de versiones",
)
async def feature_model_compare_batch(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: uuid.UUID = Path(..., description="Base Version UUID"),
    payload: CompareBatchRequest,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> TaskLaunchResponse:
    base_version = await version_repo.get(version_id)
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
        base_version_id=str(version_id),
        target_version_id=str(payload.target_version_id),
        analysis_types=[t.value for t in (payload.analysis_types or [])],
        max_solutions=payload.max_solutions,
    )

    return TaskLaunchResponse(task_id=str(task.id))


@router.post(
    "/{model_id}/versions/{version_id}/analysis/batch/recompute-stats",
    response_model=TaskLaunchResponse,
    summary="Recomputar estadísticas asíncronas",
)
async def feature_model_recompute_stats(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: uuid.UUID = Path(..., description="Version UUID"),
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> TaskLaunchResponse:
    version = await version_repo.get(version_id)
    if not version or version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

    if (
        version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
        and not version.feature_model.is_active
    ):
        raise ForbiddenException(detail="Not enough permissions to recompute stats")

    from app.tasks.feature_model_analysis import recompute_version_statistics

    task = recompute_version_statistics.delay(version_id=str(version_id))
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
