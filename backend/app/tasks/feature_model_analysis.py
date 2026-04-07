"""Tareas Celery para análisis y operaciones pesadas de Feature Models."""

from __future__ import annotations

import asyncio
import io
import json
import zipfile
from typing import Any, Optional

from app.core.celery import celery_app
from app.api.deps import SessionLocal
from app.repositories import FeatureModelVersionRepository
from app.enums import AnalysisType, ExportFormat, GenerationStrategy
from app.core.s3 import minio_client
from app.core.cache import cache_service
from app.services.feature_model import FeatureModelConfigurationGenerator
from app.services.feature_model.fm_analysis_facade import (
    analyze_version,
    compare_versions,
)
from app.services.feature_model.fm_logical_validator import FeatureModelLogicalValidator
from app.services.feature_model.fm_export import FeatureModelExportService


def _build_payload(
    version,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    features_payload: list[dict[str, Any]] = []
    relations_payload: list[dict[str, Any]] = []
    constraints_payload: list[dict[str, Any]] = []

    for feature in version.features:
        group_data = None
        if feature.group:
            group_data = {
                "group_type": (
                    feature.group.group_type.value
                    if hasattr(feature.group.group_type, "value")
                    else str(feature.group.group_type)
                ),
                "min_cardinality": feature.group.min_cardinality,
                "max_cardinality": feature.group.max_cardinality,
            }

        features_payload.append(
            {
                "id": str(feature.id),
                "name": feature.name,
                "type": (
                    feature.type.value
                    if hasattr(feature.type, "value")
                    else str(feature.type)
                ),
                "parent_id": str(feature.parent_id) if feature.parent_id else None,
                "group_id": str(feature.group_id) if feature.group_id else None,
                "group": group_data,
            }
        )

        if feature.parent_id:
            relation_type = (
                "mandatory"
                if (
                    feature.type.value
                    if hasattr(feature.type, "value")
                    else str(feature.type)
                )
                == "mandatory"
                else "optional"
            )
            relations_payload.append(
                {
                    "parent_id": str(feature.parent_id),
                    "child_id": str(feature.id),
                    "relation_type": relation_type,
                    "group_id": str(feature.group_id) if feature.group_id else None,
                    "group_type": (
                        group_data.get("group_type") if group_data else None
                    ),
                    "min_cardinality": (
                        group_data.get("min_cardinality") if group_data else None
                    ),
                    "max_cardinality": (
                        group_data.get("max_cardinality") if group_data else None
                    ),
                }
            )

    for constraint in version.constraints:
        constraints_payload.append(
            {
                "id": str(constraint.id),
                "expr_text": constraint.expr_text,
                "expr_cnf": constraint.expr_cnf,
            }
        )

    for relation in version.feature_relations:
        relation_type = (
            relation.type.value
            if hasattr(relation.type, "value")
            else str(relation.type)
        )
        if relation_type == "requires":
            expr = f"{relation.source_feature_id} REQUIRES {relation.target_feature_id}"
        elif relation_type == "excludes":
            expr = f"{relation.source_feature_id} EXCLUDES {relation.target_feature_id}"
        else:
            continue

        constraints_payload.append(
            {
                "id": str(relation.id),
                "expr_text": expr,
                "expr_cnf": None,
            }
        )

    return features_payload, relations_payload, constraints_payload


@celery_app.task(
    name="app.tasks.feature_model_analysis.run_feature_model_analysis", bind=True
)
def run_feature_model_analysis(
    self,
    *,
    model_id: str,
    version_id: str,
    analysis_types: list[str] | None = None,
    max_solutions: int = 100,
) -> dict[str, Any]:
    """Ejecuta análisis de un modelo en segundo plano y devuelve el resumen."""

    self.update_state(
        state="PROGRESS",
        meta={"step": "load_version", "percent": 10, "eta_seconds_estimate": None},
    )

    async def _run() -> dict[str, Any]:
        async def _set_progress(meta: dict[str, Any]) -> None:
            await cache_service.set_task_progress(self.request.id, meta)

        await cache_service.set_task_status(self.request.id, status="running")
        await _set_progress({"step": "load_version", "percent": 10})
        async with SessionLocal() as session:
            repo = FeatureModelVersionRepository(session)
            version = await repo.get_complete_with_relations(
                version_id=version_id,
                include_resources=False,
            )
            if not version:
                await cache_service.set_task_status(self.request.id, status="error")
                return {
                    "status": "error",
                    "error": "Feature model version not found",
                }
            if str(version.feature_model_id) != model_id:
                await cache_service.set_task_status(self.request.id, status="error")
                return {
                    "status": "error",
                    "error": "Version does not belong to model",
                }

            acquired = await cache_service.acquire_analysis_lock(version_id)
            if not acquired:
                await cache_service.set_task_status(
                    self.request.id, status="already_running"
                )
                return {
                    "status": "error",
                    "error": "Analysis already running for this version",
                }

            await cache_service.set_analysis_status(version_id, status="running")

            try:
                parsed_types = None
                if analysis_types:
                    parsed_types = [AnalysisType(t) for t in analysis_types]

                self.update_state(
                    state="PROGRESS",
                    meta={
                        "step": "analyze",
                        "percent": 70,
                        "eta_seconds_estimate": None,
                    },
                )
                await _set_progress({"step": "analyze", "percent": 70})
                summary = analyze_version(
                    version=version,
                    analysis_types=parsed_types,
                    max_solutions=max_solutions,
                    include_uvl_validation=True,
                )
                self.update_state(
                    state="PROGRESS",
                    meta={"step": "done", "percent": 100, "eta_seconds_estimate": 0},
                )
                await _set_progress({"step": "done", "percent": 100})
                await cache_service.set_analysis_status(version_id, status="done")
                await cache_service.set_task_status(self.request.id, status="done")
                return {
                    "status": "ok",
                    "result": summary.__dict__,
                }
            finally:
                await cache_service.release_analysis_lock(version_id)

    return asyncio.run(_run())


@celery_app.task(
    name="app.tasks.feature_model_analysis.generate_bulk_configurations", bind=True
)
def generate_bulk_configurations(
    self,
    *,
    model_id: str,
    version_id: str,
    count: int = 50,
    strategy: str = GenerationStrategy.SAT_ENUM.value,
    partial_selection: Optional[dict[str, bool]] = None,
) -> dict[str, Any]:
    """Genera configuraciones masivas para un modelo y devuelve un resumen."""

    self.update_state(
        state="PROGRESS",
        meta={"step": "load_version", "percent": 10, "eta_seconds_estimate": None},
    )

    async def _run() -> dict[str, Any]:
        async def _set_progress(meta: dict[str, Any]) -> None:
            await cache_service.set_task_progress(self.request.id, meta)

        await cache_service.set_task_status(self.request.id, status="running")
        await _set_progress({"step": "load_version", "percent": 10})
        async with SessionLocal() as session:
            repo = FeatureModelVersionRepository(session)
            version = await repo.get_complete_with_relations(
                version_id=version_id,
                include_resources=False,
            )
            if not version:
                return {"status": "error", "error": "Feature model version not found"}
            if str(version.feature_model_id) != model_id:
                return {"status": "error", "error": "Version does not belong to model"}

            features_payload, relations_payload, constraints_payload = _build_payload(
                version
            )
            generator = FeatureModelConfigurationGenerator()
            parsed_strategy = GenerationStrategy(strategy)
            self.update_state(
                state="PROGRESS",
                meta={
                    "step": "generate",
                    "count": count,
                    "percent": 70,
                    "eta_seconds_estimate": None,
                },
            )
            await _set_progress({"step": "generate", "count": count, "percent": 70})
            results = generator.generate_multiple_configurations(
                features=features_payload,
                relations=relations_payload,
                constraints=constraints_payload,
                count=count,
                diverse=True,
                strategy=parsed_strategy,
                partial_selection=partial_selection,
            )

            self.update_state(
                state="PROGRESS",
                meta={"step": "quality", "percent": 85, "eta_seconds_estimate": None},
            )
            await _set_progress({"step": "quality", "percent": 85})
            quality = generator.compute_quality_metrics(
                results, [str(f["id"]) for f in features_payload]
            )
            self.update_state(
                state="PROGRESS",
                meta={"step": "done", "percent": 100, "eta_seconds_estimate": 0},
            )
            await _set_progress({"step": "done", "percent": 100})
            await cache_service.set_task_status(self.request.id, status="done")
            return {
                "status": "ok",
                "result": {
                    "configurations": [r.__dict__ for r in results],
                    "quality": quality,
                },
            }

    return asyncio.run(_run())


@celery_app.task(
    name="app.tasks.feature_model_analysis.export_feature_model_bundle", bind=True
)
def export_feature_model_bundle(
    self,
    *,
    model_id: str,
    version_id: str,
    formats: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Exporta múltiples formatos y sube un bundle ZIP a MinIO."""

    self.update_state(
        state="PROGRESS",
        meta={"step": "load_version", "percent": 5, "eta_seconds_estimate": None},
    )

    async def _run() -> dict[str, Any]:
        async def _set_progress(meta: dict[str, Any]) -> None:
            await cache_service.set_task_progress(self.request.id, meta)

        await cache_service.set_task_status(self.request.id, status="running")
        await _set_progress({"step": "load_version", "percent": 5})
        async with SessionLocal() as session:
            repo = FeatureModelVersionRepository(session)
            version = await repo.get_complete_with_relations(
                version_id=version_id,
                include_resources=False,
            )
            if not version:
                return {"status": "error", "error": "Feature model version not found"}
            if str(version.feature_model_id) != model_id:
                return {"status": "error", "error": "Version does not belong to model"}

            export_formats = formats or ["uvl", "json", "dimacs"]
            exporter = FeatureModelExportService(version)

            bundle = io.BytesIO()
            with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
                total = len(export_formats)
                for fmt in export_formats:
                    percent = int(((export_formats.index(fmt) + 1) / total) * 70)
                    self.update_state(
                        state="PROGRESS",
                        meta={
                            "step": "export",
                            "format": fmt,
                            "total": total,
                            "percent": 10 + percent,
                            "eta_seconds_estimate": None,
                        },
                    )
                    await _set_progress(
                        {
                            "step": "export",
                            "format": fmt,
                            "total": total,
                            "percent": 10 + percent,
                        }
                    )
                    export_format = ExportFormat(fmt)
                    content = exporter.export(export_format)
                    zipf.writestr(f"{version_id}.{fmt}", content)

            self.update_state(
                state="PROGRESS",
                meta={"step": "upload", "percent": 90, "eta_seconds_estimate": None},
            )
            await _set_progress({"step": "upload", "percent": 90})
            object_name = await minio_client.upload_feature_model_export(
                version_id=version_id,
                export_bytes=bundle.getvalue(),
                fmt="zip",
                content_type="application/zip",
            )
            self.update_state(
                state="PROGRESS",
                meta={"step": "done", "percent": 100, "eta_seconds_estimate": 0},
            )
            await _set_progress({"step": "done", "percent": 100})
            await cache_service.set_task_status(self.request.id, status="done")
            return {
                "status": "ok",
                "result": {
                    "object_name": object_name,
                    "formats": export_formats,
                },
            }

    return asyncio.run(_run())


@celery_app.task(
    name="app.tasks.feature_model_analysis.compare_feature_model_versions", bind=True
)
def compare_feature_model_versions(
    self,
    *,
    model_id: str,
    base_version_id: str,
    target_version_id: str,
    analysis_types: list[str] | None = None,
    max_solutions: int = 100,
) -> dict[str, Any]:
    """Comparación detallada entre versiones del modelo."""

    self.update_state(
        state="PROGRESS",
        meta={"step": "load_versions", "percent": 10, "eta_seconds_estimate": None},
    )

    async def _run() -> dict[str, Any]:
        async def _set_progress(meta: dict[str, Any]) -> None:
            await cache_service.set_task_progress(self.request.id, meta)

        await cache_service.set_task_status(self.request.id, status="running")
        await _set_progress({"step": "load_versions", "percent": 10})
        async with SessionLocal() as session:
            repo = FeatureModelVersionRepository(session)
            base_version = await repo.get_complete_with_relations(
                version_id=base_version_id,
                include_resources=False,
            )
            target_version = await repo.get_complete_with_relations(
                version_id=target_version_id,
                include_resources=False,
            )
            if not base_version or not target_version:
                return {"status": "error", "error": "Feature model version not found"}
            if str(base_version.feature_model_id) != model_id:
                return {
                    "status": "error",
                    "error": "Base version does not belong to model",
                }
            if str(target_version.feature_model_id) != model_id:
                return {
                    "status": "error",
                    "error": "Target version does not belong to model",
                }

            parsed_types = None
            if analysis_types:
                parsed_types = [AnalysisType(t) for t in analysis_types]

            self.update_state(
                state="PROGRESS",
                meta={"step": "compare", "percent": 80, "eta_seconds_estimate": None},
            )
            await _set_progress({"step": "compare", "percent": 80})
            result = compare_versions(
                base_version=base_version,
                target_version=target_version,
                analysis_types=parsed_types,
                max_solutions=max_solutions,
            )
            self.update_state(
                state="PROGRESS",
                meta={"step": "done", "percent": 100, "eta_seconds_estimate": 0},
            )
            await _set_progress({"step": "done", "percent": 100})
            await cache_service.set_task_status(self.request.id, status="done")
            return {
                "status": "ok",
                "result": {
                    "base": result["base"].__dict__,
                    "target": result["target"].__dict__,
                    "delta": result["delta"],
                },
            }

    return asyncio.run(_run())


@celery_app.task(
    name="app.tasks.feature_model_analysis.recompute_version_statistics", bind=True
)
def recompute_version_statistics(self, *, version_id: str) -> dict[str, Any]:
    """Recalcula estadísticas de una versión del modelo."""

    self.update_state(
        state="PROGRESS",
        meta={"step": "load_statistics", "percent": 40, "eta_seconds_estimate": None},
    )

    async def _run() -> dict[str, Any]:
        async def _set_progress(meta: dict[str, Any]) -> None:
            await cache_service.set_task_progress(self.request.id, meta)

        await cache_service.set_task_status(self.request.id, status="running")
        await _set_progress({"step": "load_statistics", "percent": 40})
        async with SessionLocal() as session:
            repo = FeatureModelVersionRepository(session)
            stats = await repo.get_statistics(version_id=version_id)
            if stats is None:
                return {"status": "error", "error": "Feature model version not found"}
            self.update_state(
                state="PROGRESS",
                meta={"step": "done", "percent": 100, "eta_seconds_estimate": 0},
            )
            await _set_progress({"step": "done", "percent": 100})
            await cache_service.set_task_status(self.request.id, status="done")
            return {"status": "ok", "result": stats}

    return asyncio.run(_run())


@celery_app.task(
    name="app.tasks.feature_model_analysis.validate_configuration", bind=True
)
def validate_configuration(
    self,
    *,
    model_id: str,
    version_id: str,
    selected_features: list[str],
) -> dict[str, Any]:
    """Valida una configuración específica usando el validador lógico."""

    self.update_state(
        state="PROGRESS",
        meta={"step": "load_version", "percent": 10, "eta_seconds_estimate": None},
    )

    async def _run() -> dict[str, Any]:
        async def _set_progress(meta: dict[str, Any]) -> None:
            await cache_service.set_task_progress(self.request.id, meta)

        await cache_service.set_task_status(self.request.id, status="running")
        await _set_progress({"step": "load_version", "percent": 10})
        async with SessionLocal() as session:
            repo = FeatureModelVersionRepository(session)
            version = await repo.get_complete_with_relations(
                version_id=version_id,
                include_resources=False,
            )
            if not version:
                return {"status": "error", "error": "Feature model version not found"}
            if str(version.feature_model_id) != model_id:
                return {"status": "error", "error": "Version does not belong to model"}

            features_payload, relations_payload, constraints_payload = _build_payload(
                version
            )
            validator = FeatureModelLogicalValidator()
            self.update_state(
                state="PROGRESS",
                meta={"step": "validate", "percent": 80, "eta_seconds_estimate": None},
            )
            await _set_progress({"step": "validate", "percent": 80})
            result = validator.validate_configuration(
                features=features_payload,
                relations=relations_payload,
                constraints=constraints_payload,
                selected_features=selected_features,
            )
            self.update_state(
                state="PROGRESS",
                meta={"step": "done", "percent": 100, "eta_seconds_estimate": 0},
            )
            await _set_progress({"step": "done", "percent": 100})
            await cache_service.set_task_status(self.request.id, status="done")
            return {"status": "ok", "result": result.__dict__}

    return asyncio.run(_run())
