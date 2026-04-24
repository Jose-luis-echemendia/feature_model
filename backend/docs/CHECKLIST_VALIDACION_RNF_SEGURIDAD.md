# Checklist de validación técnica de RnF de Seguridad

**Proyecto:** Feature Model  
**Fecha de revisión:** 2026-04-23  
**Alcance revisado:** implementación backend + despliegue productivo (docker/traefik) + pruebas existentes.

---

## Resumen ejecutivo

| RnF                                          | Estado actual            | Observación clave                                                                                                             |
| -------------------------------------------- | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| RnF#1 JWT autenticación                      | **Cumple (base)**        | Hay emisión y validación de JWT para sesiones.                                                                                |
| RnF#2 Ciclo de vida JWT                      | **Parcial**              | Hay emisión/refresh/logout con revocación de refresh token; no se evidencia revocación de access token.                       |
| RnF#3 Eliminación lógica                     | **Parcial**              | Existe `is_active`/`deleted_at` y endpoints activate/deactivate, pero convive con borrado físico en repositorios.             |
| RnF#4 UUID PK exclusivo                      | **Parcial alto**         | Modelo base usa UUID en PK; excepción en `app_settings` (PK `key: str`).                                                      |
| RnF#5 Autorización CRUD                      | **Parcial**              | Existen dependencias por rol, pero hay rutas sin dependencia explícita de autenticación/autorización.                         |
| RnF#6 HTTPS/TLS                              | **Parcial alto**         | Traefik en producción configura TLS y redirect; falta evidencia de controles adicionales (p. ej. HSTS) y pruebas automáticas. |
| RnF#7 Configuración por variables de entorno | **Cumple (con alertas)** | Config centralizada en `Settings`; se detectan credenciales hardcodeadas en seeding/docs de desarrollo.                       |

---

## RnF#1 — Autenticación JWT

**Objetivo:** autenticación de sesiones usando JWT.

### Evidencia de implementación

- Emisión de access/refresh token: [backend/app/core/security.py](backend/app/core/security.py)
  - `create_access_token()`
  - `create_refresh_token()`
- Login con emisión de JWT: [backend/app/api/v1/routes/login.py](backend/app/api/v1/routes/login.py)
  - `login_access_token()`
- Validación de JWT para usuario actual: [backend/app/api/deps.py](backend/app/api/deps.py)
  - `get_current_user()`

### Checklist de validación

- [x] El login emite `access_token` firmado.
- [x] El token incluye `sub` (identidad de usuario).
- [x] El backend valida firma y expiración del token en cada request autenticada.
- [x] Se bloquea acceso con token inválido/expirado (`401`).
- [x] Se bloquea acceso para usuario inactivo (`403`).

### Evidencia de pruebas

- [backend/app/tests/core/test_security.py](backend/app/tests/core/test_security.py)
- [backend/app/tests/api/test_deps_auth.py](backend/app/tests/api/test_deps_auth.py)

---

## RnF#2 — Ciclo de vida JWT (emisión, renovación, invalidación)

**Objetivo:** ciclo completo con expiración y revocación explícita.

### Evidencia de implementación

- Refresh con rotación y blacklist por `jti`: [backend/app/api/v1/routes/login.py](backend/app/api/v1/routes/login.py)
  - `_refresh_blacklist_key()`
  - `_blacklist_refresh_token()`
  - `refresh_access_token()`
- Logout con revocación de refresh token: [backend/app/api/v1/routes/login.py](backend/app/api/v1/routes/login.py)
  - `logout()`
- Expiración configurada por entorno: [backend/app/core/config.py](backend/app/core/config.py)
  - `ACCESS_TOKEN_EXPIRE_MINUTES`
  - `REFRESH_TOKEN_EXPIRE_MINUTES`

### Checklist de validación

