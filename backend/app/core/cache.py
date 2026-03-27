"""
app/core/cache.py

Caché en dos niveles sobre Redis para el dominio Feature Model:

    Nivel 1 — fastapi-cache2  (@cache en rutas HTTP):
        Cachea respuestas completas de endpoints de lectura frecuente.
        Ideal para: listado de dominios/modelos, árbol completo y metadatos.

    Nivel 2 — CacheService (Redis directo):
        Caché de bajo nivel para pipelines internos:
            - Estado de jobs de importación y validación (polling)
            - Locks distribuidos para evitar ejecuciones duplicadas
            - Invalidación granular por usuario / modelo / versión

"""

from __future__ import annotations

import hashlib
import json
from typing import Any
from uuid import UUID

from fastapi import Request, Response
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import ConnectionPool, Redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# TTLs y constructores de claves centralizados
# ─────────────────────────────────────────────────────────────────────────────


class CacheKeys:
    """
    Centraliza TTLs y prefijos de caché del dominio Feature Model.
    Modifica aquí y afecta a toda la app.
    """

    # ── TTLs (segundos) ───────────────────────────────────────────────────────
    TTL_TEMPLATES = 3600  # Catálogos/plantillas globales
    TTL_FEATURE_MODELS_LIST = 120  # Listado de feature models
    TTL_FEATURE_MODEL_DETAIL = 60  # Detalle de feature model
    TTL_FEATURE_MODEL_TREE = 300  # Árbol completo serializado
    TTL_VALIDATION_STATUS = 10  # Polling de validación
    TTL_IMPORT_STATUS = 10  # Polling de importación
    TTL_VALIDATION_LOCK = 300  # Lock de validación
    TTL_IMPORT_LOCK = 300  # Lock de importación
    TTL_HEALTH = 15  # Health check

    # ── Prefijos ──────────────────────────────────────────────────────────────
    _PFX_FM = "fm:"
    _PFX_DOMAIN = "domain:"
    _PFX_TEMPLATE = "template:"
    _PFX_IMPORT_STATUS = "import_status:"
    _PFX_VALIDATION = "validation_status:"
    _PFX_LOCK = "lock:"

    # ── Claves compuestas ─────────────────────────────────────────────────────

    @staticmethod
    def feature_model_validation_status(version_id: str | UUID) -> str:
        """Estado del job de validación para una versión de Feature Model."""
        return f"{CacheKeys._PFX_VALIDATION}{version_id}"

    @staticmethod
    def feature_model_import_status(job_id: str | UUID) -> str:
        """Estado de un job de importación de Feature Model."""
        return f"{CacheKeys._PFX_IMPORT_STATUS}{job_id}"

    @staticmethod
    def import_lock(feature_model_id: str | UUID) -> str:
        """Lock distribuido para evitar importaciones concurrentes del mismo modelo."""
        return f"{CacheKeys._PFX_LOCK}import:{feature_model_id}"

    @staticmethod
    def validation_lock(version_id: str | UUID) -> str:
        """Lock distribuido para evitar validaciones duplicadas de una versión."""
        return f"{CacheKeys._PFX_LOCK}validation:{version_id}"

    @staticmethod
    def user_feature_models(user_id: str | UUID) -> str:
        """Clave de caché para el listado de feature models de un usuario."""
        return f"{CacheKeys._PFX_FM}list:{user_id}"

    @staticmethod
    def feature_model_detail(model_id: str | UUID) -> str:
        """Clave de caché para el detalle de un feature model."""
        return f"{CacheKeys._PFX_FM}detail:{model_id}"

    @staticmethod
    def feature_model_tree(version_id: str | UUID) -> str:
        """Clave de caché para el árbol completo de una versión."""
        return f"{CacheKeys._PFX_FM}tree:{version_id}"


# ─────────────────────────────────────────────────────────────────────────────
# Connection pools
# ─────────────────────────────────────────────────────────────────────────────


def _build_pool(db: int) -> ConnectionPool:
    """Pool Redis con reintentos exponenciales y health check."""
    base_url = (
        f"redis://"
        f"{(':' + settings.REDIS_PASSWORD.get_secret_value() + '@') if settings.REDIS_PASSWORD else ''}"
        f"{settings.REDIS_HOST}:{settings.REDIS_PORT}/{db}"
    )
    return ConnectionPool.from_url(
        base_url,
        max_connections=20,
        decode_responses=True,
        retry=Retry(ExponentialBackoff(cap=10, base=0.5), retries=3),
        retry_on_error=[ConnectionError, TimeoutError],
        socket_connect_timeout=5,
        socket_timeout=5,
        health_check_interval=30,
    )


