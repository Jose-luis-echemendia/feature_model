"""
Middlewares personalizados de la aplicación.

Este módulo contiene todos los middlewares HTTP personalizados que se aplican
a la aplicación FastAPI para agregar funcionalidad transversal.

Middlewares disponibles:
    - invalidate_cache_on_write: Invalida caché automáticamente en operaciones de escritura

Uso:
    from app.middleware import setup_middlewares

    app = FastAPI()
    setup_middlewares(app)
"""

import logging

from fastapi import FastAPI
from .common import (
    invalidate_cache_on_write_middleware,
)

# Configurar logger para este módulo
logger = logging.getLogger(__name__)


def setup_middlewares(app: FastAPI) -> None:
    """
    Configura todos los middlewares personalizados de la aplicación.

    Esta función debe ser llamada después de crear la instancia de FastAPI
    y antes de incluir los routers.

    Middlewares registrados (en orden de ejecución):
    1. invalidate_cache_on_write_middleware: Invalida caché en escrituras

    Args:
        app: Instancia de FastAPI

    Ejemplo:
        ```python
        from fastapi import FastAPI
        from app.middleware import setup_middlewares

        app = FastAPI()
        setup_middlewares(app)
        ```
    """
    # Registrar middleware de invalidación de caché (primero para que se ejecute después)
    app.middleware("http")(invalidate_cache_on_write_middleware)

    logger.info("✅ Middlewares configurados correctamente")
    logger.info("  - 🔄 Cache invalidation middleware (POST/PUT/PATCH/DELETE)")
