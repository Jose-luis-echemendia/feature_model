import json, logging

from typing import Any
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.app_setting import AppSetting
from app.services.redis import RedisService

logger = logging.getLogger(__name__)

CACHE_KEY_PREFIX = "app_settings:"
CACHE_EXPIRATION_SECONDS = 3600  # 1 hora


class SettingsService:
    """
    Servicio para gestionar configuraciones de la aplicación.
    Compatible con uso síncrono y asíncrono.
    """

    def __init__(self, session: Session | AsyncSession):
        self.db = session
        self.redis_sync = RedisService.get_sync()
        self.redis_async = RedisService.get_async()
        logger.debug(
            "SettingsService inicializado. redis_sync=%s, redis_async=%s",
            "disponible" if self.redis_sync else "None",
            "disponible" if self.redis_async else "None",
        )

    # ==========================================================
    # 🧩 MÉTODOS SINCRÓNICOS
    # ==========================================================

    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor desde Redis o la base de datos (modo síncrono)."""
        logger.debug(
            "get(key='%s') iniciado. redis_sync=%s", key, bool(self.redis_sync)
        )

        if not self.redis_sync:
            logger.debug(
                "Sin cliente Redis síncrono, leyendo directamente desde BD para key='%s'",
                key,
            )
            db_setting = self.db.get(AppSetting, key)
            if db_setting:
                logger.debug(
                    "Valor obtenido desde BD: key='%s', value_type=%s",
                    key,
                    type(db_setting.value).__name__,
                )
                return db_setting.value
            else:
                logger.debug(
                    "Key '%s' no encontrada en BD, devolviendo default=%s", key, default
                )
                return default

        cache_key = f"{CACHE_KEY_PREFIX}{key}"
        try:
            cached_value = self.redis_sync.get(cache_key)
            if cached_value is not None:
                logger.debug("Cache HIT para key='%s'", cache_key)
            else:
                logger.debug("Cache MISS para key='%s'", cache_key)
        except Exception as e:
            logger.exception(
                "Error leyendo cache Redis para key='%s': %s", cache_key, e
            )
            cached_value = None

        if cached_value is not None:
            try:
                value = json.loads(cached_value)
                logger.debug("Cache deserializado exitosamente para key='%s'", key)
                return value
            except json.JSONDecodeError as e:
                logger.warning(
                    "No se pudo deserializar JSON para key='%s', devolviendo string crudo. Error: %s",
                    key,
                    e,
                )
                return cached_value

        logger.debug("Consultando BD para key='%s'", key)
        db_setting = self.db.get(AppSetting, key)
        if db_setting is None:
            logger.debug(
                "Key '%s' no encontrada en BD, devolviendo default=%s", key, default
            )
            return default

        try:
            self.redis_sync.set(
                cache_key, json.dumps(db_setting.value), ex=CACHE_EXPIRATION_SECONDS
            )
            logger.debug(
                "Cache establecida para key='%s' con TTL=%ds",
                cache_key,
                CACHE_EXPIRATION_SECONDS,
            )
        except Exception as e:
            logger.exception(
                "Error estableciendo cache para key='%s': %s", cache_key, e
            )

        logger.debug(
            "Valor retornado desde BD para key='%s', type=%s",
            key,
            type(db_setting.value).__name__,
        )
        return db_setting.value

    def update(self, key: str, value: Any, description: str = None) -> AppSetting:
        """Actualiza o crea un valor en la BD y la caché (modo síncrono)."""
        logger.debug(
            "update(key='%s') iniciado. value_type=%s, description=%s",
            key,
            type(value).__name__,
            description,
        )

        db_setting = self.db.get(AppSetting, key)
        if db_setting:
            logger.debug("Actualizando setting existente: key='%s'", key)
            db_setting.value = value
            if description:
                db_setting.description = description
        else:
            logger.debug("Creando nuevo setting: key='%s'", key)
            db_setting = AppSetting(key=key, value=value, description=description)

        self.db.add(db_setting)
        self.db.commit()
        self.db.refresh(db_setting)
        logger.info("Setting guardado en BD: key='%s'", key)

        if self.redis_sync:
            try:
                self.redis_sync.set(
                    f"{CACHE_KEY_PREFIX}{key}",
                    json.dumps(db_setting.value),
                    ex=CACHE_EXPIRATION_SECONDS,
                )
                logger.debug("Cache actualizada para key='%s'", key)
            except Exception as e:
                logger.exception("Error actualizando cache para key='%s': %s", key, e)
        else:
            logger.debug(
                "Sin cliente Redis síncrono, cache no actualizada para key='%s'", key
            )

        return db_setting

    def clear_cache_for_key(self, key: str):
        logger.debug("clear_cache_for_key(key='%s') iniciado", key)
        if self.redis_sync:
            try:
                cache_key = f"{CACHE_KEY_PREFIX}{key}"
                self.redis_sync.delete(cache_key)
                logger.info("Cache eliminada para setting: key='%s'", key)
            except Exception as e:
                logger.exception("Error eliminando cache para key='%s': %s", key, e)
        else:
            logger.debug(
                "Sin cliente Redis síncrono, no se puede limpiar cache para key='%s'",
                key,
            )

    def clear_all_cache(self):
        logger.debug("clear_all_cache() iniciado")
        if self.redis_sync:
            try:
                keys_to_delete = self.redis_sync.keys(f"{CACHE_KEY_PREFIX}*")
                count = len(keys_to_delete) if keys_to_delete else 0
                logger.debug(
                    "Encontradas %d keys para eliminar con patrón '%s*'",
                    count,
                    CACHE_KEY_PREFIX,
                )

                if keys_to_delete:
                    self.redis_sync.delete(*keys_to_delete)
                    logger.info("Cache completa de settings eliminada (%d keys)", count)
                else:
                    logger.debug("No hay keys de cache para eliminar")
            except Exception as e:
                logger.exception("Error eliminando todas las cache de settings: %s", e)
        else:
            logger.debug(
                "Sin cliente Redis síncrono, no se puede limpiar cache completa"
            )

    # ==========================================================
    # ⚡ MÉTODOS ASÍNCRONOS
    # ==========================================================

    async def aget(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor desde Redis o la base de datos (modo asíncrono)."""
        logger.debug(
            "aget(key='%s') iniciado. redis_async=%s", key, bool(self.redis_async)
        )

        if self.redis_async:
            cache_key = f"{CACHE_KEY_PREFIX}{key}"
            try:
                cached_value = await self.redis_async.get(cache_key)
                if cached_value is not None:
                    logger.debug("Cache HIT (async) para key='%s'", cache_key)
                else:
                    logger.debug("Cache MISS (async) para key='%s'", cache_key)
            except Exception as e:
                logger.exception(
                    "Error leyendo cache Redis async para key='%s': %s", cache_key, e
                )
                cached_value = None

            if cached_value is not None:
                try:
                    value = json.loads(cached_value)
                    logger.debug(
                        "Cache deserializado exitosamente (async) para key='%s'", key
                    )
                    return value
                except json.JSONDecodeError as e:
                    logger.warning(
                        "No se pudo deserializar JSON (async) para key='%s', devolviendo string crudo. Error: %s",
                        key,
                        e,
                    )
                    return cached_value

        logger.debug("Consultando BD (async) para key='%s'", key)
        db_setting = await self.db.get(AppSetting, key)

        if db_setting is None:
            logger.debug(
                "Key '%s' no encontrada en BD (async), devolviendo default=%s",
                key,
                default,
            )
            return default

        if self.redis_async:
            try:
                await self.redis_async.set(
                    cache_key, json.dumps(db_setting.value), ex=CACHE_EXPIRATION_SECONDS
                )
                logger.debug(
                    "Cache establecida (async) para key='%s' con TTL=%ds",
                    cache_key,
                    CACHE_EXPIRATION_SECONDS,
                )
            except Exception as e:
                logger.exception(
                    "Error estableciendo cache (async) para key='%s': %s", cache_key, e
                )

        logger.debug(
            "Valor retornado desde BD (async) para key='%s', type=%s",
            key,
            type(db_setting.value).__name__,
        )
        return db_setting.value

    async def aupdate(
        self, key: str, value: Any, description: str = None
    ) -> AppSetting:
        logger.debug(
            "aupdate(key='%s') iniciado. value_type=%s, description=%s",
            key,
            type(value).__name__,
            description,
        )

        db_setting = await self.db.get(AppSetting, key)
        if db_setting:
            logger.debug("Actualizando setting existente (async): key='%s'", key)
            db_setting.value = value
            if description:
                db_setting.description = description
        else:
            logger.debug("Creando nuevo setting (async): key='%s'", key)
            db_setting = AppSetting(key=key, value=value, description=description)

        self.db.add(db_setting)
        await self.db.commit()
        await self.db.refresh(db_setting)
        logger.info("Setting guardado en BD (async): key='%s'", key)

        if self.redis_async:
            try:
                await self.redis_async.set(
                    f"{CACHE_KEY_PREFIX}{key}",
                    json.dumps(db_setting.value),
                    ex=CACHE_EXPIRATION_SECONDS,
                )
                logger.debug("Cache actualizada (async) para key='%s'", key)
            except Exception as e:
                logger.exception(
                    "Error actualizando cache (async) para key='%s': %s", key, e
                )
        else:
            logger.debug(
                "Sin cliente Redis async, cache no actualizada para key='%s'", key
            )

        return db_setting

    async def aclear_cache_for_key(self, key: str):
        """Limpia la caché de una clave específica (modo asíncrono)."""
        logger.debug("aclear_cache_for_key(key='%s') iniciado", key)
        if self.redis_async:
            try:
                cache_key = f"{CACHE_KEY_PREFIX}{key}"
                await self.redis_async.delete(cache_key)
                logger.info("Cache eliminada (async) para setting: key='%s'", key)
            except Exception as e:
                logger.exception(
                    "Error eliminando cache (async) para key='%s': %s", key, e
                )
        else:
            logger.debug(
                "Sin cliente Redis async, no se puede limpiar cache para key='%s'", key
            )

    async def aclear_all_cache(self):
        """Limpia toda la caché de configuraciones (modo asíncrono)."""
        logger.debug("aclear_all_cache() iniciado")
        if self.redis_async:
            try:
                keys_to_delete = await self.redis_async.keys(f"{CACHE_KEY_PREFIX}*")
                count = len(keys_to_delete) if keys_to_delete else 0
                logger.debug(
                    "Encontradas %d keys (async) para eliminar con patrón '%s*'",
                    count,
                    CACHE_KEY_PREFIX,
                )

                if keys_to_delete:
                    await self.redis_async.delete(*keys_to_delete)
                    logger.info(
                        "Cache completa de settings eliminada (async) (%d keys)", count
                    )
                else:
                    logger.debug("No hay keys de cache (async) para eliminar")
            except Exception as e:
                logger.exception(
                    "Error eliminando todas las cache de settings (async): %s", e
                )
        else:
            logger.debug("Sin cliente Redis async, no se puede limpiar cache completa")
