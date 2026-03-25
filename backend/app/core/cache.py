"""
app/core/cache.py

Caché en dos niveles sobre Redis:

  Nivel 1 — fastapi-cache2  (@cache en rutas HTTP):
    Cachea respuestas completas de endpoints de lectura frecuente.
    Ideal para: listado de plantillas, skills del usuario, proyectos…

  Nivel 2 — CacheService (Redis directo):
    Caché de bajo nivel para el pipeline interno:
      - Estado del job de generación PDF (polling)
      - Locks distribuidos para evitar generaciones duplicadas
      - Invalidación granular por usuario / CV

Uso del decorador @cache en rutas:
    from fastapi_cache.decorator import cache
    from app.core.cache import CacheKeys, user_key_builder

    @router.get("/templates")
    @cache(expire=CacheKeys.TTL_TEMPLATES, key_builder=user_key_builder)
    async def list_templates(...): ...

Uso de CacheService en servicios:
    from app.core.cache import cache_service

    status = await cache_service.get_cv_status(cv_id)
    if not status:
        ...
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
    Centraliza TTLs y prefijos de caché del dominio CV.
    Modifica aquí y afecta a toda la app.
    """

    # ── TTLs (segundos) ───────────────────────────────────────────────────────
    TTL_TEMPLATES      = 3600    # Plantillas: 1 h  (cambian poco, admin-managed)
    TTL_PROJECTS       = 300     # Proyectos del usuario: 5 min
    TTL_SKILLS         = 300     # Skills del usuario: 5 min
    TTL_PERSONAL_INFO  = 600     # Info personal: 10 min
    TTL_CV_LIST        = 120     # Lista de CVs: 2 min
    TTL_CV_DETAIL      = 60      # Detalle de un CV: 1 min
    TTL_CV_STATUS      = 10      # Estado del job PDF: 10 seg (polling rápido)
    TTL_PDF_LOCK       = 300     # Lock de generación PDF: 5 min (máx. duración)
    TTL_HEALTH         = 15      # Health check: 15 seg

    # ── Prefijos ──────────────────────────────────────────────────────────────
    _PFX_CV        = "cv:"
    _PFX_PROJECT   = "project:"
    _PFX_SKILL     = "skill:"
    _PFX_TEMPLATE  = "template:"
    _PFX_PERSONAL  = "personal:"
    _PFX_STATUS    = "cv_status:"
    _PFX_LOCK      = "lock:"

    # ── Claves compuestas ─────────────────────────────────────────────────────

    @staticmethod
    def cv_status(cv_id: str | UUID) -> str:
        """Estado del job de generación PDF de un CV."""
        return f"{CacheKeys._PFX_STATUS}{cv_id}"

    @staticmethod
    def pdf_lock(cv_id: str | UUID) -> str:
        """Lock distribuido para la generación PDF de un CV concreto."""
        return f"{CacheKeys._PFX_LOCK}pdf:{cv_id}"

    @staticmethod
    def user_projects(user_id: str | UUID) -> str:
        """Clave de caché para el listado de proyectos de un usuario."""
        return f"{CacheKeys._PFX_PROJECT}user:{user_id}"

    @staticmethod
    def user_skills(user_id: str | UUID) -> str:
        """Clave de caché para las skills de un usuario."""
        return f"{CacheKeys._PFX_SKILL}user:{user_id}"

    @staticmethod
    def user_cv_list(user_id: str | UUID) -> str:
        """Clave de caché para la lista de CVs de un usuario."""
        return f"{CacheKeys._PFX_CV}list:{user_id}"

    @staticmethod
    def cv_detail(cv_id: str | UUID) -> str:
        """Clave de caché para el detalle de un CV."""
        return f"{CacheKeys._PFX_CV}detail:{cv_id}"


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
_service_pool    = _build_pool(settings.REDIS_DB_CACHE)


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
        log.info("cache.connected", host=settings.REDIS_HOST, db=settings.REDIS_DB_CACHE)
    except Exception as exc:
        log.error("cache.connection_failed", error=str(exc))
        raise

    FastAPICache.init(
        backend=RedisBackend(redis),
        prefix="cvgen:http:",
    )
    log.info("cache.initialized", backend="redis")


