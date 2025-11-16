# S3Service y S3StorageService - Guía de Uso

## Descripción

Las clases `S3Service` y `S3StorageService` han sido refactorizadas para soportar tanto operaciones síncronas como asíncronas con S3/Minio.

## Inicialización

Los servicios se inicializan automáticamente en el startup de FastAPI (ver `app/main.py`):

```python
@app.on_event("startup")
async def on_startup():
    await RedisService.init_async()
    RedisService.init_sync()
    await S3Service.init_async()  # Inicializa cliente asíncrono
    S3Service.init_sync()          # Inicializa cliente síncrono
```

## S3Service

Servicio de bajo nivel que gestiona las conexiones con S3/Minio.

### Métodos de clase

- `init_sync()`: Inicializa el cliente boto3 síncrono
- `init_async()`: Inicializa la sesión aioboto3 asíncrona
- `get_sync()`: Obtiene el cliente síncrono
- `get_async()`: Obtiene la sesión asíncrona

## S3StorageService

Servicio de alto nivel para operaciones de almacenamiento.

### Inicialización

```python
from app.services.s3_storage import S3StorageService
from app.core.config import settings

# Crear instancia del servicio
storage_service = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)
```

### Métodos Sincrónicos

#### 1. `save_audio_file(file: UploadFile) -> str`

Guarda un archivo de audio en S3.

```python
from fastapi import UploadFile

def upload_audio(file: UploadFile):
    storage_service = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)
    object_name = storage_service.save_audio_file(file)
    return {"object_name": object_name}
```

#### 2. `save_file(file: UploadFile, prefix: str = "") -> str`

Guarda un archivo genérico con un prefijo opcional.

```python
def upload_document(file: UploadFile):
    storage_service = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)
    object_name = storage_service.save_file(file, prefix="documents/")
    return {"object_name": object_name}
```

#### 3. `get_presigned_url_for_object(object_name: str, expires_in: int = 3600) -> str`

Genera una URL pre-firmada temporal.

```python
def get_download_url(object_name: str):
    storage_service = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)
    url = storage_service.get_presigned_url_for_object(
        object_name=object_name,
        expires_in=7200  # 2 horas
    )
    return {"download_url": url}
```

#### 4. `delete_file(object_name: str) -> bool`

Elimina un archivo de S3.

```python
def remove_file(object_name: str):
    storage_service = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)
    success = storage_service.delete_file(object_name)
    return {"deleted": success}
```

#### 5. `file_exists(object_name: str) -> bool`

Verifica si un archivo existe.

```python
def check_file(object_name: str):
    storage_service = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)
    exists = storage_service.file_exists(object_name)
    return {"exists": exists}
```

### Métodos Asíncronos

Todos los métodos síncronos tienen su equivalente asíncrono con el prefijo `a`.

#### 1. `asave_audio_file(file: UploadFile) -> str`

```python
@router.post("/upload-audio-async")
async def upload_audio_async(file: UploadFile):
    storage_service = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)
    object_name = await storage_service.asave_audio_file(file)
    return {"object_name": object_name}
```

#### 2. `asave_file(file: UploadFile, prefix: str = "") -> str`

```python
@router.post("/upload-async")
async def upload_file_async(file: UploadFile):
    storage_service = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)
    object_name = await storage_service.asave_file(file, prefix="uploads/")
    return {"object_name": object_name}
```

#### 3. `aget_presigned_url_for_object(object_name: str, expires_in: int = 3600) -> str`

```python
@router.get("/download-url-async/{object_name}")
async def get_download_url_async(object_name: str):
    storage_service = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)
    url = await storage_service.aget_presigned_url_for_object(object_name)
    return {"download_url": url}
```

#### 4. `adelete_file(object_name: str) -> bool`

```python
@router.delete("/file-async/{object_name}")
async def delete_file_async(object_name: str):
    storage_service = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)
    success = await storage_service.adelete_file(object_name)
    return {"deleted": success}
```

#### 5. `afile_exists(object_name: str) -> bool`

```python
@router.get("/check-file-async/{object_name}")
async def check_file_async(object_name: str):
    storage_service = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)
    exists = await storage_service.afile_exists(object_name)
    return {"exists": exists}
```

## Ejemplo Completo de Endpoint

### Endpoint Síncrono

```python
from fastapi import APIRouter, UploadFile, File
from app.services.s3_storage import S3StorageService
from app.core.config import settings

router = APIRouter()

@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    storage = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)

    # Guardar archivo
    object_name = storage.save_file(file, prefix="uploads/")

    # Generar URL de descarga
    download_url = storage.get_presigned_url_for_object(object_name)

    return {
        "object_name": object_name,
        "download_url": download_url
    }
```

### Endpoint Asíncrono

```python
from fastapi import APIRouter, UploadFile, File
from app.services.s3_storage import S3StorageService
from app.core.config import settings

router = APIRouter()

@router.post("/upload-async")
async def upload_file_async(file: UploadFile = File(...)):
    storage = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)

    # Guardar archivo
    object_name = await storage.asave_file(file, prefix="uploads/")

    # Generar URL de descarga
    download_url = await storage.aget_presigned_url_for_object(object_name)

    return {
        "object_name": object_name,
        "download_url": download_url
    }
```

## Manejo de Errores

Todos los métodos lanzan `HTTPException` en caso de error:

```python
from fastapi import HTTPException

try:
    storage = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)
    object_name = storage.save_file(file)
except HTTPException as e:
    # Manejo de error HTTP
    print(f"Error HTTP: {e.status_code} - {e.detail}")
except Exception as e:
    # Otros errores
    print(f"Error inesperado: {e}")
```

## Logging

El servicio incluye logging detallado para debugging:

- **DEBUG**: Operaciones detalladas, nombres de objetos generados
- **INFO**: Operaciones exitosas importantes
- **ERROR**: Errores durante operaciones
- **CRITICAL**: Fallos críticos en la inicialización

Para ver logs de debug, configura el nivel de log en tu aplicación:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Requisitos

Asegúrate de tener instaladas las dependencias necesarias:

```bash
pip install boto3 aioboto3
```

O con poetry:

```bash
poetry add boto3 aioboto3
```

## Configuración

Las siguientes variables de entorno deben estar configuradas (ver `app/core/config.py`):

- `S3_ENDPOINT`: Endpoint de Minio/S3
- `S3_ACCESS_KEY`: Access key
- `S3_SECRET_KEY`: Secret key
- `S3_BUCKET_NAME`: Nombre del bucket
- `S3_USE_SSL`: Si usar SSL (true/false)

## Notas Importantes

1. **Inicialización**: Los servicios deben inicializarse en el startup de FastAPI
2. **Prefijos**: Usa prefijos para organizar archivos por tipo o categoría
3. **URLs Pre-firmadas**: Por defecto expiran en 1 hora, ajusta según necesidad
4. **Async vs Sync**: Usa métodos async en endpoints async para mejor rendimiento
5. **Logging**: Todos los métodos incluyen logging detallado para debugging
