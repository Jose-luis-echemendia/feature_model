# Ejemplo de Dependency para S3StorageService

## Uso con Dependency Injection de FastAPI

Puedes crear dependencias reutilizables para inyectar `S3StorageService` en tus endpoints:

```python
# app/api/deps.py

from typing import Annotated
from fastapi import Depends
from app.services.s3_storage import S3StorageService
from app.core.config import settings


def get_s3_storage() -> S3StorageService:
    """
    Dependencia para obtener una instancia de S3StorageService.
    """
    return S3StorageService(bucket_name=settings.S3_BUCKET_NAME)


# Type alias para usar en endpoints
S3StorageDep = Annotated[S3StorageService, Depends(get_s3_storage)]
```

## Uso en Endpoints

### Endpoint Síncrono

```python
from fastapi import APIRouter, UploadFile, File
from app.api.deps import S3StorageDep

router = APIRouter()


@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    storage: S3StorageDep = None
):
    """Sube un archivo a S3 (síncrono)."""
    object_name = storage.save_file(file, prefix="uploads/")
    url = storage.get_presigned_url_for_object(object_name)

    return {
        "object_name": object_name,
        "download_url": url
    }


@router.get("/download/{object_name}")
def get_download_url(
    object_name: str,
    storage: S3StorageDep = None
):
    """Obtiene URL de descarga para un archivo."""
    url = storage.get_presigned_url_for_object(object_name, expires_in=7200)
    return {"download_url": url}


@router.delete("/files/{object_name}")
def delete_file(
    object_name: str,
    storage: S3StorageDep = None
):
    """Elimina un archivo de S3."""
    success = storage.delete_file(object_name)
    return {"deleted": success}
```

### Endpoint Asíncrono

```python
from fastapi import APIRouter, UploadFile, File
from app.api.deps import S3StorageDep

router = APIRouter()


@router.post("/upload-async")
async def upload_file_async(
    file: UploadFile = File(...),
    storage: S3StorageDep = None
):
    """Sube un archivo a S3 (asíncrono)."""
    object_name = await storage.asave_file(file, prefix="uploads/")
    url = await storage.aget_presigned_url_for_object(object_name)

    return {
        "object_name": object_name,
        "download_url": url
    }


@router.get("/download-async/{object_name}")
async def get_download_url_async(
    object_name: str,
    storage: S3StorageDep = None
):
    """Obtiene URL de descarga para un archivo (async)."""
    url = await storage.aget_presigned_url_for_object(object_name, expires_in=7200)
    return {"download_url": url}


@router.delete("/files-async/{object_name}")
async def delete_file_async(
    object_name: str,
    storage: S3StorageDep = None
):
    """Elimina un archivo de S3 (async)."""
    success = await storage.adelete_file(object_name)
    return {"deleted": success}
```

## Ejemplo Completo: CRUD de Archivos

