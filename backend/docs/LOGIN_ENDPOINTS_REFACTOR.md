# Refactorización de Endpoints de Login

**Fecha**: 3 de diciembre de 2025  
**Archivos modificados**:

- `backend/app/api/v1/endpoints/login.py`
- `backend/app/api/deps.py`

## 📋 Resumen de Cambios

Se ha realizado una refactorización completa del módulo de autenticación (`login.py`) con los siguientes objetivos:

1. ✅ **Documentación completa** de todos los endpoints con ejemplos
2. ✅ **Conversión a asíncrono** de todas las operaciones
3. ✅ **Patrón repositorio** para todas las operaciones CRUD
4. ✅ **Mejora de códigos de estado HTTP** con constantes de FastAPI

---

## 🔄 Endpoints Refactorizados

### 1. `POST /login/access-token/`

**Descripción**: Login de usuario con email y contraseña

**Cambios**:

- ✅ Convertido a `async def`
- ✅ Usa `AsyncUserRepoDep` en lugar de `SessionDep` + `crud`
- ✅ Usa `user_repo.authenticate()` (patrón repositorio)
- ✅ Códigos de estado con `status.HTTP_400_BAD_REQUEST`
- ✅ Documentación completa con ejemplos de request/response

**Antes**:

```python
def login_access_token(*, session: SessionDep, login_data: LoginRequest) -> Token:
    user = crud.authenticate(session=session, email=..., password=...)
    if not user:
        raise HTTPException(status_code=400, detail="...")
```

**Después**:

```python
async def login_access_token(*, user_repo: AsyncUserRepoDep, login_data: LoginRequest) -> Token:
    user = await user_repo.authenticate(email=..., password=...)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="...")
```

---

### 2. `POST /login/test-token/`

**Descripción**: Verificar validez del token de acceso

**Cambios**:

- ✅ Convertido a `async def`
- ✅ Usa `AsyncCurrentUser` en lugar de `CurrentUser`
- ✅ Documentación completa con explicación del flujo de autenticación

**Antes**:

```python
def test_token(current_user: CurrentUser) -> Any:
    """Test access token"""
    return current_user
```

**Después**:

```python
async def test_token(current_user: AsyncCurrentUser) -> Any:
    """
    ## Verificar validez del token de acceso

    Endpoint para probar si el token JWT actual es válido...
    """
    return current_user
```

---

### 3. `POST /password-recovery/{email}/`

**Descripción**: Solicitar recuperación de contraseña

**Cambios**:

- ✅ Convertido a `async def`
- ✅ Usa `user_repo.get_by_email()` en lugar de `crud.get_user_by_email()`
- ✅ Código de estado `status.HTTP_404_NOT_FOUND`
- ✅ Documentación con flujo completo de recuperación

**Antes**:

```python
def recover_password(email: str, session: SessionDep) -> Message:
    user = crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="...")
```

**Después**:

```python
async def recover_password(email: str, user_repo: AsyncUserRepoDep) -> Message:
    user = await user_repo.get_by_email(email=email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="...")
```

---

### 4. `POST /reset-password/`

**Descripción**: Restablecer contraseña con token

**Cambios**:

- ✅ Convertido a `async def`
- ✅ Usa `user_repo.get_by_email()` y `user_repo.session`
- ✅ Códigos de estado semánticos (`HTTP_400_BAD_REQUEST`, `HTTP_404_NOT_FOUND`)
- ✅ Documentación con flujo completo (4 pasos)

**Antes**:

```python
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    user = crud.get_user_by_email(session=session, email=email)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
```

**Después**:

```python
async def reset_password(user_repo: AsyncUserRepoDep, body: NewPassword) -> Message:
    user = await user_repo.get_by_email(email=email)
    user.hashed_password = hashed_password
    user_repo.session.add(user)
    await user_repo.session.commit()
```

---

### 5. `POST /password-recovery-html-content/{email}/`

**Descripción**: Obtener contenido HTML del email de recuperación (Solo Superusuarios)

**Cambios**:

- ✅ Convertido a `async def`
- ✅ Usa `user_repo.get_by_email()`
- ✅ Documentación completa explicando su propósito (debugging/testing)

---

## 🆕 Nuevas Dependencias Asíncronas

Se agregaron al archivo `deps.py`:

### `get_current_user()`

Versión asíncrona de `get_current_user()` que usa el repositorio asíncrono.

```python
async def get_current_user(user_repo: AsyncUserRepoDep, token: TokenDep) -> User:
    # Decodificación JWT + validaciones
    user = await user_repo.get(user_id=token_data.sub)
    # Validaciones de usuario activo
    return user
```

