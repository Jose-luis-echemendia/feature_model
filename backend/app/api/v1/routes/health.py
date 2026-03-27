"""
app/api/routes/health.py

GET /api/v1/utils/health-check/  → liveness probe (Docker / K8s)
GET /api/v1/utils/status/        → estado detallado de todos los servicios
"""

from __future__ import annotations

import time
import shutil
import psutil
from datetime import datetime

from fastapi import APIRouter
from fastapi_cache.decorator import cache
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)
router = APIRouter(tags=["Health"])


# ─────────────────────────────────────────────────────────────────────────────
# Schemas de respuesta
# ─────────────────────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime


class ServiceStatus(BaseModel):
    name: str
    status: str  # "ok" | "degraded" | "down"
    latency_ms: float | None = None
    detail: str | None = None


class ResourceMetrics(BaseModel):
    total_gb: float
    used_gb: float
    free_or_available_gb: float
    usage_percent: float
    status: str  # "ok" | "warning" | "critical"


class NetworkMetrics(BaseModel):
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int


class SystemStatusResponse(BaseModel):
    status: str  # "ok" | "degraded" | "down"
    version: str
    environment: str
    timestamp: datetime
    services: list[ServiceStatus]
    disk_usage: ResourceMetrics
    memory_usage: ResourceMetrics
    network: NetworkMetrics


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────


@router.get(
    "/health-check",
    response_model=HealthResponse,
    summary="Liveness probe",
    description="Retorna 200 si el proceso está vivo. Usado por Docker y K8s.",
)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", timestamp=datetime.utcnow())


@router.get(
    "/status",
    response_model=SystemStatusResponse,
    summary="Estado detallado del sistema",
    description=(
        "Verifica la conectividad con PostgreSQL, Redis y Celery. "
        "Respuesta cacheada 15 segundos para no saturar los servicios."
    ),
)
@cache(expire=15)
async def system_status() -> SystemStatusResponse:
    services: list[ServiceStatus] = []
    overall = "ok"

    # ── PostgreSQL ─────────────────────────────────────────────
    try:
        from app.core.db import AsyncSessionLocal
        from sqlmodel import text

        t0 = time.monotonic()
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        services.append(
            ServiceStatus(
                name="postgresql",
                status="ok",
                latency_ms=round((time.monotonic() - t0) * 1000, 1),
            )
        )
    except Exception as exc:
        services.append(
            ServiceStatus(name="postgresql", status="down", detail=str(exc)[:150])
        )
        overall = "down"

    # ── Redis ──────────────────────────────────────────────────
    try:
        from app.core.cache import cache_service

        t0 = time.monotonic()
        ok = await cache_service.ping()
        latency = round((time.monotonic() - t0) * 1000, 1)
        services.append(
            ServiceStatus(
                name="redis",
                status="ok" if ok else "down",
                latency_ms=latency,
            )
        )
        if not ok and overall != "down":
            overall = "degraded"
    except Exception as exc:
        services.append(
            ServiceStatus(name="redis", status="down", detail=str(exc)[:150])
        )
        if overall != "down":
            overall = "degraded"

    # ── Celery workers ─────────────────────────────────────────
    try:
        from app.core.celery import celery_app

        t0 = time.monotonic()
        active = celery_app.control.inspect(timeout=2.0).active()
        latency = round((time.monotonic() - t0) * 1000, 1)
        workers = len(active) if active else 0
        services.append(
            ServiceStatus(
                name="celery",
                status="ok" if workers > 0 else "degraded",
                latency_ms=latency,
                detail=f"{workers} worker(s) activos",
            )
        )
        if workers == 0 and overall == "ok":
            overall = "degraded"
    except Exception as exc:
        services.append(
            ServiceStatus(name="celery", status="degraded", detail=str(exc)[:150])
        )
        if overall == "ok":
            overall = "degraded"

    # ── MinIO / S3  ────────────────────────────────────────────
    try:
        import boto3

        t0 = time.monotonic()
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            use_ssl=settings.MINIO_USE_SSL,
            region_name="us-east-1",  # MinIO usually ignores this, but boto3 may complain if empty
        )
        # Verificamos si el bucket existe y tenemos acceso
        s3.head_bucket(Bucket=settings.MINIO_BUCKET_FM)
        latency = round((time.monotonic() - t0) * 1000, 1)
        services.append(
            ServiceStatus(
                name="minio",
                status="ok",
                latency_ms=latency,
            )
        )
    except Exception as exc:
        services.append(
            ServiceStatus(name="minio", status="down", detail=str(exc)[:150])
        )
        if overall != "down":
            overall = "degraded"

    # ── Métricas de Recursos ───────────────────────────────────
    # Umbrales: >85% warning, >95% critical
    DISK_WARNING_THRESHOLD = 85.0
    DISK_CRITICAL_THRESHOLD = 95.0
    MEM_WARNING_THRESHOLD = 85.0
    MEM_CRITICAL_THRESHOLD = 95.0

    disk = shutil.disk_usage("/")
    disk_percent = round((disk.used / disk.total) * 100, 1)
    disk_status = "ok"
    if disk_percent >= DISK_CRITICAL_THRESHOLD:
        disk_status = "critical"
        overall = "degraded" if overall == "ok" else overall
    elif disk_percent >= DISK_WARNING_THRESHOLD:
        disk_status = "warning"

    disk_metrics = ResourceMetrics(
        total_gb=round(disk.total / (1024**3), 2),
        used_gb=round(disk.used / (1024**3), 2),
        free_or_available_gb=round(disk.free / (1024**3), 2),
        usage_percent=disk_percent,
        status=disk_status,
    )

    mem = psutil.virtual_memory()
    mem_percent = mem.percent
    mem_status = "ok"
    if mem_percent >= MEM_CRITICAL_THRESHOLD:
        mem_status = "critical"
        overall = "degraded" if overall == "ok" else overall
    elif mem_percent >= MEM_WARNING_THRESHOLD:
        mem_status = "warning"

    mem_metrics = ResourceMetrics(
        total_gb=round(mem.total / (1024**3), 2),
        used_gb=round(mem.used / (1024**3), 2),
        free_or_available_gb=round(mem.available / (1024**3), 2),
        usage_percent=mem_percent,
        status=mem_status,
    )

    net = psutil.net_io_counters()
    net_metrics = NetworkMetrics(
        bytes_sent=net.bytes_sent,
        bytes_recv=net.bytes_recv,
        packets_sent=net.packets_sent,
        packets_recv=net.packets_recv,
    )

    return SystemStatusResponse(
        status=overall,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.utcnow(),
        services=services,
        disk_usage=disk_metrics,
        memory_usage=mem_metrics,
        network=net_metrics,
    )
