"""Middleware para rate limiting usando Redis."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, Request, status
from app.core.redis import redis_client

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter usando Redis para almacenar contadores.

    Implementa un algoritmo de sliding window para contar requests.
    """

    def __init__(
        self,
        max_requests: int,
        window_seconds: int,
        key_prefix: str = "rate_limit",
    ):
        """
        Inicializa el rate limiter.

        Args:
            max_requests: Número máximo de requests permitidos en la ventana
            window_seconds: Duración de la ventana en segundos
            key_prefix: Prefijo para las keys en Redis
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.key_prefix = key_prefix

    def _get_client_identifier(self, request: Request) -> str:
        """
        Obtiene un identificador único del cliente.

        Prioridad:
        1. IP real del cliente (si está detrás de proxy)
        2. IP del cliente directo
        3. "unknown" como fallback
        """
        # Intentar obtener IP real si está detrás de proxy
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # X-Forwarded-For puede contener múltiples IPs
            return forwarded.split(",")[0].strip()

        # IP directa del cliente
        if request.client:
            return request.client.host

        return "unknown"

    async def check_rate_limit(
        self,
        request: Request,
        identifier: Optional[str] = None,
    ) -> bool:
        """
        Verifica si el cliente ha excedido el rate limit.

        Args:
            request: Request de FastAPI
            identifier: Identificador personalizado (opcional)

        Returns:
            True si está dentro del límite, False si lo excedió

        Raises:
            HTTPException: Si se excede el rate limit
        """
        redis = redis_client

        # Obtener identificador del cliente
        client_id = identifier or self._get_client_identifier(request)

        # Crear key única para este cliente y endpoint
        endpoint = request.url.path
        key = f"{self.key_prefix}:{endpoint}:{client_id}"

        # Obtener timestamp actual
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=self.window_seconds)

        try:
            # Usar Redis sorted set para implementar sliding window
            # Score = timestamp, valor = request ID único

            # 1. Limpiar requests antiguos fuera de la ventana
            await redis.zremrangebyscore(key, "-inf", window_start.timestamp())

            # 2. Contar requests en la ventana actual
            current_count = await redis.zcard(key)

            # 3. Verificar si excede el límite
            if current_count >= self.max_requests:
                # Obtener el timestamp del request más antiguo
                oldest = await redis.zrange(key, 0, 0, withscores=True)
                if oldest:
                    oldest_timestamp = oldest[0][1]
                    retry_after = int(
                        oldest_timestamp + self.window_seconds - now.timestamp()
                    )
                    retry_after = max(retry_after, 1)  # Mínimo 1 segundo
                else:
                    retry_after = self.window_seconds

                logger.warning(
                    f"Rate limit excedido para {client_id} en {endpoint}: "
                    f"{current_count}/{self.max_requests} requests en {self.window_seconds}s"
                )

                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                    headers={"Retry-After": str(retry_after)},
                )

            # 4. Agregar el request actual
            request_id = f"{now.timestamp()}:{id(request)}"
            await redis.zadd(key, {request_id: now.timestamp()})

            # 5. Establecer expiración de la key (limpieza automática)
            await redis.expire(key, self.window_seconds + 60)

            # Agregar headers informativos
            remaining = self.max_requests - current_count - 1

            logger.debug(
                f"Rate limit para {client_id} en {endpoint}: "
                f"{current_count + 1}/{self.max_requests} "
                f"(quedan {remaining} requests)"
            )

            return True
        except HTTPException:
            raise
        except Exception as exc:
            # Fail-open: si Redis falla, no bloquear tráfico legítimo
            logger.warning(
                "Rate limiting degradado por error de Redis; permitiendo request",
                extra={"endpoint": endpoint, "client_id": client_id, "error": str(exc)},
            )
            return True


# Instancias predefinidas para diferentes niveles de protección

# Rate limiter estricto para endpoints críticos (login, registro)
strict_rate_limiter = RateLimiter(
    max_requests=5,  # 5 requests
    window_seconds=60,  # por minuto
    key_prefix="rate_limit:strict",
)

# Rate limiter moderado para endpoints sensibles (MFA, password reset)
moderate_rate_limiter = RateLimiter(
    max_requests=10,  # 10 requests
    window_seconds=60,  # por minuto
    key_prefix="rate_limit:moderate",
)

# Rate limiter ligero para endpoints generales
light_rate_limiter = RateLimiter(
    max_requests=30,  # 30 requests
    window_seconds=60,  # por minuto
    key_prefix="rate_limit:light",
)


# Dependency para usar en rutas de FastAPI


async def apply_strict_rate_limit(request: Request):
    """Dependency para aplicar rate limiting estricto."""
    await strict_rate_limiter.check_rate_limit(request)


async def apply_moderate_rate_limit(request: Request):
    """Dependency para aplicar rate limiting moderado."""
    await moderate_rate_limiter.check_rate_limit(request)


async def apply_light_rate_limit(request: Request):
    """Dependency para aplicar rate limiting ligero."""
    await light_rate_limiter.check_rate_limit(request)
