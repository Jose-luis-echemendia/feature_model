"""Tareas periódicas y de mantenimiento para Feature Models."""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any

from sqlmodel import select
from sqlalchemy.orm import selectinload

from app.core.celery import celery_app
from app.api.deps import SessionLocal
from app.core.redis import redis_client
from app.core.cache import cache_service
from app.core.logging import get_logger
from app.models import FeatureModel, FeatureModelVersion
from app.repositories import FeatureModelVersionRepository
from app.services.feature_model.fm_analysis_facade import analyze_version

log = get_logger(__name__)


def _progress_meta(
    *,
    step: str,
    current: int,
    total: int,
    start_time: float,
) -> dict[str, Any]:
    percent = int((current / total) * 100) if total else 0
    elapsed = max(time.perf_counter() - start_time, 0.0)
    eta_seconds = int((elapsed / current) * (total - current)) if current else None
    return {
        "step": step,
        "current": current,
        "total": total,
        "percent": percent,
        "eta_seconds_estimate": eta_seconds,
    }


async def _get_latest_versions(session, limit: int = 50) -> list[FeatureModelVersion]:
    stmt = (
        select(FeatureModel)
        .options(selectinload(FeatureModel.versions))
        .where(FeatureModel.is_active == True)  # noqa: E712
        .limit(limit)
    )
    result = await session.execute(stmt)
    models = result.scalars().all()

    versions: list[FeatureModelVersion] = []
    for model in models:
        if not model.versions:
            continue
        latest = max(model.versions, key=lambda v: v.version_number)
        versions.append(latest)
    return versions


@celery_app.task(name="app.tasks.maintenance.refresh_active_models_metrics", bind=True)
def refresh_active_models_metrics(self, limit: int = 50) -> dict[str, Any]:
    """Recalcula métricas de modelos activos y las cachea en Redis."""

    async def _run() -> dict[str, Any]:
        await cache_service.set_task_status(self.request.id, status="running")
        async with SessionLocal() as session:
            versions = await _get_latest_versions(session, limit=limit)
            cached = 0
            total = len(versions)
            start_time = time.perf_counter()
            for idx, version in enumerate(versions, start=1):
                progress = _progress_meta(
                    step="analyze",
                    current=idx,
                    total=total,
                    start_time=start_time,
                )
                self.update_state(state="PROGRESS", meta=progress)
                await cache_service.set_task_progress(self.request.id, progress)
                summary = analyze_version(
                    version=version,
                    analysis_types=None,
                    max_solutions=50,
                    include_uvl_validation=False,
                )
                key = f"fm:metrics:{version.id}"
                await redis_client.set(key, json.dumps(summary.__dict__), ex=86400)
                cached += 1
            self.update_state(
                state="PROGRESS",
                meta={"step": "done", "percent": 100, "eta_seconds_estimate": 0},
            )
            await cache_service.set_task_progress(
                self.request.id,
                {"step": "done", "percent": 100, "eta_seconds_estimate": 0},
            )
            await cache_service.set_task_status(self.request.id, status="done")
            return {"status": "ok", "cached": cached}

    return asyncio.run(_run())


@celery_app.task(name="app.tasks.maintenance.cleanup_stale_task_results", bind=True)
def cleanup_stale_task_results(
    self, prefix: str = "celery-task-meta-"
) -> dict[str, Any]:
    """Elimina resultados sin expiración (TTL=-1) para evitar acumulación en Redis."""

    async def _run() -> dict[str, Any]:
        await cache_service.set_task_status(self.request.id, status="running")
        deleted = 0
        cursor = 0
        while True:
            cursor, keys = await redis_client.scan(cursor=cursor, match=f"{prefix}*")
            for key in keys:
                ttl = await redis_client.ttl(key)
                if ttl == -1:
                    await redis_client.delete(key)
                    deleted += 1
            if cursor == 0:
                break
        self.update_state(
            state="PROGRESS",
            meta={
                "step": "done",
                "deleted": deleted,
                "percent": 100,
                "eta_seconds_estimate": 0,
            },
        )
        await cache_service.set_task_progress(
            self.request.id,
            {"step": "done", "deleted": deleted, "percent": 100},
        )
        await cache_service.set_task_status(self.request.id, status="done")
        return {"status": "ok", "deleted": deleted}

    return asyncio.run(_run())


