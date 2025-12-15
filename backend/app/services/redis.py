# app/core/redis_service.py

import redis
from redis import asyncio as aioredis
import logging

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisService:
    """
    Servicio unificado de conexión a Redis.
    Provee acceso tanto asíncrono como sincrónico.
    """

    _async_client: aioredis.Redis | None = None
    _sync_client: redis.Redis | None = None

    @classmethod
    async def init_async(cls) -> None:
        """
        Inicializa la conexión asíncrona y FastAPICache.
        Se debe llamar en el evento startup de FastAPI.
        """
        logger.debug("Iniciando conexión Redis (async) a %s", settings.REDIS_URL)
        try:
            cls._async_client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            pong = await cls._async_client.ping()
            if pong:
                FastAPICache.init(RedisBackend(cls._async_client), prefix="fastapi-cache")
                logger.info("RedisService (async) conectado y FastAPICache inicializado.")
            else:
                logger.warning("RedisService (async) conectado pero ping devolvió falsy: %s", pong)
        except Exception as e:
            logger.exception("Error conectando Redis (async): %s", e)
            cls._async_client = None

    @classmethod
    def init_sync(cls) -> None:
        """
        Inicializa la conexión sincrónica, útil para código no async.
        """
        logger.debug("Iniciando conexión Redis (sync) a %s", settings.REDIS_URL)
        try:
            cls._sync_client = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            pong = cls._sync_client.ping()
            if pong:
                logger.info("RedisService (sync) conectado exitosamente.")
            else:
                logger.warning("RedisService (sync) conectado pero ping devolvió falsy: %s", pong)
        except redis.exceptions.ConnectionError as e:
            logger.exception("Error conectando Redis (sync): %s", e)
            cls._sync_client = None
        except Exception as e:
            logger.exception("Error inesperado inicializando Redis (sync): %s", e)
            cls._sync_client = None

    @classmethod
    def get_sync(cls) -> redis.Redis | None:
        """Devuelve el cliente sincrónico."""
        logger.debug("Obteniendo cliente Redis (sync): %s", "disponible" if cls._sync_client else "None")
        return cls._sync_client

    @classmethod
    def get_async(cls) -> aioredis.Redis | None:
        """Devuelve el cliente asíncrono."""
        logger.debug("Obteniendo cliente Redis (async): %s", "disponible" if cls._async_client else "None")
        return cls._async_client