# Pools independientes para fastapi-cache2 y CacheService
# (misma DB Redis, distinto pool para no bloquear entre sí)
_http_cache_pool = _build_pool(settings.REDIS_DB_CACHE)
_service_pool = _build_pool(settings.REDIS_DB_CACHE)


async def _close_pool(pool: ConnectionPool) -> None:
    """Cierra un pool Redis compatible con distintas versiones de redis-py."""
    closer = getattr(pool, "aclose", None)
    if callable(closer):
        await closer()
        return

    disconnect = getattr(pool, "disconnect", None)
    if callable(disconnect):
        result = disconnect(inuse_connections=True)
        if hasattr(result, "__await__"):
            await result


def get_redis_client() -> Redis:
    """Cliente Redis listo para usar en servicios y tareas Celery."""
    return Redis(connection_pool=_service_pool)


# ─────────────────────────────────────────────────────────────────────────────
# Lifecycle de fastapi-cache2
# ─────────────────────────────────────────────────────────────────────────────


async def setup_cache() -> None:
    """
    Inicializa fastapi-cache2 con backend Redis.
    Llamar en el lifespan startup de FastAPI.
    """
    redis = Redis(connection_pool=_http_cache_pool)
    try:
        await redis.ping()
        log.info(
            "cache.connected", host=settings.REDIS_HOST, db=settings.REDIS_DB_CACHE
        )
    except Exception as exc:
        log.error("cache.connection_failed", error=str(exc))
        raise

    FastAPICache.init(
        backend=RedisBackend(redis),
        prefix="fm:http:",
    )
    log.info("cache.initialized", backend="redis")


async def teardown_cache() -> None:
    """Libera pools Redis. Llamar en el lifespan shutdown de FastAPI."""
    await FastAPICache.clear()
    await _close_pool(_http_cache_pool)
    await _close_pool(_service_pool)
    log.info("cache.shutdown")


# ─────────────────────────────────────────────────────────────────────────────
# Key builders para @cache
# ─────────────────────────────────────────────────────────────────────────────


def user_key_builder(
    func: Any,
    namespace: str = "",
    request: Request | None = None,
    response: Response | None = None,
    args: tuple = (),
    kwargs: dict = {},
) -> str:
    """
    Clave de caché que incluye el user_id del header X-User-Id.
    Garantiza que cada usuario tenga su propia entrada de caché.
    Usar en endpoints del dominio Feature Model.
    """
    prefix = FastAPICache.get_prefix()
    user_id = request.headers.get("X-User-Id", "anon") if request else "anon"
    path = request.url.path if request else ""
    query = str(sorted(request.query_params.items())) if request else ""
    raw = f"{namespace}:{user_id}:{path}:{query}"
    return f"{prefix}:{hashlib.md5(raw.encode()).hexdigest()}"


def feature_model_detail_key_builder(
    func: Any,
    namespace: str = "",
    request: Request | None = None,
    response: Response | None = None,
    args: tuple = (),
    kwargs: dict = {},
) -> str:
    """Key builder para detalle de un feature model/version concreto."""
    prefix = FastAPICache.get_prefix()
    user_id = request.headers.get("X-User-Id", "anon") if request else "anon"
    model_id = kwargs.get("model_id", "")
    version_id = kwargs.get("version_id", "")
    return f"{prefix}:fm:{user_id}:{model_id}:{version_id}"


def template_key_builder(
    func: Any,
    namespace: str = "",
    request: Request | None = None,
    response: Response | None = None,
    args: tuple = (),
    kwargs: dict = {},
) -> str:
    """
    Las plantillas son globales (no por usuario).
    Clave simple basada en el path, sin user_id.
    """
    prefix = FastAPICache.get_prefix()
    path = request.url.path if request else ""
    return f"{prefix}:templates:{hashlib.md5(path.encode()).hexdigest()}"


# ─────────────────────────────────────────────────────────────────────────────
# CacheService — caché de bajo nivel
# ─────────────────────────────────────────────────────────────────────────────