@celery_app.task(name="app.tasks.maintenance.verify_models_integrity", bind=True)
def verify_models_integrity(self, limit: int = 50) -> dict[str, Any]:
    """Verifica integridad de modelos activos y reporta inconsistencias."""

    async def _run() -> dict[str, Any]:
        await cache_service.set_task_status(self.request.id, status="running")
        async with SessionLocal() as session:
            versions = await _get_latest_versions(session, limit=limit)
            issues = []
            total = len(versions)
            start_time = time.perf_counter()
            for idx, version in enumerate(versions, start=1):
                progress = _progress_meta(
                    step="verify",
                    current=idx,
                    total=total,
                    start_time=start_time,
                )
                self.update_state(state="PROGRESS", meta=progress)
                await cache_service.set_task_progress(self.request.id, progress)
                try:
                    summary = analyze_version(
                        version=version,
                        analysis_types=None,
                        max_solutions=20,
                        include_uvl_validation=True,
                    )
                    if not summary.satisfiable:
                        issues.append(
                            {
                                "version_id": str(version.id),
                                "model_id": str(version.feature_model_id),
                                "errors": summary.errors,
                            }
                        )
                except Exception as exc:
                    issues.append(
                        {
                            "version_id": str(version.id),
                            "model_id": str(version.feature_model_id),
                            "errors": [str(exc)],
                        }
                    )
            self.update_state(
                state="PROGRESS",
                meta={"step": "done", "percent": 100, "eta_seconds_estimate": 0},
            )
            await cache_service.set_task_progress(
                self.request.id,
                {"step": "done", "percent": 100, "eta_seconds_estimate": 0},
            )
            await cache_service.set_task_status(self.request.id, status="done")
            return {"status": "ok", "issues": issues}

    return asyncio.run(_run())


@celery_app.task(
    name="app.tasks.maintenance.precache_popular_models_analysis", bind=True
)
def precache_popular_models_analysis(self, limit: int = 20) -> dict[str, Any]:
    """Precalcula análisis para modelos activos (placeholder para ranking futuro)."""

    async def _run() -> dict[str, Any]:
        await cache_service.set_task_status(self.request.id, status="running")
        async with SessionLocal() as session:
            versions = await _get_latest_versions(session, limit=limit)
            total = len(versions)
            start_time = time.perf_counter()
            for idx, version in enumerate(versions, start=1):
                progress = _progress_meta(
                    step="precache",
                    current=idx,
                    total=total,
                    start_time=start_time,
                )
                self.update_state(state="PROGRESS", meta=progress)
                await cache_service.set_task_progress(self.request.id, progress)
                summary = analyze_version(
                    version=version,
                    analysis_types=None,
                    max_solutions=30,
                    include_uvl_validation=False,
                )
                key = f"fm:precache:{version.id}"
                await redis_client.set(key, json.dumps(summary.__dict__), ex=43200)
            self.update_state(
                state="PROGRESS",
                meta={"step": "done", "percent": 100, "eta_seconds_estimate": 0},
            )
            await cache_service.set_task_progress(
                self.request.id,
                {"step": "done", "percent": 100, "eta_seconds_estimate": 0},
            )
            await cache_service.set_task_status(self.request.id, status="done")
            return {"status": "ok", "precached": len(versions)}

    return asyncio.run(_run())