- [x] Existe emisión de `access_token` y `refresh_token`.
- [x] Existe endpoint de renovación (`/login/refresh-token`).
- [x] Existe endpoint de invalidación explícita (`/login/logout`).
- [x] Se verifica expiración de refresh token.
- [x] Se usa blacklist para revocar refresh tokens.
- [ ] Se evidencia revocación de `access_token` antes de su expiración (no encontrada).
- [ ] Se evidencian pruebas automáticas de `refresh` y `logout` (no encontradas en tests actuales).

### Resultado de revisión

**Parcial**: cumple para refresh/logout, pendiente cobertura para invalidación temprana de access token y pruebas específicas.

---

## RnF#3 — Eliminación lógica (activo/inactivo)

**Objetivo:** preservar integridad referencial con soft delete.

### Evidencia de implementación

- Base de entidades con `is_active` y `deleted_at`: [backend/app/models/common.py](backend/app/models/common.py)
  - `BaseTable`
- Repositorios con `activate()`/`deactivate()`:
  - [backend/app/repositories/domain.py](backend/app/repositories/domain.py)
  - [backend/app/repositories/feature_model.py](backend/app/repositories/feature_model.py)
  - [backend/app/repositories/constraint.py](backend/app/repositories/constraint.py)
- Ejemplo explícito de soft delete en constraint: [backend/app/repositories/constraint.py](backend/app/repositories/constraint.py)

### Hallazgo crítico

- Existe borrado físico (`session.delete`) en al menos: [backend/app/repositories/domain.py](backend/app/repositories/domain.py) `delete()`.

### Checklist de validación

- [x] Las entidades de dominio incluyen `is_active`.
- [x] Existen operaciones de activación/desactivación.
- [x] Existen consultas que filtran por `is_active` en listados.
- [ ] Todos los deletes del sistema usan solo eliminación lógica.
- [ ] Existe política única documentada para cuándo hard delete es permitido.

### Resultado de revisión

**Parcial**: patrón soft-delete existe, pero no es consistente en todo el sistema.

---

## RnF#4 — UUID exclusivo como PK

**Objetivo:** llaves primarias UUID, no numéricas.

### Evidencia de implementación

- PK UUID por defecto en base de tablas: [backend/app/models/common.py](backend/app/models/common.py) (`id: uuid.UUID`).
- Migración inicial con UUID en tablas principales: [backend/app/alembic/versions/d8b152111a20_initial_schema.py](backend/app/alembic/versions/d8b152111a20_initial_schema.py).

### Excepción encontrada

- [backend/app/models/app_setting.py](backend/app/models/app_setting.py): PK `key: str`.
- [backend/app/alembic/versions/d8b152111a20_initial_schema.py](backend/app/alembic/versions/d8b152111a20_initial_schema.py): tabla `app_settings` con PK string.

### Checklist de validación

- [x] Tablas de negocio usan UUID como PK.
- [x] Endpoints usan UUID en parámetros/path para entidades principales.
- [ ] 100% de tablas usan UUID como PK (hay excepción `app_settings`).
- [ ] Está documentada formalmente la excepción (si aplica por diseño).

### Resultado de revisión

**Parcial alto**: cumplimiento amplio, con excepción puntual.

---

## RnF#5 — Solo usuarios autorizados pueden crear/modificar/eliminar

**Objetivo:** control de acceso por autenticación + autorización.

### Evidencia de implementación

- Dependencias de autorización por rol: [backend/app/api/deps.py](backend/app/api/deps.py)
  - `get_admin_user()`, `get_verified_user()`, `role_required()`
- Rutas con control explícito (ejemplo): [backend/app/api/v1/routes/domain.py](backend/app/api/v1/routes/domain.py)
  - `Depends(get_verified_user)` / `Depends(get_admin_user)`

### Hallazgos de brecha

- Rutas sin dependencia explícita en archivo de configuración: [backend/app/api/v1/routes/configuration.py](backend/app/api/v1/routes/configuration.py).
- En usuarios, `read_users_by_role` no declara dependencia de autenticación/autorización en decorator: [backend/app/api/v1/routes/user.py](backend/app/api/v1/routes/user.py).