class CacheService:
    """
    Caché Redis de bajo nivel para operaciones internas del dominio Feature Model.
    Complementa a fastapi-cache2 para datos no-HTTP.
    """

    def __init__(self) -> None:
        self._redis = get_redis_client()

    # ── Estado de jobs (importación / validación) ───────────────────────────

    async def set_validation_status(
        self,
        version_id: str | UUID,
        status: str,
        error: str | None = None,
    ) -> None:
        """Persiste estado de validación de una versión de Feature Model."""
        key = CacheKeys.feature_model_validation_status(version_id)
        payload = {"status": status, "version_id": str(version_id)}
        if error:
            payload["error"] = error
        await self._redis.setex(
            key, CacheKeys.TTL_VALIDATION_STATUS, json.dumps(payload)
        )
        log.debug(
            "cache.validation_status.set", version_id=str(version_id), status=status
        )

    async def get_validation_status(self, version_id: str | UUID) -> dict | None:
        """Retorna estado cacheado de validación o None si expiró."""
        key = CacheKeys.feature_model_validation_status(version_id)
        value = await self._redis.get(key)
        return json.loads(value) if value else None

    async def set_import_status(
        self,
        job_id: str | UUID,
        status: str,
        error: str | None = None,
    ) -> None:
        """Persiste estado de un job de importación de Feature Model."""
        key = CacheKeys.feature_model_import_status(job_id)
        payload = {"status": status, "job_id": str(job_id)}
        if error:
            payload["error"] = error
        await self._redis.setex(key, CacheKeys.TTL_IMPORT_STATUS, json.dumps(payload))
        log.debug("cache.import_status.set", job_id=str(job_id), status=status)

    async def get_import_status(self, job_id: str | UUID) -> dict | None:
        """Retorna estado cacheado de importación o None si expiró."""
        key = CacheKeys.feature_model_import_status(job_id)
        value = await self._redis.get(key)
        return json.loads(value) if value else None

    # ── Locks distribuidos ────────────────────────────────────────────────────

    async def acquire_import_lock(self, feature_model_id: str | UUID) -> bool:
        """Adquiere lock exclusivo para importar un Feature Model."""
        key = CacheKeys.import_lock(feature_model_id)
        acquired = await self._redis.set(
            key, "1", nx=True, ex=CacheKeys.TTL_IMPORT_LOCK
        )
        if acquired:
            log.debug(
                "cache.import_lock.acquired", feature_model_id=str(feature_model_id)
            )
        else:
            log.warning(
                "cache.import_lock.already_held", feature_model_id=str(feature_model_id)
            )
        return bool(acquired)

    async def release_import_lock(self, feature_model_id: str | UUID) -> None:
        """Libera lock de importación."""
        key = CacheKeys.import_lock(feature_model_id)
        await self._redis.delete(key)
        log.debug("cache.import_lock.released", feature_model_id=str(feature_model_id))

    async def acquire_validation_lock(self, version_id: str | UUID) -> bool:
        """Adquiere lock exclusivo para validar una versión."""
        key = CacheKeys.validation_lock(version_id)
        acquired = await self._redis.set(
            key, "1", nx=True, ex=CacheKeys.TTL_VALIDATION_LOCK
        )
        if acquired:
            log.debug("cache.validation_lock.acquired", version_id=str(version_id))
        else:
            log.warning(
                "cache.validation_lock.already_held", version_id=str(version_id)
            )
        return bool(acquired)

    async def release_validation_lock(self, version_id: str | UUID) -> None:
        """Libera lock de validación."""
        key = CacheKeys.validation_lock(version_id)
        await self._redis.delete(key)
        log.debug("cache.validation_lock.released", version_id=str(version_id))

    # ── Invalidación granular ─────────────────────────────────────────────────

    async def invalidate_user_feature_models(self, user_id: str | UUID) -> None:
        """Invalida caché de listados de feature models asociados al usuario."""
        await self._invalidate_pattern(f"fm:http:*feature-model*{user_id}*")
        log.debug("cache.invalidated.feature_models", user_id=str(user_id))

    async def invalidate_feature_model(
        self,
        model_id: str | UUID,
        version_id: str | UUID | None = None,
    ) -> None:
        """Invalida detalle/listado/árbol de un feature model concreto."""
        await self._invalidate_pattern(f"fm:http:*{model_id}*")
        if version_id:
            await self._invalidate_pattern(f"fm:http:*{version_id}*")
        log.debug(
            "cache.invalidated.feature_model",
            model_id=str(model_id),
            version_id=str(version_id) if version_id else None,
        )

    async def invalidate_domains(self) -> None:
        """Invalida caché de endpoints globales de dominios/catálogos."""
        await self._invalidate_pattern("fm:http:*domain*")
        log.debug("cache.invalidated.domains")

    async def invalidate_templates(self) -> None:
        """Invalida caché de plantillas/catálogos globales."""
        await self._invalidate_pattern("fm:http:*templates*")
        log.debug("cache.invalidated.templates")

    async def _invalidate_pattern(self, pattern: str) -> None:
        """Borra todas las claves que coincidan con el patrón glob."""
        keys = await self._redis.keys(pattern)
        if keys:
            await self._redis.delete(*keys)

    # ── Health ────────────────────────────────────────────────────────────────

    async def ping(self) -> bool:
        try:
            return bool(await self._redis.ping())
        except Exception:
            return False


# ── Singleton ─────────────────────────────────────────────────────────────────
cache_service = CacheService()
