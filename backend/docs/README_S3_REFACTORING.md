# S3Service y S3StorageService - Refactorización Completa ✅

## 🎯 Resumen

Las clases `S3Service` y `S3StorageService` han sido completamente refactorizadas para soportar **operaciones síncronas y asíncronas**, siguiendo el mismo patrón utilizado en `RedisService` y `SettingsService`.

## 📋 Archivos Modificados

### 1. Código Principal

- ✅ `app/services/s3_storage.py` - Refactorización completa
- ✅ `app/main.py` - Actualización de inicialización
- ✅ `pyproject.toml` - Agregada dependencia `aioboto3`

### 2. Documentación Creada

- ✅ `docs/s3_service_usage.md` - Guía completa de uso
- ✅ `docs/s3_service_changes.md` - Resumen de cambios
- ✅ `docs/s3_dependency_examples.md` - Ejemplos con FastAPI dependencies

### 3. Scripts de Utilidad

- ✅ `scripts/verify_s3_services.py` - Script de verificación

## 🚀 Instalación

### 1. Instalar la nueva dependencia

```bash
# Con uv (recomendado)
uv pip install aioboto3

# Con poetry
poetry add aioboto3

# Con pip
pip install aioboto3
```

### 2. Verificar la instalación

```bash
# Ejecutar script de verificación
python scripts/verify_s3_services.py

# O hacerlo ejecutable
chmod +x scripts/verify_s3_services.py
./scripts/verify_s3_services.py
```

## 📚 Nuevas Características

### S3Service (Servicio de bajo nivel)

#### Antes:

```python
S3Service.init()              # Solo síncrono
client = S3Service.get_client()
```

#### Ahora:

```python
# Síncrono
S3Service.init_sync()
client = S3Service.get_sync()

# Asíncrono
await S3Service.init_async()
session = S3Service.get_async()
```

### S3StorageService (Servicio de alto nivel)

#### Constructor Simplificado:

```python
# ❌ ANTES
storage = S3StorageService(client=s3_client, bucket_name=bucket)

# ✅ AHORA
storage = S3StorageService(bucket_name=bucket)
```

#### Métodos Síncronos:

- ✅ `save_audio_file(file)` - Guarda archivos de audio
- ✅ `save_file(file, prefix="")` - Guarda cualquier archivo
- ✅ `get_presigned_url_for_object(object_name, expires_in=3600)` - URL temporal
- ✅ `delete_file(object_name)` - Elimina archivos ⭐ NUEVO
- ✅ `file_exists(object_name)` - Verifica existencia ⭐ NUEVO

#### Métodos Asíncronos (prefijo `a`):

- ✅ `asave_audio_file(file)`
- ✅ `asave_file(file, prefix="")`
- ✅ `aget_presigned_url_for_object(object_name, expires_in=3600)`
- ✅ `adelete_file(object_name)` ⭐ NUEVO
- ✅ `afile_exists(object_name)` ⭐ NUEVO

## 💡 Ejemplos Rápidos

### Ejemplo Síncrono

```python
from fastapi import APIRouter, UploadFile
from app.services.s3_storage import S3StorageService
from app.core.config import settings

router = APIRouter()

@router.post("/upload")
def upload(file: UploadFile):
    storage = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)

    # Guardar archivo
    object_name = storage.save_file(file, prefix="uploads/")

    # Obtener URL de descarga
    url = storage.get_presigned_url_for_object(object_name)

    return {"object_name": object_name, "url": url}
```

### Ejemplo Asíncrono

```python
from fastapi import APIRouter, UploadFile
from app.services.s3_storage import S3StorageService
from app.core.config import settings

router = APIRouter()

@router.post("/upload")
async def upload(file: UploadFile):
    storage = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)

    # Guardar archivo (async)
    object_name = await storage.asave_file(file, prefix="uploads/")

    # Obtener URL de descarga (async)
    url = await storage.aget_presigned_url_for_object(object_name)

    return {"object_name": object_name, "url": url}
```

### Con Dependency Injection

```python
# app/api/deps.py
from typing import Annotated
from fastapi import Depends
from app.services.s3_storage import S3StorageService
from app.core.config import settings

def get_s3_storage() -> S3StorageService:
    return S3StorageService(bucket_name=settings.S3_BUCKET_NAME)

S3StorageDep = Annotated[S3StorageService, Depends(get_s3_storage)]

# En tu endpoint
@router.post("/upload")
async def upload(file: UploadFile, storage: S3StorageDep):
    object_name = await storage.asave_file(file)
    return {"object_name": object_name}
```