```python
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.api.deps import S3StorageDep, CurrentUser
from app.models.user import User

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: CurrentUser = None,
    storage: S3StorageDep = None
):
    """
    Sube un archivo y registra en base de datos.
    """
    # Verificar tipo de archivo
    allowed_types = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido: {file.content_type}"
        )

    # Guardar en S3
    object_name = await storage.asave_file(
        file,
        prefix=f"users/{current_user.id}/"
    )

    # Aquí guardarías en la base de datos
    # file_record = crud.create_file(
    #     session=session,
    #     owner_id=current_user.id,
    #     object_name=object_name,
    #     filename=file.filename,
    #     content_type=file.content_type
    # )

    return {
        "object_name": object_name,
        "filename": file.filename,
        "content_type": file.content_type
    }


@router.get("/{object_name}/download")
async def download_file(
    object_name: str,
    storage: S3StorageDep = None
):
    """
    Genera URL de descarga temporal para un archivo.
    """
    # Verificar que el archivo existe
    exists = await storage.afile_exists(object_name)
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado"
        )

    # Generar URL temporal (válida por 15 minutos)
    url = await storage.aget_presigned_url_for_object(
        object_name,
        expires_in=900
    )

    return {"download_url": url}


@router.delete("/{object_name}")
async def delete_file(
    object_name: str,
    current_user: CurrentUser = None,
    storage: S3StorageDep = None
):
    """
    Elimina un archivo (con verificación de permisos).
    """
    # Verificar que el archivo existe
    exists = await storage.afile_exists(object_name)
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado"
        )

    # Verificar permisos (ejemplo)
    if not object_name.startswith(f"users/{current_user.id}/"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este archivo"
        )

    # Eliminar de S3
    await storage.adelete_file(object_name)

    # Aquí eliminarías de la base de datos
    # crud.delete_file(session=session, object_name=object_name)

    return {"message": "Archivo eliminado exitosamente"}


@router.head("/{object_name}")
async def check_file_exists(
    object_name: str,
    storage: S3StorageDep = None
):
    """
    Verifica si un archivo existe sin descargarlo.
    """
    exists = await storage.afile_exists(object_name)

    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado"
        )

    return {"exists": True}
```

## Múltiples Buckets

Si necesitas trabajar con múltiples buckets, puedes crear dependencias específicas:

```python
# app/api/deps.py

def get_uploads_storage() -> S3StorageService:
    """Bucket para archivos subidos por usuarios."""
    return S3StorageService(bucket_name=settings.S3_UPLOADS_BUCKET)


def get_exports_storage() -> S3StorageService:
    """Bucket para exportaciones y reportes."""
    return S3StorageService(bucket_name=settings.S3_EXPORTS_BUCKET)


def get_backups_storage() -> S3StorageService:
    """Bucket para backups."""
    return S3StorageService(bucket_name=settings.S3_BACKUPS_BUCKET)


# Type aliases
UploadsStorageDep = Annotated[S3StorageService, Depends(get_uploads_storage)]
ExportsStorageDep = Annotated[S3StorageService, Depends(get_exports_storage)]
BackupsStorageDep = Annotated[S3StorageService, Depends(get_backups_storage)]
```

Uso:

```python
@router.post("/export")
async def export_data(
    exports_storage: ExportsStorageDep = None,
    backups_storage: BackupsStorageDep = None
):
    """Exporta datos a múltiples buckets."""

    # Guardar en bucket de exports
    export_file = await create_export()
    export_name = await exports_storage.asave_file(export_file, prefix="exports/")

    # Guardar backup
    backup_name = await backups_storage.asave_file(export_file, prefix="backups/")

    return {
        "export_url": await exports_storage.aget_presigned_url_for_object(export_name),
        "backup_url": await backups_storage.aget_presigned_url_for_object(backup_name)
    }
```

## Testing con Dependencias

Para testing, puedes sobrescribir las dependencias:

```python
# tests/conftest.py

from fastapi.testclient import TestClient
from app.api.deps import get_s3_storage
from app.services.s3_storage import S3StorageService


class MockS3Storage(S3StorageService):
    """Mock para testing sin conectar a S3 real."""

    async def asave_file(self, file, prefix=""):
        return f"mock-{file.filename}"

    async def afile_exists(self, object_name):
        return True

    async def adelete_file(self, object_name):
        return True


@pytest.fixture
def client():
    app.dependency_overrides[get_s3_storage] = lambda: MockS3Storage(bucket_name="test")
    yield TestClient(app)
    app.dependency_overrides.clear()
```

## Ventajas de usar Dependencies

1. **Reutilización**: Define una vez, usa en todos los endpoints
2. **Testing**: Fácil de mockear para tests
3. **Flexibilidad**: Cambia la implementación sin tocar los endpoints
4. **Múltiples buckets**: Gestiona diferentes buckets fácilmente
5. **Type hints**: Mejor autocompletado en el IDE
