import sentry_sdk

from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware

# --- imports de la APP ---
from app.admin import setup_admin
from app.utils import custom_generate_unique_id
from app.core.config import settings
from app.api.v1.router import api_router as api_router_v1
from app.services import RedisService, S3Service

if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

# ========================================================================
#                 --- INSTANCIA DEL PROJECTO ---
# ========================================================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)


# ========================================================================
#           --- INICIALIZACIÓN DE SERVICIOS (CACHÉ Y STORAGES) ---
# ========================================================================
@app.on_event("startup")
async def on_startup():
    await RedisService.init_async()
    RedisService.init_sync()
    await S3Service.init_async()
    S3Service.init_sync()


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
app.include_router(api_router_v1, prefix=settings.API_V1_STR)


# ========================================================================
#             --- PANEL DE ADMINISTRACIÓN INICIALIZADO ---
# ========================================================================
setup_admin(app)