## 🔧 Configuración

Asegúrate de tener estas variables de entorno configuradas:

```env
S3_ENDPOINT=localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=my-bucket
S3_USE_SSL=false
```

## ✅ Checklist de Migración

- [x] Refactorizar `S3Service` para sync/async
- [x] Refactorizar `S3StorageService` para sync/async
- [x] Agregar métodos `delete_file` y `file_exists`
- [x] Actualizar `main.py` con inicialización dual
- [x] Agregar dependencia `aioboto3` a `pyproject.toml`
- [x] Crear documentación completa
- [x] Crear script de verificación
- [ ] Instalar `aioboto3`: `uv pip install aioboto3`
- [ ] Ejecutar script de verificación: `python scripts/verify_s3_services.py`
- [ ] Verificar que la aplicación inicia correctamente
- [ ] (Opcional) Migrar código existente a métodos async

## 📖 Documentación Completa

Para más detalles, consulta:

1. **`docs/s3_service_usage.md`** - Guía completa de uso con ejemplos
2. **`docs/s3_service_changes.md`** - Resumen detallado de cambios
3. **`docs/s3_dependency_examples.md`** - Ejemplos con FastAPI dependencies

## 🧪 Testing

### Verificación Automática

```bash
python scripts/verify_s3_services.py
```

Este script verifica:

- ✅ Dependencias instaladas
- ✅ Configuración correcta
- ✅ Inicialización síncrona
- ✅ Inicialización asíncrona
- ✅ Métodos de `S3StorageService`

### Testing Manual

```python
# Test síncrono
from app.services.s3_storage import S3Service, S3StorageService
from app.core.config import settings

S3Service.init_sync()
storage = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)
exists = storage.file_exists("test-file.txt")
print(f"File exists: {exists}")

# Test asíncrono
import asyncio

async def test():
    await S3Service.init_async()
    storage = S3StorageService(bucket_name=settings.S3_BUCKET_NAME)
    exists = await storage.afile_exists("test-file.txt")
    print(f"File exists: {exists}")

asyncio.run(test())
```

## 🎉 Beneficios

1. **Consistencia**: Mismo patrón que `RedisService` y `SettingsService`
2. **Flexibilidad**: Elige entre sync/async según el contexto
3. **Rendimiento**: Endpoints async no bloquean el event loop
4. **Funcionalidad**: Nuevos métodos para eliminar y verificar archivos
5. **Organización**: Prefijos para organizar archivos por categoría
6. **Debugging**: Logging detallado en todas las operaciones
7. **Type Safety**: Mejores type hints y autocompletado

## ⚠️ Notas Importantes

1. **Breaking Change**: El constructor de `S3StorageService` cambió

   ```python
   # Viejo (no funcionará)
   storage = S3StorageService(client=s3_client, bucket_name=bucket)

   # Nuevo
   storage = S3StorageService(bucket_name=bucket)
   ```

2. **Inicialización**: Ambos servicios deben inicializarse en el startup:

   ```python
   @app.on_event("startup")
   async def on_startup():
       await S3Service.init_async()
       S3Service.init_sync()
   ```

3. **Async en Async**: Usa métodos async (`asave_file`, etc.) en endpoints async

4. **URLs Pre-firmadas**: Por defecto expiran en 1 hora, configurable con `expires_in`

## 🆘 Troubleshooting

### Error: "S3Service no ha sido inicializado"

- **Causa**: No se llamó a `init_sync()` o `init_async()` en el startup
- **Solución**: Verifica que `main.py` tenga la inicialización correcta

### Error: "No module named 'aioboto3'"

- **Causa**: Dependencia no instalada
- **Solución**: `uv pip install aioboto3`

### Error al conectar con Minio

- **Causa**: Configuración incorrecta o Minio no está corriendo
- **Solución**:
  1. Verifica las variables de entorno
  2. Verifica que Minio esté corriendo: `docker ps`
  3. Ejecuta el script de verificación

## 📞 Soporte

Si tienes problemas:

1. Ejecuta `python scripts/verify_s3_services.py` para diagnóstico
2. Revisa los logs de la aplicación (nivel DEBUG)
3. Consulta la documentación en `docs/`

---

**¡Los servicios S3 están listos para usar! 🎉**
