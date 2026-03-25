import logging


# Configurar logger para este módulo
logger = logging.getLogger(__name__)


async def invalidate_cache_pattern(redis_client, pattern: str):
    """
    Invalida todas las claves de caché que coincidan con el patrón dado.

    Usa SCAN en lugar de KEYS para evitar bloquear Redis en producción.

    Args:
        redis_client: Cliente de Redis (asíncrono)
        pattern: Patrón de búsqueda (ej: "fastapi-cache:*features*")
    """
    try:
        # Buscar todas las claves que coincidan con el patrón usando SCAN
        keys = []
        cursor = 0

        while True:
            cursor, partial_keys = await redis_client.scan(
                cursor, match=pattern, count=100
            )
            keys.extend(partial_keys)
            if cursor == 0:
                break

        if keys:
            # Eliminar todas las claves encontradas
            deleted_count = await redis_client.delete(*keys)
            logger.info(
                f"🗑️  Invalidadas {deleted_count} claves de caché con patrón: {pattern}"
            )
        else:
            logger.debug(
                f"🔍 No se encontraron claves para invalidar con patrón: {pattern}"
            )
    except Exception as e:
        logger.error(f"⚠️  Error al invalidar patrón {pattern}: {e}", exc_info=True)

