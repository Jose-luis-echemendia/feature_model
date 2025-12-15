# Excepciones de Dominio - Documentación para Desarrolladores

Esta documentación describe todas las excepciones personalizadas disponibles para el módulo de **Dominios** en el sistema de Feature Models.

## 📋 Tabla de Contenidos

1. [Excepciones de Entidad de Dominio](#excepciones-de-entidad-de-dominio)
2. [Excepciones de Operaciones](#excepciones-de-operaciones)
3. [Excepciones de Estado](#excepciones-de-estado)
4. [Excepciones de Validación](#excepciones-de-validación)
5. [Mejores Prácticas](#mejores-prácticas)
6. [Ejemplos de Uso](#ejemplos-de-uso)

---

## Excepciones de Entidad de Dominio

### 1. DomainNotFoundException

**Código HTTP:** `404 Not Found`

**Cuándo usar:**

- El dominio solicitado no existe en la base de datos
- El dominio fue eliminado previamente
- El UUID proporcionado no corresponde a ningún dominio

**Ejemplo:**

```python
from app.exceptions import DomainNotFoundException

domain = await domain_repo.get(domain_id)
if not domain:
    raise DomainNotFoundException(domain_id=str(domain_id))
```

**Mensaje de error:**

```
Domain with ID '123e4567-e89b-12d3-a456-426614174000' not found
```

---

### 2. DomainAlreadyExistsException

**Código HTTP:** `409 Conflict`

**Cuándo usar:**

- Intentando crear un dominio con un nombre que ya existe
- Los nombres de dominio deben ser únicos en el sistema

**Ejemplo:**

```python
from app.exceptions import DomainAlreadyExistsException

try:
    domain = await domain_repo.create(domain_in)
except ValueError as e:
    if "already exists" in str(e).lower():
        raise DomainAlreadyExistsException(
            domain_name=domain_in.name,
            existing_domain_id="abc-123"  # Opcional
        )
```

**Mensajes de error:**

```
# Sin ID existente
Domain with name 'E-Commerce' already exists

# Con ID existente
Domain with name 'E-Commerce' already exists (ID: abc-123)
```

---

### 3. InvalidDomainNameException

**Código HTTP:** `422 Unprocessable Entity`

**Cuándo usar:**

- Nombre de dominio vacío o demasiado corto
- Nombre contiene caracteres inválidos
- Nombre no cumple con las reglas de validación

**Ejemplo:**

```python
from app.exceptions import InvalidDomainNameException

if not domain_name or len(domain_name) < 3:
    raise InvalidDomainNameException(
        domain_name=domain_name,
        reason="Domain name must be at least 3 characters long"
    )
```

**Mensaje de error:**

```
Invalid domain name '': Domain name cannot be empty
```

---

## Excepciones de Operaciones

### 4. DomainHasDependenciesException

**Código HTTP:** `400 Bad Request`

**Cuándo usar:**

- Intentando eliminar un dominio que tiene feature models asociados
- El dominio tiene otros recursos que deben eliminarse primero

**Ejemplo:**

```python
from app.exceptions import DomainHasDependenciesException

if hasattr(domain, "feature_models") and domain.feature_models:
    raise DomainHasDependenciesException(
        domain_id=str(domain.id),
        domain_name=domain.name,
        dependency_count=len(domain.feature_models),
        dependency_type="feature models"
    )
```

**Mensaje de error:**

```
Cannot delete domain 'E-Commerce' (ID: 123). It has 5 associated feature models.
Delete them first or use deactivate instead.
```

---

### 5. DomainUpdateConflictException

**Código HTTP:** `409 Conflict`

**Cuándo usar:**

- Actualizando el nombre del dominio a uno que ya existe
- La actualización viola restricciones de unicidad

**Ejemplo:**

```python
from app.exceptions import DomainUpdateConflictException

try:
    updated_domain = await domain_repo.update(db_domain, domain_in)
except ValueError as e:
    if "already exists" in str(e).lower():
        raise DomainUpdateConflictException(
            domain_id=str(domain_id),
            conflicting_field="name",
            conflicting_value=domain_in.name
        )
```

**Mensaje de error:**

```
Cannot update domain 123: name 'E-Commerce' already exists
```

---

## Excepciones de Estado

### 6. DomainAlreadyActiveException

**Código HTTP:** `400 Bad Request`

**Cuándo usar:**

- Intentando activar un dominio que ya está activo
- Operación redundante

**Ejemplo:**

```python
from app.exceptions import DomainAlreadyActiveException

if domain.is_active:
    raise DomainAlreadyActiveException(
        domain_id=str(domain_id),
        domain_name=domain.name
    )
```

**Mensaje de error:**

```
Domain 'E-Commerce' (ID: 123) is already active
```

---

### 7. DomainAlreadyInactiveException

**Código HTTP:** `400 Bad Request`

**Cuándo usar:**

- Intentando desactivar un dominio que ya está inactivo
- Operación redundante

**Ejemplo:**

```python
from app.exceptions import DomainAlreadyInactiveException

if not domain.is_active:
    raise DomainAlreadyInactiveException(
        domain_id=str(domain_id),
        domain_name=domain.name
    )
```

**Mensaje de error:**

```
Domain 'E-Commerce' (ID: 123) is already inactive
```

---

### 8. DomainInactiveException

**Código HTTP:** `400 Bad Request`

**Cuándo usar:**

- Intentando crear feature models en un dominio inactivo
- Intentando operaciones que requieren un dominio activo

**Ejemplo:**

```python
from app.exceptions import DomainInactiveException

if not domain.is_active:
    raise DomainInactiveException(
        domain_id=str(domain_id),
        domain_name=domain.name,
        operation="create feature model"
    )
```

**Mensaje de error:**

```
Cannot create feature model: Domain 'E-Commerce' (ID: 123) is inactive.
Activate it first.
```

---

## Excepciones de Validación

### 9. InvalidDomainDescriptionException

**Código HTTP:** `422 Unprocessable Entity`

**Cuándo usar:**

- Descripción del dominio es demasiado larga
- Descripción contiene contenido inválido

**Ejemplo:**

```python
from app.exceptions import InvalidDomainDescriptionException

if len(description) > 500:
    raise InvalidDomainDescriptionException(
        reason="Description exceeds maximum length of 500 characters"
    )
```

**Mensaje de error:**

```
Invalid domain description: Description exceeds maximum length of 500 characters
```

---

### 10. DomainAccessDeniedException

**Código HTTP:** `400 Bad Request`

**Cuándo usar:**

- Usuario no tiene permisos para acceder al dominio
- Dominio restringido a ciertos roles

**Ejemplo:**

```python
from app.exceptions import DomainAccessDeniedException

if user.role not in [UserRole.ADMIN, UserRole.DEVELOPER]:
    raise DomainAccessDeniedException(
        domain_id=str(domain_id),
        domain_name=domain.name,
        user_role=user.role.value
    )
```

**Mensaje de error:**

```
Access denied to domain 'E-Commerce' (ID: 123).
Role 'VIEWER' does not have sufficient permissions.
```

---

## Mejores Prácticas

### 1. **Usar excepciones específicas en lugar de HTTPException genérica**

❌ **Evitar:**

```python
if not domain:
    raise HTTPException(status_code=404, detail="Domain not found")
```

✅ **Preferir:**

```python
if not domain:
    raise DomainNotFoundException(domain_id=str(domain_id))
```

### 2. **Proporcionar contexto detallado**

Las excepciones personalizadas incluyen automáticamente información relevante:

- IDs de recursos
- Nombres de entidades
- Conteos de dependencias
- Valores conflictivos

### 3. **Verificar estado antes de operaciones**

```python
# Antes de activar, verificar que no esté activo
if domain.is_active:
    raise DomainAlreadyActiveException(
        domain_id=str(domain_id),
        domain_name=domain.name
    )
```

### 4. **Convertir ValueError a excepciones específicas**

```python
try:
    domain = await domain_repo.create(domain_in)
except ValueError as e:
    if "already exists" in str(e).lower():
        raise DomainAlreadyExistsException(
            domain_name=domain_in.name
        )
    raise  # Re-lanzar si es otro error
```

---

## Ejemplos de Uso

### Endpoint: Crear Dominio

```python
@router.post("/", response_model=DomainPublic)
async def create_domain(
    domain_repo: AsyncDomainRepoDep,
    domain_in: DomainCreate,
) -> DomainPublic:
    """Create new domain."""
    try:
        domain = await domain_repo.create(domain_in)
        return DomainPublic.model_validate(domain)
    except ValueError as e:
        if "already exists" in str(e).lower():
            raise DomainAlreadyExistsException(
                domain_name=domain_in.name
            )
        raise HTTPException(status_code=400, detail=str(e))
```

### Endpoint: Eliminar Dominio

```python
@router.delete("/{domain_id}/", response_model=Message)
async def delete_domain(
    domain_id: uuid.UUID,
    domain_repo: AsyncDomainRepoDep,
) -> Message:
    """Permanently delete a domain."""
    domain = await domain_repo.get(domain_id)
    if not domain:
        raise DomainNotFoundException(domain_id=str(domain_id))

    if hasattr(domain, "feature_models") and domain.feature_models:
        raise DomainHasDependenciesException(
            domain_id=str(domain_id),
            domain_name=domain.name,
            dependency_count=len(domain.feature_models)
        )

    await domain_repo.delete(domain)
    return Message(message="Domain deleted successfully")
```

### Endpoint: Activar Dominio

```python
@router.patch("/{domain_id}/activate/", response_model=DomainPublic)
async def activate_domain(
    domain_id: uuid.UUID,
    domain_repo: AsyncDomainRepoDep,
) -> DomainPublic:
    """Activate a domain."""
    domain = await domain_repo.get(domain_id)
    if not domain:
        raise DomainNotFoundException(domain_id=str(domain_id))

    if domain.is_active:
        raise DomainAlreadyActiveException(
            domain_id=str(domain_id),
            domain_name=domain.name
        )

    return await domain_repo.activate(domain)
```

---

## Formato de Respuesta de Error

Todas las excepciones generan respuestas JSON con el siguiente formato:

```json
{
  "detail": "Domain with ID '123e4567-e89b-12d3-a456-426614174000' not found"
}
```

Para validación de FastAPI, el formato puede incluir más detalles:

```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Testing

Para probar estas excepciones en tests unitarios:

```python
import pytest
from app.exceptions import DomainNotFoundException

def test_domain_not_found():
    with pytest.raises(DomainNotFoundException) as exc_info:
        raise DomainNotFoundException(domain_id="123")

    assert exc_info.value.status_code == 404
    assert "123" in exc_info.value.detail
```

---

## Mantenimiento

Para agregar nuevas excepciones de dominio:

1. Añadir la clase en `app/exceptions/domain_exceptions.py`
2. Importar y exportar en `app/exceptions/__init__.py`
3. Agregar tests en `app/tests/exceptions/test_domain_exceptions.py`
4. Actualizar esta documentación

---

## Referencias

- **Código fuente:** `app/exceptions/domain_exceptions.py`
- **Tests:** `app/tests/exceptions/test_domain_exceptions.py`
- **Endpoints:** `app/api/v1/endpoints/domain.py`
- **Excepciones base:** `app/exceptions/exceptions.py`