@celery_app.task(
    name="app.tasks.maintenance.collect_analysis_runtime_metrics", bind=True
)
def collect_analysis_runtime_metrics(self, limit: int = 20) -> dict[str, Any]:
    """Recolecta tiempos de análisis y tamaño del modelo para alertas."""

    async def _run() -> dict[str, Any]:
        await cache_service.set_task_status(self.request.id, status="running")
        async with SessionLocal() as session:
            versions = await _get_latest_versions(session, limit=limit)
            metrics = []
            total = len(versions)
            start_time = time.perf_counter()
            for idx, version in enumerate(versions, start=1):
                progress = _progress_meta(
                    step="measure",
                    current=idx,
                    total=total,
                    start_time=start_time,
                )
                self.update_state(state="PROGRESS", meta=progress)
                await cache_service.set_task_progress(self.request.id, progress)
                start = time.perf_counter()
                summary = analyze_version(
                    version=version,
                    analysis_types=None,
                    max_solutions=10,
                    include_uvl_validation=False,
                )
                elapsed_ms = int((time.perf_counter() - start) * 1000)
                metrics.append(
                    {
                        "version_id": str(version.id),
                        "model_id": str(version.feature_model_id),
                        "elapsed_ms": elapsed_ms,
                        "estimated_configurations": summary.estimated_configurations,
                        "dead_features": len(summary.dead_features),
                    }
                )
            key = "fm:runtime_metrics:last"
            await redis_client.set(key, json.dumps(metrics), ex=3600)
            self.update_state(
                state="PROGRESS",
                meta={"step": "done", "percent": 100, "eta_seconds_estimate": 0},
            )
            await cache_service.set_task_progress(
                self.request.id,
                {"step": "done", "percent": 100, "eta_seconds_estimate": 0},
            )
            await cache_service.set_task_status(self.request.id, status="done")
            return {"status": "ok", "count": len(metrics)}

    return asyncio.run(_run())


@celery_app.task(name="app.tasks.maintenance.recompute_version_statistics", bind=True)
def recompute_version_statistics(self, limit: int = 50) -> dict[str, Any]:
    """Recalcula estadísticas básicas de las últimas versiones activas."""

    async def _run() -> dict[str, Any]:
        await cache_service.set_task_status(self.request.id, status="running")
        async with SessionLocal() as session:
            versions = await _get_latest_versions(session, limit=limit)
            repo = FeatureModelVersionRepository(session)
            stats_map: list[dict[str, Any]] = []
            total = len(versions)
            start_time = time.perf_counter()
            for idx, version in enumerate(versions, start=1):
                progress = _progress_meta(
                    step="recompute",
                    current=idx,
                    total=total,
                    start_time=start_time,
                )
                self.update_state(state="PROGRESS", meta=progress)
                await cache_service.set_task_progress(self.request.id, progress)
                stats = await repo.get_statistics(version_id=version.id)
                if stats is None:
                    continue
                stats_map.append({"version_id": str(version.id), "stats": stats})
            self.update_state(
                state="PROGRESS",
                meta={"step": "done", "percent": 100, "eta_seconds_estimate": 0},
            )
            await cache_service.set_task_progress(
                self.request.id,
                {"step": "done", "percent": 100, "eta_seconds_estimate": 0},
            )
            await cache_service.set_task_status(self.request.id, status="done")
            return {"status": "ok", "stats": stats_map}

    return asyncio.run(_run())


@celery_app.task(
    name="app.tasks.maintenance.audit_feature_model_data_quality", bind=True
)
def audit_feature_model_data_quality(self, limit: int = 50) -> dict[str, Any]:
    """Auditoría básica de calidad de datos (placeholder)."""

    async def _run() -> dict[str, Any]:
        await cache_service.set_task_status(self.request.id, status="running")
        async with SessionLocal() as session:
            versions = await _get_latest_versions(session, limit=limit)
            findings = []
            total = len(versions)
            start_time = time.perf_counter()
            for idx, version in enumerate(versions, start=1):
                progress = _progress_meta(
                    step="audit",
                    current=idx,
                    total=total,
                    start_time=start_time,
                )
                self.update_state(state="PROGRESS", meta=progress)
                await cache_service.set_task_progress(self.request.id, progress)
                if not version.features:
                    findings.append(
                        {
                            "version_id": str(version.id),
                            "issue": "Model has no features",
                        }
                    )
            self.update_state(
                state="PROGRESS",
                meta={"step": "done", "percent": 100, "eta_seconds_estimate": 0},
            )
            await cache_service.set_task_progress(
                self.request.id,
                {"step": "done", "percent": 100, "eta_seconds_estimate": 0},
            )
            await cache_service.set_task_status(self.request.id, status="done")
            return {"status": "ok", "findings": findings}

    return asyncio.run(_run())
