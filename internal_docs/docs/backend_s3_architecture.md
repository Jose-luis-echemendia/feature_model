# Arquitectura de S3Service y S3StorageService

## 📐 Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI App                              │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              app.on_event("startup")                    │    │
│  │                                                          │    │
│  │  await S3Service.init_async()  ──────────────────┐     │    │
│  │  S3Service.init_sync()         ────────────┐     │     │    │
│  └────────────────────────────────────────────│─────│─────┘    │
│                                                │     │           │
└────────────────────────────────────────────────│─────│───────────┘
                                                 ▼     ▼
┌─────────────────────────────────────────────────────────────────┐
│                         S3Service                                │
│                    (Servicio de bajo nivel)                      │
│                                                                  │
│  ┌──────────────────────────┐   ┌──────────────────────────┐   │
│  │    Cliente Síncrono      │   │    Sesión Asíncrona      │   │
│  │      (boto3.client)      │   │  (aioboto3.Session)      │   │
│  │                          │   │                          │   │
│  │  _sync_client: Redis     │   │  _async_session: Session │   │
│  │                          │   │                          │   │
│  │  + init_sync()           │   │  + init_async()          │   │
│  │  + get_sync()            │   │  + get_async()           │   │
│  │  + _ensure_bucket_       │   │  + _ensure_bucket_       │   │
│  │    exists_sync()         │   │    exists_async()        │   │
│  └──────────────────────────┘   └──────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                    │                           │
                    │                           │
                    ▼                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    S3StorageService                              │
│                   (Servicio de alto nivel)                       │
│                                                                  │
│  Constructor:                                                    │
│    __init__(bucket_name: str)                                   │
│      ├─ self.bucket_name = bucket_name                          │
│      ├─ self.sync_client = S3Service.get_sync()                 │
│      └─ self.async_session = S3Service.get_async()              │
│                                                                  │
│  ┌──────────────────────────┐   ┌──────────────────────────┐   │
│  │   Métodos Síncronos      │   │   Métodos Asíncronos     │   │
│  │                          │   │                          │   │
│  │  save_audio_file()       │   │  asave_audio_file()      │   │
│  │  save_file()             │   │  asave_file()            │   │
│  │  get_presigned_url_*()   │   │  aget_presigned_url_*()  │   │
│  │  delete_file()           │   │  adelete_file()          │   │
│  │  file_exists()           │   │  afile_exists()          │   │
│  │                          │   │                          │   │
│  │  Usa: self.sync_client   │   │  Usa: self.async_session │   │
│  └──────────────────────────┘   └──────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                    │                           │
                    │                           │
                    ▼                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Minio / S3 Storage                          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                    Buckets                              │    │
│  │                                                          │    │
│  │  📦 my-bucket/                                          │    │
│  │     ├─ uploads/                                         │    │
│  │     │   ├─ uuid1.jpg                                    │    │
│  │     │   └─ uuid2.pdf                                    │    │
│  │     ├─ audio/                                           │    │
│  │     │   └─ uuid3.mp3                                    │    │
│  │     └─ users/                                           │    │
│  │         └─ user123/                                     │    │
│  │             └─ uuid4.png                                │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Flujo de Datos

### Flujo Síncrono

```
┌─────────────┐      ┌──────────────┐      ┌────────────┐      ┌─────────┐
│   Endpoint  │─────▶│ S3Storage    │─────▶│ S3Service  │─────▶│  Minio  │
│  (sync)     │      │ Service      │      │ .get_sync()│      │   S3    │
└─────────────┘      │              │      └────────────┘      └─────────┘
                     │ save_file()  │            │
                     └──────────────┘            │
                            │                    │
                            │                    ▼
                            │            boto3.client
                            │            upload_fileobj()
                            │                    │
                            │                    │
                            ▼                    ▼
                    ┌──────────────────────────────┐
                    │   Archivo guardado en S3     │
                    │   Retorna: object_name       │
                    └──────────────────────────────┘
```

### Flujo Asíncrono

```
┌─────────────┐      ┌──────────────┐      ┌────────────┐      ┌─────────┐
│   Endpoint  │─────▶│ S3Storage    │─────▶│ S3Service  │─────▶│  Minio  │
│  (async)    │await │ Service      │await │ .get_async()│await │   S3    │
└─────────────┘      │              │      └────────────┘      └─────────┘
                     │ asave_file() │            │
                     └──────────────┘            │
                            │                    │
                            │                    ▼
                            │         aioboto3.Session
                            │         .client() context
                            │         await upload_fileobj()
                            │                    │
                            │                    │
                            ▼                    ▼
                    ┌──────────────────────────────┐
                    │   Archivo guardado en S3     │
                    │   Retorna: object_name       │
                    └──────────────────────────────┘
```

