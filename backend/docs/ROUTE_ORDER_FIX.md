# 🔧 Fix: Orden de Rutas en FastAPI

## 🐛 Problema Encontrado

**Error**:

```json
{
  "code": 422,
  "description": "Field 'path.version_id': Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `l` at 1"
}
```

**URL que falló**:

```
GET /api/v1/feature-models/{model_id}/versions/latest/statistics
```

## 🔍 Causa Raíz

En FastAPI, **el orden de declaración de rutas importa**. Las rutas se evalúan **en el orden en que se definen**.

### ❌ Orden Incorrecto (Antes)

```python
# Esta ruta se define PRIMERO
@router.get("/{model_id}/versions/{version_id}/statistics")
async def get_feature_model_statistics(
    version_id: uuid.UUID  # ← Intenta parsear "latest" como UUID
):
    ...

# Esta ruta se define DESPUÉS
@router.get("/{model_id}/versions/latest/statistics")
async def get_latest_feature_model_statistics():
    ...
```

**Problema**: Cuando llega una petición a `/versions/latest/statistics`:

1. FastAPI evalúa la primera ruta `/{version_id}/statistics`
2. Intenta convertir "latest" a UUID
3. Falla con error 422 ❌
4. Nunca llega a evaluar la segunda ruta

### ✅ Orden Correcto (Después)

```python
# Rutas ESPECÍFICAS primero
@router.get("/{model_id}/versions/latest/statistics")
async def get_latest_feature_model_statistics():
    ...

# Rutas con PARÁMETROS VARIABLES después
@router.get("/{model_id}/versions/{version_id}/statistics")
async def get_feature_model_statistics(
    version_id: uuid.UUID
):
    ...
```

**Solución**: Cuando llega una petición a `/versions/latest/statistics`:

1. FastAPI evalúa la primera ruta `/latest/statistics`
2. ¡Coincide exactamente! ✅
3. Ejecuta la función correcta

## 📋 Regla General de FastAPI

### Orden de Prioridad (de mayor a menor)

1. **Rutas literales exactas** (más específicas)

   ```python
   @router.get("/users/me")  # ← Se evalúa PRIMERO
   ```

2. **Rutas con parámetros path**

   ```python
   @router.get("/users/{user_id}")  # ← Se evalúa DESPUÉS
   ```

3. **Rutas con comodines**
   ```python
   @router.get("/users/{path:path}")  # ← Se evalúa AL FINAL
   ```

### ✅ Ejemplo Correcto

```python
# 1. Rutas específicas primero
@router.get("/users/me")
@router.get("/users/admin")
@router.get("/users/latest")

# 2. Rutas con parámetros después
@router.get("/users/{user_id}")

# 3. Rutas catch-all al final
@router.get("/users/{path:path}")
```

### ❌ Ejemplo Incorrecto

```python
# ❌ MALO: Parámetro variable primero
@router.get("/users/{user_id}")

# Estas rutas NUNCA se ejecutarán porque {user_id} las captura
@router.get("/users/me")
@router.get("/users/admin")
@router.get("/users/latest")
```

## 🔧 Solución Aplicada

### Archivo: `feature_model_statistics.py`

**Antes**:

```python
@router.get("/{model_id}/versions/{version_id}/statistics")
async def get_feature_model_statistics(...):
    ...

@router.get("/{model_id}/versions/latest/statistics")
async def get_latest_feature_model_statistics(...):
    ...
```

**Después**:

```python
# ============================================================================
# IMPORTANTE: Las rutas más específicas (/latest/) deben ir ANTES que las
# rutas con parámetros variables (/{version_id}/) para evitar conflictos
# ============================================================================

@router.get("/{model_id}/versions/latest/statistics")
async def get_latest_feature_model_statistics(...):
    ...

@router.get("/{model_id}/versions/{version_id}/statistics")
async def get_feature_model_statistics(...):
    ...
```

## ✅ Verificación

### Probar el endpoint `/latest/`

```bash
# Debería funcionar ahora ✅
curl -X GET "http://localhost:8000/api/v1/feature-models/{model_id}/versions/latest/statistics" \
  -H "Authorization: Bearer TOKEN"
```

**Respuesta esperada**:

```json
{
  "total_features": 45,
  "mandatory_features": 32,
  "optional_features": 13,
  ...
}
```

### Probar el endpoint con UUID

```bash
# También debería funcionar ✅
curl -X GET "http://localhost:8000/api/v1/feature-models/{model_id}/versions/{version_id}/statistics" \
  -H "Authorization: Bearer TOKEN"
```

## 📝 Otros Endpoints Afectados

Revisar si hay patrones similares en otros archivos:

### ✅ Ya corregido en `feature_model_complete.py`

```python
# Correcto: /latest/ antes de /{version_id}/
@router.get("/{model_id}/versions/latest/complete")
@router.get("/{model_id}/versions/{version_id}/complete")
```

## 💡 Lecciones Aprendidas

1. **Siempre declarar rutas específicas antes que genéricas**
2. **Comentar el orden cuando sea crítico**
3. **Probar rutas especiales (`/latest/`, `/me/`, etc.) temprano**
4. **FastAPI no avisa de este problema en tiempo de desarrollo**

## 🎓 Documentación Oficial

De la [documentación de FastAPI](https://fastapi.tiangolo.com/tutorial/path-params/#order-matters):

> "When creating path operations, you can find situations where you have a fixed path.
>
> For example: `/users/me`
>
> You also have a path `/users/{user_id}` to get data about a specific user by user ID.
>
> Because path operations are evaluated in order, you need to make sure that the path for `/users/me` is declared before the one for `/users/{user_id}`"

## ✅ Checklist de Revisión

- [x] Identificar rutas con parámetros variables
- [x] Identificar rutas literales específicas
- [x] Reordenar: específicas primero, variables después
- [x] Agregar comentarios explicativos
- [x] Probar ambos endpoints
- [x] Documentar en guía de desarrollo

---

¡Problema resuelto! 🎉