### `get_optional_user()`

Versión asíncrona de `get_optional_user()` para endpoints públicos.

```python
async def get_optional_user(user_repo: AsyncUserRepoDep, token: OptionalTokenDep = None) -> User | None:
    if not token:
        return None
    try:
        return await get_current_user(user_repo=user_repo, token=token)
    except HTTPException:
        return None
```

### Nuevos Type Hints

```python
AsyncCurrentUser = Annotated[User, Depends(get_current_user)]
AsyncOptionalUser = Annotated[User | None, Depends(get_optional_user)]
```

---

## 📚 Mejoras en Documentación

Cada endpoint ahora incluye:

1. **Título descriptivo** en formato Markdown (`##`)
2. **Descripción funcional** de lo que hace
3. **Sección de Parámetros** con tipos y descripciones
4. **Sección de Retorno** explicando la respuesta
5. **Sección de Errores** con todos los códigos de estado posibles
6. **Notas adicionales** cuando aplica (seguridad, flujos, etc.)
7. **Ejemplo de uso** con request y response en formato código

### Ejemplo de documentación:

````python
"""
## Solicitar recuperación de contraseña

Envía un email con un token de recuperación de contraseña al usuario.

### Parámetros
- **email**: Email del usuario que solicita recuperar su contraseña

### Retorna
Mensaje de confirmación indicando que se envió el email

### Errores
- **404**: No existe un usuario con ese email

### Notas
- El token de recuperación tiene una validez limitada
- El email contiene un enlace para restablecer la contraseña
- Por seguridad, siempre devuelve 200 incluso si el email no existe

### Ejemplo de uso
```python
# Request
POST /api/v1/password-recovery/user@example.com/

# Response
{
    "message": "Password recovery email sent"
}
````

"""

````

---

## 🎯 Beneficios

### 1. **Performance**
- ✅ Operaciones asíncronas = mejor concurrencia
- ✅ No bloqueantes = más requests por segundo
- ✅ Mejor uso de recursos del servidor

### 2. **Mantenibilidad**
- ✅ Patrón repositorio = lógica de BD centralizada
- ✅ Fácil cambiar implementación sin tocar endpoints
- ✅ Mejor testing (mock del repositorio)

### 3. **Documentación**
- ✅ OpenAPI/Swagger mejorado automáticamente
- ✅ Desarrolladores entienden endpoints sin leer código
- ✅ Ejemplos claros para consumidores de la API

### 4. **Código Limpio**
- ✅ Códigos HTTP semánticos (`status.HTTP_*`)
- ✅ Sin dependencia directa de `crud`
- ✅ Mejor separación de responsabilidades

---

## 🧪 Testing

Para probar los endpoints refactorizados:

```bash
# 1. Login
curl -X POST http://localhost/api/v1/login/access-token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "changethis"}'

# 2. Test token
curl -X POST http://localhost/api/v1/login/test-token/ \
  -H "Authorization: Bearer <tu_token>"

# 3. Recuperar contraseña
curl -X POST http://localhost/api/v1/password-recovery/admin@example.com/

# 4. Reset contraseña
curl -X POST http://localhost/api/v1/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{"token": "<token_del_email>", "new_password": "newpass123"}'
````

---

## 📝 Notas Importantes

1. **Compatibilidad**: Los endpoints mantienen exactamente la misma interfaz externa (rutas, parámetros, respuestas)
2. **Sin Breaking Changes**: Clientes existentes funcionarán sin modificaciones
3. **Repositorio**: Ya existían `UserRepository` y `UserRepository` con los métodos necesarios
4. **Dependencias**: Se agregaron versiones asíncronas de las dependencias de autenticación

---

## 🔜 Próximos Pasos

Endpoints similares que se beneficiarían de esta refactorización:

1. ✅ Login (COMPLETADO)
2. 🔲 Users (`/users/*`)
3. 🔲 Domains (`/domains/*`)
4. 🔲 Feature Models (`/feature-models/*`)
5. 🔲 Features (`/features/*`)
6. 🔲 Relations (`/feature-relations/*`)
7. 🔲 Constraints (`/constraints/*`)
8. 🔲 Configurations (`/configurations/*`)

**Patrón a seguir**:

1. Crear repositorio asíncrono si no existe
2. Convertir endpoints a `async def`
3. Reemplazar `SessionDep` + operaciones directas por `{Resource}RepoDep`
4. Agregar documentación completa
5. Usar códigos de estado semánticos
