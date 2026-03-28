"""
Middlewares personalizados de la aplicación.

Este módulo contiene todos los middlewares HTTP personalizados que se aplican
a la aplicación FastAPI para agregar funcionalidad transversal.

Middlewares disponibles:
    - protect_internal_docs: Protege la documentación interna con JWT
    - invalidate_cache_on_write: Invalida caché automáticamente en operaciones de escritura

Uso:
    from app.middleware import setup_middlewares

    app = FastAPI()
    setup_middlewares(app)
"""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import settings
from app.core.security import ALGORITHM
from app.enums import UserRole
from app.services import RedisService

# Configurar logger para este módulo
logger = logging.getLogger(__name__)


async def protect_internal_docs_middleware(request: Request, call_next):
    """
    Middleware para proteger la documentación interna.

    En desarrollo: Acceso público sin autenticación
    En producción: Solo usuarios con rol DEVELOPER pueden acceder a /internal-docs/

    Valida el token JWT y verifica el rol del usuario en producción.

    Soporta tres métodos de autenticación:
    1. Header Authorization: Bearer <token>
    2. Query parameter: ?token=<token> (para acceso inicial desde navegador)
    3. Cookie: internal_docs_token (se establece automáticamente después del primer acceso)

    Cuando se accede con ?token=, el middleware guarda el token en una cookie
    para que las navegaciones subsecuentes dentro de /internal-docs/ no requieran
    el parámetro en la URL.

    Los archivos estáticos (CSS, JS, imágenes, etc.) pasan sin validación
    para permitir que la documentación se muestre correctamente.

    Args:
        request: Request HTTP entrante
        call_next: Siguiente middleware/handler en la cadena

    Returns:
        Response del siguiente handler o JSONResponse con error
    """
    path = request.url.path

    # Protege todo lo que empiece con /internal-docs
    if path.startswith("/internal-docs"):
        # 🆓 En desarrollo/local, permitir acceso público sin autenticación
        if settings.ENVIRONMENT in ("development", "local"):
            logger.debug(
                f"📖 Acceso público a documentación interna ({settings.ENVIRONMENT}): {path}"
            )
            return await call_next(request)

        # 🔒 En producción, validar autenticación
        # Permitir archivos estáticos sin autenticación (CSS, JS, imágenes, fuentes, etc.)
        static_extensions = (
            ".css",
            ".js",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".ico",
            ".woff",
            ".woff2",
            ".ttf",
            ".eot",
            ".map",
            ".webp",
            ".webmanifest",
        )

        if path.endswith(static_extensions):
            # Los archivos estáticos pasan sin validación
            return await call_next(request)

        # Para archivos HTML y el resto, validar autenticación
        # Obtener token de múltiples fuentes (header, query param, cookie)
        auth_header = request.headers.get("Authorization")
        query_token = request.query_params.get("token")
        cookie_token = request.cookies.get("internal_docs_token")

        # Prioridad: header Authorization > query param > cookie
        token = None
        token_from_query = False

        if auth_header:
            try:
                # Validar formato del header
                parts = auth_header.split()
                if len(parts) == 2 and parts[0].lower() == "bearer":
                    token = parts[1]
            except Exception:
                pass
        elif query_token:
            token = query_token
            token_from_query = True  # Marcar que el token vino del query param
        elif cookie_token:
            token = cookie_token

        if not token:
            logger.warning(
                f"🔒 Intento de acceso sin token a documentación interna: {path}"
            )
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "No autenticado. Se requiere token de acceso.",
                    "message": "Debes iniciar sesión para acceder a la documentación interna.",
                    "help": "Puedes autenticarte de tres formas:",
                    "methods": [
                        "1. Header: Authorization: Bearer <token>",
                        "2. Query param: ?token=<token> (recomendado para navegador)",
                        "3. Cookie: Se establece automáticamente al usar ?token=",
                    ],
                },
            )

        try:
            # Decodificar y validar el token JWT
            payload = jwt.decode(
                token,
                settings.SECRET_KEY.get_secret_value(),
                algorithms=[ALGORITHM],
            )

            # Extraer el rol del usuario del payload
            user_role = payload.get("role")

            if not user_role:
                logger.warning(f"🔒 Token sin rol detectado al acceder a: {path}")
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": "Token inválido: rol no encontrado",
                        "message": "El token no contiene información de rol",
                    },
                )

            # Verificar que el rol sea DEVELOPER
            if user_role != UserRole.DEVELOPER.value:
                logger.warning(
                    f"🔒 Acceso denegado a documentación interna. Rol '{user_role}' intentó acceder a: {path}"
                )
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": "Acceso denegado: se requiere rol de desarrollador",
                        "message": f"Tu rol actual ({user_role}) no tiene acceso a la documentación interna. Solo usuarios con rol 'developer' pueden acceder.",
                        "required_role": UserRole.DEVELOPER.value,
                        "current_role": user_role,
                    },
                )

            # Acceso exitoso
            logger.info(
                f"✅ Acceso concedido a documentación interna: {path} (rol: {user_role})"
            )

            # Procesar la petición
            response = await call_next(request)

            # Si el token vino del query param, establecer cookie para futuras peticiones
            if token_from_query:
                # Establecer cookie con el token para que persista en navegaciones
                response.set_cookie(
                    key="internal_docs_token",
                    value=token,
                    max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES
                    * 60,  # Convertir minutos a segundos
                    httponly=True,  # No accesible desde JavaScript (seguridad)
                    secure=settings.ENVIRONMENT
                    == "production",  # Solo HTTPS en producción
                    samesite="lax",  # Protección CSRF
                    path="/internal-docs",  # Solo para rutas de documentación
                )
                logger.info(
                    f"🍪 Cookie de autenticación establecida para documentación interna"
                )

            return response

        except InvalidTokenError as e:
            logger.warning(
                f"🔒 Token inválido o expirado al acceder a: {path} - {str(e)}"
            )
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Token inválido o expirado",
                    "message": "El token de autenticación no es válido o ha expirado. Por favor, inicia sesión nuevamente.",
                    "error": str(e),
                },
            )
        except ValueError as e:
            logger.error(f"⚠️  Error de formato en autenticación: {path} - {str(e)}")
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Error en formato de autenticación",
                    "message": str(e),
                },
            )
        except Exception as e:
            logger.error(
                f"⚠️  Error interno al validar autenticación: {path} - {str(e)}",
                exc_info=True,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Error interno del servidor",
                    "message": "Ocurrió un error al validar la autenticación",
                    "error": str(e),
                },
            )

    # Si pasa la validación o no es ruta protegida, continúa normalmente
    return await call_next(request)


