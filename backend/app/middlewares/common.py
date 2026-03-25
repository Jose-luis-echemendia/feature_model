import logging

from fastapi import Request
from app.core.redis import redis_client
from app.utils import invalidate_cache_pattern

# Configurar logger para este módulo
logger = logging.getLogger(__name__)

# Tamaño máximo de payload en bytes (10MB por defecto)
MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10MB


async def invalidate_cache_on_write_middleware(request: Request, call_next):
    """
    Middleware para invalidar el caché automáticamente en operaciones de escritura.

    Cuando se realizan operaciones de escritura exitosas (POST, PUT, PATCH, DELETE)
    sobre ciertos recursos, se invalida el caché relacionado automáticamente.

    Recursos monitoreados (todos los del sistema):
    - /app-settings/: Invalida caché de configuraciones

    La invalidación se hace de forma asíncrona usando SCAN (no bloquea Redis)
    y solo se elimina las claves que coincidan con el patrón específico.

    Args:
        request: Request HTTP entrante
        call_next: Siguiente middleware/handler en la cadena

    Returns:
        Response del handler
    """
    # Solo procesar métodos de escritura
    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        path = request.url.path

        # Diccionario de rutas y sus patrones de caché relacionados
        # Cada entrada puede tener múltiples patrones para invalidar caché relacionado
        cache_invalidation_map = {
            # App Settings
            "/app-settings": [
                "fastapi-cache:*app-settings*",
            ],
        }

        # Procesar la request
        response = await call_next(request)

        # Solo invalidar si la operación fue exitosa (2xx)
        if 200 <= response.status_code < 300:
            # Buscar coincidencias en el mapa de invalidación
            patterns_to_invalidate = []

            for route_prefix, patterns in cache_invalidation_map.items():
                if path.startswith(route_prefix):
                    patterns_to_invalidate.extend(patterns)
                    logger.info(
                        f"🔄 Operación de escritura exitosa en {path} ({request.method}). "
                        f"Invalidando caché: {', '.join(patterns)}"
                    )
                    break

            # Invalidar todos los patrones encontrados
            if patterns_to_invalidate:
                try:
                    for pattern in patterns_to_invalidate:
                        await invalidate_cache_pattern(redis_client, pattern)
                except Exception as e:
                    logger.error(
                        f"⚠️  Error al invalidar caché después de {request.method} {path}: {e}",
                        exc_info=True,
                    )

        return response
    else:
        # Métodos de lectura (GET, HEAD, OPTIONS) pasan sin modificación
        return await call_next(request)