## 📊 Comparación: Antes vs Después

### Antes de la Refactorización

```python
# Inicialización (solo sync)
S3Service.init()
client = S3Service.get_client()

# Uso
storage = S3StorageService(
    client=client,  # ← Cliente como parámetro
    bucket_name=settings.S3_BUCKET_NAME
)

# Métodos disponibles (solo sync)
storage.save_audio_file(file)
storage.get_presigned_url_for_object(object_name)

# ❌ No disponible:
# - Métodos async
# - delete_file()
# - file_exists()
# - save_file() genérico
```

### Después de la Refactorización

```python
# Inicialización (sync + async)
S3Service.init_sync()
await S3Service.init_async()

# Uso (constructor simplificado)
storage = S3StorageService(
    bucket_name=settings.S3_BUCKET_NAME  # ← Solo bucket
)

# Métodos síncronos
storage.save_audio_file(file)
storage.save_file(file, prefix="uploads/")  # ✨ Nuevo
storage.get_presigned_url_for_object(object_name, expires_in=3600)
storage.delete_file(object_name)  # ✨ Nuevo
storage.file_exists(object_name)  # ✨ Nuevo

# Métodos asíncronos (todos nuevos)
await storage.asave_audio_file(file)
await storage.asave_file(file, prefix="uploads/")
await storage.aget_presigned_url_for_object(object_name)
await storage.adelete_file(object_name)
await storage.afile_exists(object_name)
```

## 🎯 Casos de Uso

### 1. Upload Simple (Síncrono)

```python
@router.post("/upload")
def upload(file: UploadFile):
    storage = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)
    object_name = storage.save_file(file)
    return {"object_name": object_name}
```

### 2. Upload con Organización (Asíncrono)

```python
@router.post("/users/{user_id}/avatar")
async def upload_avatar(user_id: int, file: UploadFile):
    storage = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)

    # Guardar en carpeta específica del usuario
    object_name = await storage.asave_file(
        file,
        prefix=f"users/{user_id}/avatars/"
    )

    return {"avatar_url": object_name}
```

### 3. Download con Verificación (Asíncrono)

```python
@router.get("/download/{object_name}")
async def download(object_name: str):
    storage = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)

    # Verificar que existe
    if not await storage.afile_exists(object_name):
        raise HTTPException(404, "File not found")

    # Generar URL temporal
    url = await storage.aget_presigned_url_for_object(
        object_name,
        expires_in=300  # 5 minutos
    )

    return {"download_url": url}
```

### 4. Delete con Validación (Asíncrono)

```python
@router.delete("/files/{object_name}")
async def delete(object_name: str, current_user: User):
    storage = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)

    # Verificar permisos
    if not object_name.startswith(f"users/{current_user.id}/"):
        raise HTTPException(403, "Forbidden")

    # Eliminar
    await storage.adelete_file(object_name)

    return {"message": "File deleted"}
```

## 🔌 Integración con FastAPI Dependencies

```python
# app/api/deps.py
from typing import Annotated
from fastapi import Depends
from app.services.s3_storage import S3StorageService
from app.core.config import settings

def get_s3_storage() -> S3StorageService:
    return S3StorageService(bucket_name=settings.S3_BUCKET_NAME)

S3StorageDep = Annotated[S3StorageService, Depends(get_s3_storage)]

# En endpoints
@router.post("/upload")
async def upload(file: UploadFile, storage: S3StorageDep):
    object_name = await storage.asave_file(file)
    return {"object_name": object_name}
```

## 🏗️ Patrón de Diseño

El patrón implementado sigue estos principios:

1. **Singleton Pattern**: `S3Service` mantiene instancias únicas de clientes
2. **Service Layer**: `S3StorageService` abstrae la lógica de negocio
3. **Dependency Injection**: Compatible con FastAPI dependencies
4. **Async/Await Pattern**: Soporte completo para operaciones asíncronas
5. **Factory Pattern**: Métodos `init_*()` actúan como factories

## 📈 Beneficios de la Arquitectura

1. **Separación de Responsabilidades**

   - `S3Service`: Gestión de conexiones
   - `S3StorageService`: Lógica de negocio

2. **Reutilización**

   - Una inicialización, múltiples instancias de storage
   - Diferentes buckets con la misma base

3. **Escalabilidad**

   - Fácil agregar nuevos métodos
   - Soporte para múltiples buckets

4. **Mantenibilidad**

   - Código organizado y predecible
   - Logging consistente

5. **Testing**
   - Fácil de mockear con dependencies
   - Separación clara entre sync/async

---

**Esta arquitectura proporciona una base sólida y escalable para el almacenamiento de archivos en tu aplicación FastAPI! 🚀**