async def teardown_cache() -> None:
    """Libera pools Redis. Llamar en el lifespan shutdown de FastAPI."""
    await FastAPICache.clear()
    await _http_cache_pool.aclose()
    await _service_pool.aclose()
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
    Usar en todos los endpoints del dominio CV.
    """
    prefix   = FastAPICache.get_prefix()
    user_id  = request.headers.get("X-User-Id", "anon") if request else "anon"
    path     = request.url.path if request else ""
    query    = str(sorted(request.query_params.items())) if request else ""
    raw      = f"{namespace}:{user_id}:{path}:{query}"
    return f"{prefix}:{hashlib.md5(raw.encode()).hexdigest()}"


def cv_detail_key_builder(
    func: Any,
    namespace: str = "",
    request: Request | None = None,
    response: Response | None = None,
    args: tuple = (),
    kwargs: dict = {},
) -> str:
    """Key builder para el detalle de un CV concreto (incluye cv_id del path)."""
    prefix  = FastAPICache.get_prefix()
    user_id = request.headers.get("X-User-Id", "anon") if request else "anon"
    cv_id   = kwargs.get("cv_id", "")
    return f"{prefix}:cv:{user_id}:{cv_id}"


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
    path   = request.url.path if request else ""
    return f"{prefix}:templates:{hashlib.md5(path.encode()).hexdigest()}"


# ─────────────────────────────────────────────────────────────────────────────
# CacheService — caché de bajo nivel
# ─────────────────────────────────────────────────────────────────────────────

class CacheService:
    """
    Caché Redis de bajo nivel para operaciones internas del dominio CV.
    Complementa a fastapi-cache2 para datos no-HTTP.
    """

    def __init__(self) -> None:
        self._redis = get_redis_client()

    # ── Estado de generación PDF ──────────────────────────────────────────────

    async def set_cv_status(
        self,
        cv_id: str | UUID,
        status: str,
        error: str | None = None,
    ) -> None:
        """
        Persiste el estado del job de generación PDF para polling.
        El worker lo actualiza; el endpoint GET /cvs/{id}/status lo lee.
        """
        key     = CacheKeys.cv_status(cv_id)
        payload = {"status": status, "cv_id": str(cv_id)}
        if error:
            payload["error"] = error
        await self._redis.setex(key, CacheKeys.TTL_CV_STATUS, json.dumps(payload))
        log.debug("cache.cv_status.set", cv_id=str(cv_id), status=status)

    async def get_cv_status(self, cv_id: str | UUID) -> dict | None:
        """Retorna el estado cacheado del job PDF o None si expiró."""
        key   = CacheKeys.cv_status(cv_id)
        value = await self._redis.get(key)
        return json.loads(value) if value else None

    # ── Locks distribuidos ────────────────────────────────────────────────────

    async def acquire_pdf_lock(self, cv_id: str | UUID) -> bool:
        """
        Adquiere un lock exclusivo para generar el PDF de un CV.
        Evita que dos tareas Celery generen el mismo PDF en paralelo.

        Returns:
            True  → lock adquirido, proceder con la generación.
            False → otro worker ya está generando este CV.
        """
        key      = CacheKeys.pdf_lock(cv_id)
        acquired = await self._redis.set(key, "1", nx=True, ex=CacheKeys.TTL_PDF_LOCK)
        if acquired:
            log.debug("cache.pdf_lock.acquired", cv_id=str(cv_id))
        else:
            log.warning("cache.pdf_lock.already_held", cv_id=str(cv_id))
        return bool(acquired)

    async def release_pdf_lock(self, cv_id: str | UUID) -> None:
        """Libera el lock de generación PDF (siempre llamar en finally)."""
        key = CacheKeys.pdf_lock(cv_id)
        await self._redis.delete(key)
        log.debug("cache.pdf_lock.released", cv_id=str(cv_id))

    # ── Invalidación granular ─────────────────────────────────────────────────

    async def invalidate_user_projects(self, user_id: str | UUID) -> None:
        """Invalida el caché de proyectos de un usuario (tras crear/editar/borrar)."""
        await self._invalidate_pattern(f"cvgen:http:*project*{user_id}*")
        log.debug("cache.invalidated.projects", user_id=str(user_id))

    async def invalidate_user_skills(self, user_id: str | UUID) -> None:
        """Invalida el caché de skills de un usuario."""
        await self._invalidate_pattern(f"cvgen:http:*skill*{user_id}*")
        log.debug("cache.invalidated.skills", user_id=str(user_id))

    async def invalidate_cv(self, cv_id: str | UUID, user_id: str | UUID) -> None:
        """Invalida el caché de un CV concreto y la lista de CVs del usuario."""
        await self._invalidate_pattern(f"cvgen:http:*cv*{user_id}*")
        await self._invalidate_pattern(f"cvgen:http:*cv*{cv_id}*")
        log.debug("cache.invalidated.cv", cv_id=str(cv_id), user_id=str(user_id))

    async def invalidate_templates(self) -> None:
        """Invalida el caché de plantillas (solo admin lo necesita)."""
        await self._invalidate_pattern("cvgen:http:*templates*")
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