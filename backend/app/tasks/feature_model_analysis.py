"""Tareas Celery para análisis de Feature Models."""

from __future__ import annotations

import asyncio
from typing import Any

from app.core.celery import celery_app
from app.api.deps import SessionLocal
from app.repositories import FeatureModelVersionRepository
from app.enums import AnalysisType
from app.services.feature_model.fm_analysis_facade import analyze_version


@celery_app.task(name="app.tasks.feature_model_analysis.run_feature_model_analysis")
def run_feature_model_analysis(
    *,
    model_id: str,
    version_id: str,
    analysis_types: list[str] | None = None,
    max_solutions: int = 100,
) -> dict[str, Any]:
    """Ejecuta análisis de un modelo en segundo plano y devuelve el resumen."""

    async def _run() -> dict[str, Any]:
        async with SessionLocal() as session:
            repo = FeatureModelVersionRepository(session)
            version = await repo.get_complete_with_relations(
                version_id=version_id,
                include_resources=False,
            )
            if not version:
                return {
                    "status": "error",
                    "error": "Feature model version not found",
                }
            if str(version.feature_model_id) != model_id:
                return {
                    "status": "error",
                    "error": "Version does not belong to model",
                }

            parsed_types = None
            if analysis_types:
                parsed_types = [AnalysisType(t) for t in analysis_types]

            summary = analyze_version(
                version=version,
                analysis_types=parsed_types,
                max_solutions=max_solutions,
                include_uvl_validation=True,
            )
            return {
                "status": "ok",
                "result": summary.__dict__,
            }

    return asyncio.run(_run())
