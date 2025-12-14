import uuid
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import re

from app.models.common import ErrorDetail, ErrorResponse

_ERROR_CODE_MAP = {
    422: 1001,
    400: 1002,
    401: 1003,
    403: 1004,
    404: 1005,
    409: 1006,
    500: 5000,
}


def _extract_object_from_request(request: Request) -> str:
    """Try to build an object string like 'client.get' from the request path and method.

    Strategy: split the path, ignore common prefixes like 'api' and version segments 'v1',
    take the first meaningful segment as resource and use the HTTP method as operation.
    """
    path = request.url.path or ""
    parts = [p for p in path.strip("/").split("/") if p]
    # remove common prefixes
    parts = [p for p in parts if not re.fullmatch(r"v\d+", p) and p.lower() != "api"]
    resource = parts[0] if parts else "unknown"
    operation = request.method.lower() if request.method else "unknown"
    # normalize resource to singular-ish by removing trailing s if present
    if resource.endswith("s") and len(resource) > 1:
        resource = resource[:-1]
    return f"{resource}.{operation}"


# --- Manejador para errores de validación (HTTP 422) ---
# Se activa cuando los datos de entrada (body, query params) no son válidos
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = str(uuid.uuid4())

    # Formateamos los errores de validación para que sean más legibles
    error_descriptions = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_descriptions.append(f"Field '{field}': {message}")

    error_detail = ErrorDetail(
        http_code=422,
        error_code=_ERROR_CODE_MAP.get(422, 1001),
        category="request_validation",
        description=", ".join(error_descriptions),
        request_id=request_id,
    )

    response_content = ErrorResponse(
        object=_extract_object_from_request(request),
        code=422,
        status="error",
        message=error_detail,
    )

    return JSONResponse(status_code=422, content=response_content.model_dump())


# --- Manejador para errores HTTP genéricos (los que lanzas con raise HTTPException) ---
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = str(uuid.uuid4())

    http_code = exc.status_code
    error_detail = ErrorDetail(
        http_code=http_code,
        error_code=_ERROR_CODE_MAP.get(http_code, 1000 + http_code),
        category="http_error",
        description=str(exc.detail),
        request_id=request_id,
    )

    response_content = ErrorResponse(
        object=_extract_object_from_request(request),
        code=http_code,
        status="error",
        message=error_detail,
    )

    return JSONResponse(status_code=http_code, content=response_content.model_dump())


# --- Manejador para errores inesperados del servidor (HTTP 500) ---
async def generic_exception_handler(request: Request, exc: Exception):
    # ¡Importante! En producción, deberías loggear el error `exc` completo
    # para poder depurarlo. Por ejemplo: logging.error(f"Unhandled error: {exc}")
    request_id = str(uuid.uuid4())

    error_detail = ErrorDetail(
        http_code=500,
        error_code=_ERROR_CODE_MAP.get(500, 5000),
        category="internal_server_error",
        description="An unexpected internal server error occurred.",
        request_id=request_id,
    )

    response_content = ErrorResponse(
        object=_extract_object_from_request(request),
        code=500,
        status="error",
        message=error_detail,
    )

    return JSONResponse(status_code=500, content=response_content.model_dump())


# ========================================================================
# CUSTOM EXCEPTIONS
# ========================================================================


class NotFoundException(HTTPException):
    """Excepción para recursos no encontrados (404)."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)


class BusinessLogicException(HTTPException):
    """Excepción para errores de lógica de negocio (400)."""

    def __init__(self, detail: str = "Business logic error"):
        super().__init__(status_code=400, detail=detail)


class UnprocessableEntityException(HTTPException):
    """Excepción para entidades no procesables (422)."""

    def __init__(self, detail: str = "Unprocessable entity"):
        super().__init__(status_code=422, detail=detail)


class ConflictException(HTTPException):
    """Excepción para conflictos de recursos (409)."""

    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(status_code=409, detail=detail)


class ForbiddenException(HTTPException):
    """Excepción para acceso prohibido (403)."""

    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(status_code=403, detail=detail)


class UnauthorizedException(HTTPException):
    """Excepción para acceso no autorizado (401)."""

    def __init__(self, detail: str = "Unauthorized access"):
        super().__init__(status_code=401, detail=detail)
