# endpoints for Root and Utils

from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache

from pydantic.networks import EmailStr

from app import enums
from app.models import Message, AllEnumsResponse
from app.services import format_enum_for_frontend, SettingsService
from app.api.deps import get_settings_service
from app.core.config import settings
from app.api.deps import get_current_active_superuser
from app.utils import generate_test_email, send_email

router = APIRouter(prefix="/utils", tags=["utils"])


# ===========================================================================
#           --- THIS ROUTER HAS ALL ITS OPERATIONS ASYNC ---
# ===========================================================================


# ===========================================================================
#  Endpoint raíz de bienvenida.
# ===========================================================================

@router.get("/")
def read_root():
    """ """
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


# ===========================================================================
# Endpoint Health Check
# ===========================================================================

@router.get("/health-check/")
async def health_check() -> bool:
    return True


# ===========================================================================
# Endpoint para probar el envío de correos electrónicos.
# ===========================================================================

@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")



# ===========================================================================
# Endpoint para probar el servicio de variables dinámicas del sistema.
# ===========================================================================

@router.get("/test/setting/")
async def get_example_with_dynamic_setting(
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
        Endpoint para probar el servicio de variables dinámicas configurables.
        Usamos el servicio para obtener un ajuste dinámico
    """
    
    items_per_page = await settings_service.aget("ITEMS_PER_PAGE", default=25)
    maintenance_mode = await settings_service.aget("MAINTENANCE_MODE", default=False)
    
    if maintenance_mode:
        return {"message": "El sistema está en modo mantenimiento."}

    return {"message": f"Mostrando {items_per_page} items por página."}



# ===========================================================================
# Endpoint para obtener los roles del sistema.
# ===========================================================================
@router.get(
    "/roles/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=list[str],
)
def get_roles() -> list[str]:
    """
    Retrieve the roles of the system.
    """
    from app.enums import UserRole 
    return [role.value for role in UserRole]


# ===========================================================================
#           --- Endpoint para obtener los enums del sistema ---
# ===========================================================================
    
@router.get(
    "/options/",
    response_model=AllEnumsResponse,
    summary="Obtener todas las opciones (enums) para los selectores del frontend"
)
@cache(expire=86400)
def read_enums():
    """
    Proporciona una lista consolidada de todos los valores de enumeración
    utilizados en la aplicación.

    Esto es útil para poblar dinámicamente los menús desplegables,
    filtros y otros componentes en el frontend sin tener que codificar
    estos valores.
    """
    return {
        "userRoles": format_enum_for_frontend(enums.UserRole),
        "resourceType": format_enum_for_frontend(enums.ResourceType),
        "resourceStatus": format_enum_for_frontend(enums.ResourceStatus),
        "licenseType": format_enum_for_frontend(enums.LicenseType),
        "featureType": format_enum_for_frontend(enums.FeatureType),
        "featureGroupType": format_enum_for_frontend(enums.FeatureGroupType),
        "featureRelationType": format_enum_for_frontend(enums.FeatureRelationType),
    }

# ===========================================================================
#           --- Endpoint para limpiar la CACHÉ del sistema ---
# ===========================================================================
     
@router.post("/clear-cache/")
async def clear_cache():
    from app.services.redis import RedisService
    from fastapi_cache import FastAPICache

    redis = RedisService.get_async()
    if redis:
        await redis.flushdb()
    FastAPICache.clear()
    return {"detail": "Cache cleared"}