### Checklist de validación

- [x] Existen mecanismos de authz por rol reutilizables.
- [x] Existen rutas críticas con protección por rol.
- [ ] Todas las rutas CRUD tienen dependencia explícita de auth/authz.
- [ ] Hay pruebas de autorización por endpoint y rol para todas las rutas de escritura.
- [ ] Hay pruebas de denegación (`403`) por rol insuficiente en todos los CRUD.

### Resultado de revisión

**Parcial**: arquitectura de autorización existe, pero cobertura no homogénea.

---

## RnF#6 — Comunicación segura TLS/SSL (HTTPS)

**Objetivo:** acceso por HTTPS para proteger confidencialidad e integridad.

### Evidencia de implementación

- Routers HTTPS/TLS y redirección HTTP→HTTPS en despliegue: [docker-compose.prod.yml](docker-compose.prod.yml).
  - `traefik.http.routers.*-https.tls=true`
  - `*.tls.certresolver=le`
  - middleware `https-redirect`

### Checklist de validación

- [x] El despliegue productivo define routers HTTPS.
- [x] Se configura redirección de HTTP a HTTPS.
- [x] El frontend productivo usa URL de API con `https://`.
- [ ] Se validan cabeceras de seguridad TLS/HSTS en runtime (pendiente verificar).
- [ ] Existen pruebas automáticas de seguridad de transporte (pendiente).

### Resultado de revisión

**Parcial alto**: base sólida en infraestructura, falta validación automática/hardening verificable.

---

## RnF#7 — Configuración variable por entorno (sin hardcode)

**Objetivo:** inyección de configuración vía variables de entorno.

### Evidencia de implementación

- Configuración centralizada en `Settings`: [backend/app/core/config.py](backend/app/core/config.py).
- Validaciones de seguridad para secretos en `Settings`: [backend/app/core/config.py](backend/app/core/config.py).
- Composición de entorno productivo por variables: [docker-compose.prod.yml](docker-compose.prod.yml).
- Pruebas de configuración: [backend/app/tests/core/test_config.py](backend/app/tests/core/test_config.py).

### Alertas detectadas

- Credenciales de desarrollo en seeding/documentación (ej.: `admin123`) en:
  - [backend/app/seed/data_users.py](backend/app/seed/data_users.py)
  - [backend/app/seed/README.md](backend/app/seed/README.md)

### Checklist de validación

- [x] Variables sensibles se leen desde `Settings`/env.
- [x] Despliegue productivo inyecta variables vía `.env`/compose.
- [x] Hay validadores para secretos inseguros en producción.
- [ ] No existen credenciales hardcodeadas en el repositorio (hay ejemplos de desarrollo).
- [ ] Existe escaneo automático de secretos en CI (pendiente evidenciar).

### Resultado de revisión

**Cumple con alertas**: patrón principal correcto; requiere saneamiento de hardcodes de desarrollo y controles CI.

---

## Criterios de aceptación global sugeridos

Marcar el bloque como aprobado solo si se cumple todo:

- [ ] RnF#1 aprobado
- [ ] RnF#2 aprobado
- [ ] RnF#3 aprobado
- [ ] RnF#4 aprobado
- [ ] RnF#5 aprobado
- [ ] RnF#6 aprobado
- [ ] RnF#7 aprobado

**Estado final de seguridad RnF:**

- [ ] APROBADO
- [ ] APROBADO CON OBSERVACIONES
- [ ] RECHAZADO

---

## Recomendación priorizada (cierre de brechas)

1. **Alta prioridad:** cerrar authz faltante en rutas sin dependencia de seguridad.
2. **Alta prioridad:** definir política única de eliminación (soft delete por defecto).
3. **Media-alta:** completar ciclo JWT con estrategia de revocación de access token (si el riesgo lo exige).
4. **Media:** decidir y documentar excepción UUID de `app_settings` o migrarla.
5. **Media:** agregar pruebas automáticas de HTTPS/HSTS y escaneo de secretos en CI.
