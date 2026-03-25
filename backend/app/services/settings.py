import json
import logging
from typing import Any

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.app_setting import AppSetting
from app.core.redis import redis_client

logger = logging.getLogger(__name__)

CACHE_KEY_PREFIX = "app_settings:"
CACHE_EXPIRATION_SECONDS = 3600  # 1 hora


class SettingsService:
    """
    Servicio para gestionar configuraciones de la aplicación.
    Modo asíncrono, operando con cliente Redis centralizado.
    """

    def __init__(self, session: AsyncSession):
        self.db = session
        logger.debug("SettingsService inicializado.")

    async def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor desde Redis o la base de datos."""
        logger.debug("get(key='%s') iniciado.", key)

        cache_key = f"{CACHE_KEY_PREFIX}{key}"
        try:
            cached_value = await redis_client.get(cache_key)
            if cached_value is not None:
                logger.debug("Cache HIT para key='%s'", cache_key)
            else:
                logger.debug("Cache MISS para key='%s'", cache_key)
        except Exception as e:
            logger.exception("Error leyendo cache Redis para key='%s': %s", cache_key, e)
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
        db_setting = await self.db.get(AppSetting, key)

        if db_setting is None:
            logger.debug(
                "Key '%s' no encontrada en BD, devolviendo default=%s", key, default
            )
            return default

        try:
            await redis_client.set(
                cache_key, json.dumps(db_setting.value), ex=CACHE_EXPIRATION_SECONDS
            )
            logger.debug(
                "Cache establecida para key='%s' con TTL=%ds",
                cache_key,
                CACHE_EXPIRATION_SECONDS,
            )
        except Exception as e:
            logger.exception("Error estableciendo cache para key='%s': %s", cache_key, e)

        logger.debug(
            "Valor retornado desde BD para key='%s', type=%s",
            key,
            type(db_setting.value).__name__,
        )
        return db_setting.value

    async def update(self, key: str, value: Any, description: str = None) -> AppSetting:
        """Actualiza o crea un valor en la BD y la caché."""
        logger.debug(
            "update(key='%s') iniciado. value_type=%s, description=%s",
            key,
            type(value).__name__,
            description,
        )

        db_setting = await self.db.get(AppSetting, key)
        if db_setting:
            logger.debug("Actualizando setting existente: key='%s'", key)
            db_setting.value = value
            if description is not None:
                db_setting.description = description
        else:
            logger.debug("Creando nuevo setting: key='%s'", key)
            db_setting = AppSetting(key=key, value=value, description=description)

        self.db.add(db_setting)
        await self.db.commit()
        await self.db.refresh(db_setting)
        logger.info("Setting guardado en BD: key='%s'", key)

        try:
            await redis_client.set(
                f"{CACHE_KEY_PREFIX}{key}",
                json.dumps(db_setting.value),
                ex=CACHE_EXPIRATION_SECONDS,
            )
            logger.debug("Cache actualizada para key='%s'", key)
        except Exception as e:
            logger.exception("Error actualizando cache para key='%s': %s", key, e)

        return db_setting

    async def clear_cache_for_key(self, key: str):
        """Limpia la caché de una clave específica."""
        logger.debug("clear_cache_for_key(key='%s') iniciado", key)
        try:
            cache_key = f"{CACHE_KEY_PREFIX}{key}"
            await redis_client.delete(cache_key)
            logger.info("Cache eliminada para setting: key='%s'", key)
        except Exception as e:
            logger.exception("Error eliminando cache para key='%s': %s", key, e)

    async def clear_all_cache(self):
        """Limpia toda la caché de configuraciones."""
        logger.debug("clear_all_cache() iniciado")
        try:
            keys_to_delete = await redis_client.keys(f"{CACHE_KEY_PREFIX}*")
            count = len(keys_to_delete) if keys_to_delete else 0
            logger.debug(
                "Encontradas %d keys para eliminar con patrón '%s*'",
                count,
                CACHE_KEY_PREFIX,
            )

            if keys_to_delete:
                await redis_client.delete(*keys_to_delete)
                logger.info("Cache completa de settings eliminada (%d keys)", count)
            else:
                logger.debug("No hay keys de cache para eliminar")
        except Exception as e:
            logger.exception("Error eliminando todas las cache de settings: %s", e)
