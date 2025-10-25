import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)


# --- INICIALIZACIÓN DE CACHÉ ---
@app.on_event("startup")
async def startup_event():
    """
    Inicializa la conexión a Redis para el cacheo al iniciar la app.
    """
    print("Conectando a Redis para el cacheo...")
    try:
        redis = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        # Verifica la conexión
        await redis.ping()
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        print("Conexión a Redis establecida y FastAPICache inicializado.")
    except Exception as e:
        print(f"ERROR: No se pudo conectar a Redis. La caché estará deshabilitada. Error: {e}")


# Import exceptions to register global exception handlers
import app.exceptions as _exceptions

# Register exception handlers defined in app.exceptions
app.add_exception_handler(_exceptions.RequestValidationError, _exceptions.validation_exception_handler)
app.add_exception_handler(_exceptions.HTTPException, _exceptions.http_exception_handler)
app.add_exception_handler(Exception, _exceptions.generic_exception_handler)


# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app.include_router(api_router, prefix=settings.API_V1_STR)
