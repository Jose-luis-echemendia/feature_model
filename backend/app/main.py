import sentry_sdk

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from starlette.middleware.cors import CORSMiddleware

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

# --- imports de la APP ---
from app.admin import setup_admin
from app.utils import custom_generate_unique_id
from app.core.config import settings
from app.api.v1.router import api_router as api_router_v1
from app.middlewares import setup_middlewares
from app.schemas import WelcomeResponse

# --- imports core services ---
from app.core.cache import setup_cache, teardown_cache
from app.core.config import settings
from app.core.db import check_database, a_engine
from app.core.logging import get_logger, setup_logging
from app.core.s3 import minio_client
from app.core.redis import setup_redis, teardown_redis, check_redis

if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)


log = get_logger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Lifespan — startup y shutdown de todos los servicios
# ─────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # ── STARTUP ───────────────────────────────────────────────────────────────
    setup_logging()
    log.info("app.starting", env=settings.ENVIRONMENT, version=settings.APP_VERSION)

    # 1. Base de datos
    db_ok = await check_database()
    if not db_ok:
        raise RuntimeError("No se puede conectar a PostgreSQL. Abortando arranque.")
    log.info("app.db.ready")

    # 2. Redis
    await setup_redis()
    log.info("app.redis.ready")

    # 3. Caché Redis (fastapi-cache2 + CacheService)
    await setup_cache()
    log.info("app.cache.ready")

    # 4. MinIO — verificar conexión y crear buckets si no existen
    minio_ok = await minio_client.health_check()
    if not minio_ok:
        raise RuntimeError("No se puede conectar a MinIO. Abortando arranque.")
    await minio_client.ensure_buckets()
    log.info("app.minio.ready")

    log.info("app.started")
    yield

    # ── SHUTDOWN ──────────────────────────────────────────────────────────────
    log.info("app.stopping")

    await teardown_cache()
    log.info("app.cache.closed")

    await a_engine.dispose()
    log.info("app.db.closed")

    log.info("app.stopped")


# ========================================================================
#                 --- INSTANCIA DEL PROJECTO ---
# ========================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)


# ========================================================================
#              --- Servir documentación interna ---
# ========================================================================
app.mount(
    "/internal-docs",
    StaticFiles(directory="internal_docs/site", html=True),
    name="internal-docs",
)

# ========================================================================
#              --- CONFIGURACIÓN DE MIDDLEWARES ---
# ========================================================================
setup_middlewares(app)


# ========================================================================
#                   --- MANEJADOR DE ERRORES ---
# ========================================================================

# Import exceptions to register global exception handlers
import app.exceptions as _exceptions

# Register exception handlers defined in app.exceptions
app.add_exception_handler(
    _exceptions.RequestValidationError, _exceptions.validation_exception_handler
)
app.add_exception_handler(_exceptions.HTTPException, _exceptions.http_exception_handler)
app.add_exception_handler(Exception, _exceptions.generic_exception_handler)


# ========================================================================
#                   --- CORS ---
# ========================================================================


# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ========================================================================
#             --- MÉTODOS DE LA API ( ROUTERS ) ---
# ========================================================================
app.include_router(api_router_v1, prefix=settings.API_V1_PREFIX)


# ========================================================================
#             --- PANEL DE ADMINISTRACIÓN INICIALIZADO ---
# ========================================================================
setup_admin(app)


# ========================================================================
#             --- Welcome Response y Healt Check (ROOT) ---
# ========================================================================


@app.get("/", response_model=WelcomeResponse)
def read_root():

    log.info("app.root_accessed", message="Endpoint raíz accedido")

    return WelcomeResponse(
        message=f"Welcome to {settings.APP_NAME}",
        project=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )


@app.get("/health", tags=["health"], include_in_schema=False)
async def health() -> dict:
    from app.core.cache import cache_service

    log.info("app.health_check", message="Health check endpoint accedido")

    return {
        "status": "ok",
        "env": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "services": {
            "database": await check_database(),
            "redis": await check_redis(),
            "cache": await cache_service.ping(),
            "minio": await minio_client.health_check(),
        },
    }
