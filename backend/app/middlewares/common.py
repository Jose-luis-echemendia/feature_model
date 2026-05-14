import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import settings
from app.core.redis import redis_client
from app.core.security import ALGORITHM, require_api_key
from app.enums import UserRole
from app.utils import invalidate_cache_pattern

# Configurar logger para este módulo
logger = logging.getLogger(__name__)

# Tamaño máximo de payload en bytes (10MB por defecto)
MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10MB


def _is_api_key_exempt_path(path: str) -> bool:
    """Indica si una ruta debe quedar exenta de la API key."""
    api_v1_prefix = settings.API_V1_PREFIX.rstrip("/")

    exempt_exact_paths = {
        "/",
        "/health",
        f"{api_v1_prefix}/health-check",
        f"{api_v1_prefix}/status",
    }

    if path in exempt_exact_paths:
        return True

    tags_prefix = f"{api_v1_prefix}/tags"
    if path == tags_prefix or path.startswith(f"{tags_prefix}/"):
        return True

    return False


async def require_api_key_middleware(request: Request, call_next):
    """
    Middleware global para exigir X-API-Key en todos los endpoints.

    Utiliza la dependencia require_api_key para validar la cabecera y
    retorna 403 si falta o es incorrecta.
    """
    path = request.url.path

    if request.method == "OPTIONS" or _is_api_key_exempt_path(path):
        return await call_next(request)

    try:
        await require_api_key(request.headers.get("X-API-Key"))
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    logger.debug(f"api_key.middleware.allowed path={path}")
    return await call_next(request)


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
        normalized_path = path
        if settings.API_V1_PREFIX and path.startswith(settings.API_V1_PREFIX):
            normalized_path = path[len(settings.API_V1_PREFIX) :]
            if not normalized_path.startswith("/"):
                normalized_path = f"/{normalized_path}"

        # Diccionario de rutas y sus patrones de caché relacionados
        # Cada entrada puede tener múltiples patrones para invalidar caché relacionado
        # Incluye el prefijo actual (fm:http:) y el legacy (fastapi-cache:)
        cache_invalidation_map = {
            # Usuarios
            "/users": ["fm:http:*users*", "fastapi-cache:*users*"],
            # Dominios - también invalida feature models del dominio
            "/domains": [
                "fm:http:*domains*",
                "fm:http:*feature-models*",
                "fastapi-cache:*domains*",
                "fastapi-cache:*feature-models*",
            ],
            # Feature Models - invalida todo el árbol de features relacionado
            "/feature-models": [
                "fm:http:*feature-models*",
                "fm:http:*features*",
                "fm:http:*feature-relations*",
                "fm:http:*feature-groups*",
                "fm:http:*constraints*",
                "fm:http:*configurations*",
                "fastapi-cache:*feature-models*",
                "fastapi-cache:*features*",
                "fastapi-cache:*feature-relations*",
                "fastapi-cache:*feature-groups*",
                "fastapi-cache:*constraints*",
                "fastapi-cache:*configurations*",
            ],
            # Features - invalida features, relations y groups
            "/features": [
                "fm:http:*features*",
                "fm:http:*feature-relations*",
                "fm:http:*feature-groups*",
                "fastapi-cache:*features*",
                "fastapi-cache:*feature-relations*",
                "fastapi-cache:*feature-groups*",
            ],
            # Feature Relations
            "/feature-relations": [
                "fm:http:*feature-relations*",
                "fm:http:*features*",
                "fastapi-cache:*feature-relations*",
                "fastapi-cache:*features*",
            ],
            # Feature Groups
            "/feature-groups": [
                "fm:http:*feature-groups*",
                "fm:http:*features*",
                "fastapi-cache:*feature-groups*",
                "fastapi-cache:*features*",
            ],
            # Constraints
            "/constraints": [
                "fm:http:*constraints*",
                "fm:http:*features*",
                "fastapi-cache:*constraints*",
                "fastapi-cache:*features*",
            ],
            # Configurations
            "/configurations": [
                "fm:http:*configurations*",
                "fastapi-cache:*configurations*",
            ],
            # Resources (recursos educativos)
            "/resources": [
                "fm:http:*resources*",
                "fastapi-cache:*resources*",
            ],
            # Tags - también invalida asociaciones de features con tags
            "/tags": [
                "fm:http:*tags*",
                "fm:http:*features*",
                "fastapi-cache:*tags*",
                "fastapi-cache:*features*",
            ],
            # App Settings
            "/app-settings": [
                "fm:http:*app-settings*",
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
                if normalized_path.startswith(route_prefix):
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
