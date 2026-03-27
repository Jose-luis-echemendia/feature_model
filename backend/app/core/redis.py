"""
app/core/redis.py

Cliente Redis centralizado para el dominio de Feature Models.

Provee:
    - Dos pools independientes: uno para `CacheService` y otro
        disponible para uso directo en servicios/tareas.
  - Dependency de FastAPI (get_redis) para inyección en rutas.
  - Health check.
  - Función de inicialización/cierre para el lifespan.

Uso en servicios:
    from app.core.redis import redis_client
    await redis_client.set("key", "value", ex=60)

Uso como dependency en rutas:
    from app.core.redis import get_redis
    async def my_route(redis: Redis = Depends(get_redis)): ...
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from redis.asyncio import ConnectionPool, Redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError, TimeoutError

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Factory de pools
# ─────────────────────────────────────────────────────────────────────────────


def _build_pool(db: int, max_connections: int = 20) -> ConnectionPool:
    """
    Construye un ConnectionPool Redis con:
      - Reintentos exponenciales (3 intentos, cap 10 s)
      - Health check cada 30 s para descartar conexiones muertas
      - Timeout de conexión y socket de 5 s
      - decode_responses=True → todos los valores son str, no bytes
    """
    password = settings.REDIS_PASSWORD
    auth = f":{password.get_secret_value()}@" if password else ""
    url = f"redis://{auth}{settings.REDIS_HOST}:{settings.REDIS_PORT}/{db}"

    return ConnectionPool.from_url(
        url,
        max_connections=max_connections,
        decode_responses=True,
        retry=Retry(
            ExponentialBackoff(cap=10, base=0.5),
            retries=3,
        ),
        retry_on_error=[ConnectionError, TimeoutError],
        socket_connect_timeout=5,
        socket_timeout=5,
        health_check_interval=30,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Pools
# ─────────────────────────────────────────────────────────────────────────────

# Pool principal — caché de la app
# Compartido entre CacheService y cualquier uso directo en servicios.
_cache_pool: ConnectionPool = _build_pool(
    db=settings.REDIS_DB_CACHE,
    max_connections=20,
)

# Pool secundario — uso puntual en rutas via Depends(get_redis)
# Mismo DB que `_cache_pool`, pero separado para no saturarlo.
_request_pool: ConnectionPool = _build_pool(
    db=settings.REDIS_DB_CACHE,
    max_connections=10,
)


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


# ─────────────────────────────────────────────────────────────────────────────
# Clientes
# ─────────────────────────────────────────────────────────────────────────────

# Singleton para usar en servicios y tareas Celery:
#   from app.core.redis import redis_client
redis_client: Redis = Redis(connection_pool=_cache_pool)


# ─────────────────────────────────────────────────────────────────────────────
# Dependency FastAPI
# ─────────────────────────────────────────────────────────────────────────────


async def get_redis() -> AsyncGenerator[Redis, None]:
    """
    Dependency de FastAPI — inyecta un cliente Redis por request.
    Usa el pool secundario para no bloquear el CacheService.

    Uso:
        @router.get("/")
        async def route(redis: Redis = Depends(get_redis)):
            await redis.set("key", "value", ex=60)
    """
    client = Redis(connection_pool=_request_pool)
    try:
        yield client
    finally:
        await client.aclose()


# ─────────────────────────────────────────────────────────────────────────────
# Lifecycle — llamar desde el lifespan de main.py
# ─────────────────────────────────────────────────────────────────────────────


async def setup_redis() -> None:
    """
    Verifica la conexión a Redis al arrancar.
    Lanza excepción si Redis no está disponible — la app no debe arrancar sin él.
    """
    try:
        await redis_client.ping()
        log.info(
            "redis.connected",
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db_cache=settings.REDIS_DB_CACHE,
        )
    except Exception as exc:
        log.error("redis.connection_failed", error=str(exc))
        raise


async def teardown_redis() -> None:
    """Cierra los pools al apagar la app."""
    await _close_pool(_cache_pool)
    await _close_pool(_request_pool)
    log.info("redis.pools_closed")


# ─────────────────────────────────────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────────────────────────────────────


async def check_redis() -> bool:
    """
    Comprueba que Redis responde. Usado en GET /health.
    Retorna False en lugar de lanzar excepción.
    """
    try:
        return bool(await redis_client.ping())
    except Exception as exc:
        log.error("redis.health_check.failed", error=str(exc))
        return False