async def invalidate_cache_on_write_middleware(request: Request, call_next):
    """
    Middleware para invalidar el caché automáticamente en operaciones de escritura.

    Cuando se realizan operaciones de escritura exitosas (POST, PUT, PATCH, DELETE)
    sobre ciertos recursos, se invalida el caché relacionado automáticamente.

    Recursos monitoreados (todos los del sistema Feature Models):
    - /users/: Invalida caché de usuarios
    - /domains/: Invalida caché de dominios y sus feature models relacionados
    - /feature-models/: Invalida caché de feature models, features, relations y constraints
    - /features/: Invalida caché de features y sus relaciones
    - /feature-relations/: Invalida caché de relaciones entre features
    - /feature-groups/: Invalida caché de grupos de features
    - /constraints/: Invalida caché de constraints
    - /configurations/: Invalida caché de configuraciones
    - /resources/: Invalida caché de recursos educativos
    - /tags/: Invalida caché de tags y sus asociaciones

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
            # Usuarios
            "/users": ["fastapi-cache:*users*"],
            # Dominios - también invalida feature models del dominio
            "/domains": [
                "fastapi-cache:*domains*",
                "fastapi-cache:*feature-models*",
            ],
            # Feature Models - invalida todo el árbol de features relacionado
            "/feature-models": [
                "fastapi-cache:*feature-models*",
                "fastapi-cache:*features*",
                "fastapi-cache:*feature-relations*",
                "fastapi-cache:*feature-groups*",
                "fastapi-cache:*constraints*",
                "fastapi-cache:*configurations*",
            ],
            # Features - invalida features, relations y groups
            "/features": [
                "fastapi-cache:*features*",
                "fastapi-cache:*feature-relations*",
                "fastapi-cache:*feature-groups*",
            ],
            # Feature Relations
            "/feature-relations": [
                "fastapi-cache:*feature-relations*",
                "fastapi-cache:*features*",
            ],
            # Feature Groups
            "/feature-groups": [
                "fastapi-cache:*feature-groups*",
                "fastapi-cache:*features*",
            ],
            # Constraints
            "/constraints": [
                "fastapi-cache:*constraints*",
                "fastapi-cache:*features*",
            ],
            # Configurations
            "/configurations": [
                "fastapi-cache:*configurations*",
            ],
            # Resources (recursos educativos)
            "/resources": [
                "fastapi-cache:*resources*",
            ],
            # Tags - también invalida asociaciones de features con tags
            "/tags": [
                "fastapi-cache:*tags*",
                "fastapi-cache:*features*",
            ],
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
                    redis = await RedisService.get_redis()
                    for pattern in patterns_to_invalidate:
                        await _invalidate_cache_pattern(redis, pattern)
                except Exception as e:
                    logger.error(
                        f"⚠️  Error al invalidar caché después de {request.method} {path}: {e}",
                        exc_info=True,
                    )

        return response
    else:
        # Métodos de lectura (GET, HEAD, OPTIONS) pasan sin modificación
        return await call_next(request)


async def _invalidate_cache_pattern(redis_client, pattern: str):
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


def setup_middlewares(app: FastAPI) -> None:
    """
    Configura todos los middlewares personalizados de la aplicación.

    Esta función debe ser llamada después de crear la instancia de FastAPI
    y antes de incluir los routers.

    Middlewares registrados (en orden de ejecución):
    1. invalidate_cache_on_write_middleware: Invalida caché en escrituras
    2. protect_internal_docs_middleware: Protege documentación interna

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

    # Registrar middleware de protección de documentación interna
    app.middleware("http")(protect_internal_docs_middleware)

    logger.info("✅ Middlewares configurados correctamente")
    logger.info("  - 🔄 Cache invalidation middleware (POST/PUT/PATCH/DELETE)")
    logger.info("  - 🔒 Internal docs protection middleware (/internal-docs)")
