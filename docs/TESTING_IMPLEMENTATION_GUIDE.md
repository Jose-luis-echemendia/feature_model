# Guía de Implementación de Pruebas - Feature Model

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Bibliotecas Empleadas](#bibliotecas-empleadas)
3. [Estructura de Pruebas](#estructura-de-pruebas)
4. [Pruebas Unitarias](#pruebas-unitarias)
5. [Pruebas de Integración](#pruebas-de-integración)
6. [Aislamiento y Mocking](#aislamiento-y-mocking)

---

## Introducción

El proyecto **Feature Model** implementa una estrategia de pruebas multinivel que cubre:

- **Pruebas Unitarias**: Para excepciones, servicios y repositorios
- **Pruebas de Integración**: Para controladores (rutas API) y dependencias
- **Pruebas de Componentes**: Para partes específicas del sistema (ejemplo: Flamapy)

Este documento detalla la implementación técnica, propósito, proceso y mecanismos de aislamiento utilizados.

---

## Bibliotecas Empleadas

### 1. **pytest** (v7.4.3 - v8.0.0)

**Propósito**: Framework principal para todas las pruebas.

```toml
[dependency-groups]
dev = [
    "pytest<8.0.0,>=7.4.3",
]
```

**Características clave**:

- Fixtures reutilizables
- Parametrización de pruebas
- Plugins extensibles
- Integración con TestClient de FastAPI

**Uso en el proyecto**:

- Decoradores `@pytest.fixture` para configuración
- `@pytest.mark.parametrize` para pruebas parametrizadas
- `pytest.raises()` para verificación de excepciones

### 2. **FastAPI TestClient**

**Propósito**: Cliente HTTP para pruebas de integración de endpoints.

```python
from fastapi.testclient import TestClient
from app.main import app

with TestClient(app) as client:
    response = client.post("/api/v1/feature-models/", json=payload)
```

**Características**:

- Realiza peticiones HTTP sin levantar servidor externo
- Ejecuta lógica de middleware y autenticación
- Proporciona respuestas completas (headers, status, body)

### 3. **unittest.mock** (estándar de Python)

**Propósito**: Aislamiento de dependencias mediante mocks y patches.

```python
from unittest.mock import AsyncMock, Mock, patch

session = Mock()
session.execute = AsyncMock()
session.commit = AsyncMock()
```

**Características**:

- `Mock()`: Objetos simulados básicos
- `AsyncMock()`: Para funciones asincrónicas
- `patch()`: Reemplaza código durante pruebas
- `monkeypatch`: Fixture de pytest para modificar atributos

### 4. **SQLModel + SQLAlchemy**

**Propósito**: ORM para persistencia en pruebas de integración.

**Configuración en conftest.py**:

```python
from sqlmodel import Session, delete
from app.core.db import engine, init_db

@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(User)
        session.execute(statement)
        session.commit()
```

---

## Estructura de Pruebas

### Organización de Directorios

```
backend/app/tests/
├── __init__.py
├── conftest.py                  # Configuración global (fixtures, setup)
├── api/
│   ├── routes/                  # Pruebas de integración de endpoints
│   │   ├── test_feature_models.py
│   │   ├── test_domains.py
│   │   ├── test_users.py
│   │   └── ...
│   ├── test_deps_auth.py       # Pruebas de dependencias (autenticación)
│   └── fm_test_helpers.py      # Utilitarios para pruebas de FM
├── repositories/                # Pruebas unitarias de repositorios
│   ├── test_feature_model_repository.py
│   ├── test_feature_repository.py
│   ├── test_base_repositories.py
│   └── ...
├── services/                    # Pruebas unitarias de servicios
│   └── test_flamapy_integration.py
├── exceptions/                  # Pruebas unitarias de excepciones
│   ├── test_domain_exceptions.py
│   ├── test_exception_handlers.py
│   ├── test_additional_exceptions.py
│   └── test_feature_model_exceptions.py
├── utils/
│   ├── user.py                 # Utilitarios para crear usuarios de prueba
│   └── utils.py                # Utilidades generales
└── core/
    └── test_config.py          # Pruebas de configuración
```

---

## Pruebas Unitarias

### 1. Pruebas de Excepciones

**Propósito**: Verificar que las excepciones personalizadas:

- Heredan de la clase base correcta
- Retornan el código HTTP correcto
- Generan mensajes descriptivos
- Incluyen contexto relevante

**Ubicación**: `backend/app/tests/exceptions/`

#### Ejemplo: Pruebas de Excepciones de Dominio

**Archivo**: `test_domain_exceptions.py`

```python
"""
Unit tests for Domain custom exceptions.

Verifica:
1. Herencia de clase base correcta
2. Código de estado HTTP correcto
3. Mensajes de error descriptivos
4. Contexto relevante en el mensaje
"""

import pytest
from fastapi import HTTPException
from app.exceptions import (
    DomainNotFoundException,
    DomainAlreadyExistsException,
    InvalidDomainNameException,
)

class TestDomainEntityExceptions:
    """Tests para excepciones relacionadas con entidades de dominio."""

    def test_domain_not_found_exception(self):
        """Verifica DomainNotFoundException con ID de dominio."""
        domain_id = "123e4567-e89b-12d3-a456-426614174000"
        exception = DomainNotFoundException(domain_id=domain_id)

        assert exception.status_code == 404
        assert domain_id in exception.detail
        assert "not found" in exception.detail.lower()

    def test_domain_already_exists_exception(self):
        """Verifica DomainAlreadyExistsException con nombre de dominio."""
        domain_name = "E-Commerce"
        exception = DomainAlreadyExistsException(domain_name=domain_name)

        assert exception.status_code == 409
        assert domain_name in exception.detail
        assert "already exists" in exception.detail.lower()

    def test_invalid_domain_name_exception(self):
        """Verifica InvalidDomainNameException con nombre inválido y razón."""
        domain_name = ""
        reason = "Domain name cannot be empty"
        exception = InvalidDomainNameException(
            domain_name=domain_name,
            reason=reason
        )

        assert exception.status_code == 422
        assert reason in exception.detail
        assert "invalid" in exception.detail.lower()
```

**Propósito de cada test**:

- Validar códigos HTTP correctos (404, 409, 422, 403, etc.)
- Verificar que el contexto (IDs, nombres) está en el mensaje
- Asegurar consistencia de mensaje

**Aislamiento**:

- ✅ No requiere BD
- ✅ No requiere dependencias externas
- ✅ Pruebas puras de comportamiento de excepciones

#### Ejemplo: Pruebas de Manejadores de Excepciones

**Archivo**: `test_exception_handlers.py`

```python
import asyncio
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request

def _build_request(path: str, method: str = "GET") -> Request:
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "headers": [],
        "query_string": b"",
        "client": ("testclient", 50000),
        "scheme": "http",
        "server": ("testserver", 80),
    }
    return Request(scope)

def test_validation_exception_handler_returns_normalized_payload() -> None:
    """Verifica que el manejador de validación normaliza la respuesta."""
    request = _build_request("/api/v1/users", method="POST")
    exc = RequestValidationError(
        [{"loc": ("body", "email"), "msg": "Field required", "type": "missing"}]
    )

    response = asyncio.run(validation_exception_handler(request, exc))
    payload = response.body.decode("utf-8")

    assert response.status_code == 422
    assert '"object":"user.post"' in payload
    assert '"category":"request_validation"' in payload
    assert "Field 'body.email': Field required" in payload
```

---

### 2. Pruebas Unitarias de Repositorios

**Propósito**: Verificar la lógica de acceso a datos sin tocar la BD real.

**Ubicación**: `backend/app/tests/repositories/`

#### Estrategia de Aislamiento

Los repositorios se prueban usando **mocks de sesión SQLModel**:

```python
from unittest.mock import AsyncMock, Mock

def _build_session() -> Mock:
    """Crea una sesión mock reutilizable."""
    session = Mock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = Mock()
    return session
```

#### Ejemplo: Pruebas de Repositorio de Features

**Archivo**: `test_feature_repository.py`

```python
import asyncio
import uuid
from unittest.mock import AsyncMock, Mock
from app.repositories.feature import FeatureRepository

def run_async(coro):
    """Utilidad para ejecutar corrutinas en el contexto de prueba."""
    return asyncio.run(coro)

def _build_session() -> Mock:
    session = Mock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = Mock()
    return session

def test_get_returns_scalar_one_or_none() -> None:
    """Verifica que get() retorna el resultado esperado."""
    session = _build_session()
    expected = object()
    result = Mock()
    result.scalar_one_or_none.return_value = expected
    session.execute.return_value = result

    repo = FeatureRepository(session)
    found = run_async(repo.get(uuid.uuid4()))

    assert found is expected

def test_exists_returns_boolean() -> None:
    """Verifica que exists() usa get() para determinar existencia."""
    session = _build_session()
    repo = FeatureRepository(session)

    # Mock retorna algo la primera vez (existe), None la segunda (no existe)
    repo.get = AsyncMock(side_effect=[object(), None])

    assert run_async(repo.exists(uuid.uuid4())) is True
    assert run_async(repo.exists(uuid.uuid4())) is False

def test_activate_and_deactivate_toggle_flag() -> None:
    """Verifica que activate/deactivate modifican el flag correctamente."""
    session = _build_session()
    repo = FeatureRepository(session)
    feature = Mock(is_active=False)

    activated = run_async(repo.activate(feature))
    assert activated is feature
    assert feature.is_active is True

    deactivated = run_async(repo.deactivate(activated))
    assert deactivated is feature
    assert feature.is_active is False
```

**Técnicas de aislamiento usadas**:

| Técnica                | Propósito                                                 | Ejemplo                                             |
| ---------------------- | --------------------------------------------------------- | --------------------------------------------------- |
| **Mock() para sesión** | Simular SQLModel Session sin BD                           | `session = Mock()`                                  |
| **AsyncMock()**        | Simular métodos asincrónico (execute, commit)             | `session.execute = AsyncMock()`                     |
| **side_effect**        | Hacer que mock retorne valores diferentes en cada llamada | `repo.get = AsyncMock(side_effect=[obj, None])`     |
| **return_value**       | Configurar valor retornado por el mock                    | `result.scalar_one_or_none.return_value = expected` |

#### Ejemplo: Pruebas de Repositorio de Modelos de Features

**Archivo**: `test_feature_model_repository.py`

```python
import asyncio
import uuid
from app.api.deps import SessionLocal
from app.core.security import get_password_hash
from app.models.domain import DomainCreate
from app.models.feature_model import FeatureModelCreate, FeatureModelUpdate
from app.models.user import User
from app.repositories.domain import DomainRepository
from app.repositories.feature_model import FeatureModelRepository

def run_async(coro):
    return asyncio.run(coro)

async def _create_user(session, email: str) -> User:
    """Crea un usuario de prueba en la BD."""
    user = User(
        email=email,
        hashed_password=get_password_hash("test-password"),
        is_superuser=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

def test_feature_model_repository_crud() -> None:
    """Prueba flujo CRUD completo usando BD real."""
    async def _test() -> None:
        async with SessionLocal() as session:
            domain_repo = DomainRepository(session)
            feature_model_repo = FeatureModelRepository(session)

            # Crear usuario propietario
            user = await _create_user(session, f"owner-{uuid.uuid4()}@example.com")

            # Crear dominio
            domain = await domain_repo.create(
                DomainCreate(name=f"domain-{uuid.uuid4()}", description="repo test")
            )

            # Crear modelo de feature
            model = await feature_model_repo.create(
                FeatureModelCreate(
                    name=f"model-{uuid.uuid4()}",
                    description="initial",
                    domain_id=domain.id,
                ),
                owner_id=user.id,
            )

            # Verificaciones
            assert model.id
            assert model.domain_id == domain.id
            assert model.owner_id == user.id

            # GET
            fetched = await feature_model_repo.get(model.id)
            assert fetched.id == model.id

            # UPDATE
            update = FeatureModelUpdate(name=f"{model.name}-updated")
            updated = await feature_model_repo.update(fetched, update)
            assert updated.name.endswith("-updated")

            # COUNT
            count = await feature_model_repo.count()
            assert count >= 1

            # GET BY DOMAIN
            by_domain = await feature_model_repo.get_by_domain(domain.id)
            assert any(m.id == model.id for m in by_domain)

            # ACTIVATE/DEACTIVATE
            active = await feature_model_repo.activate(updated)
            assert active.is_active is True

            inactive = await feature_model_repo.deactivate(active)
            assert inactive.is_active is False

            # DELETE
            await feature_model_repo.delete(inactive)
            await domain_repo.delete(domain)
            await _delete_user(session, user.id)

    run_async(_test())
```

**Diferencia**: Esta prueba usa BD real vs mocks.

**Cuándo usar cada enfoque**:

| Approach    | Cuándo usarlo               | Ventajas                        | Desventajas               |
| ----------- | --------------------------- | ------------------------------- | ------------------------- |
| **Mocks**   | Lógica pura del repositorio | Rápido, aislado, determinístico | No valida SQL, queries    |
| **BD Real** | Flujo CRUD completo         | Valida SQL, transacciones       | Más lento, requiere setup |

---

### 3. Pruebas Unitarias de Servicios

**Propósito**: Verificar lógica de negocio sin dependencias externas.

**Ubicación**: `backend/app/tests/services/`

#### Ejemplo: Integración con Flamapy

**Archivo**: `test_flamapy_integration.py`

```python
import importlib
import pytest
from app.services.feature_model.fm_analysis_facade import _run_flamapy_satisfiable

UVL_MINIMAL = """namespace TestModel
features
    Root
        optional Child
"""

def _flamapy_module_available() -> bool:
    """Verifica si Flamapy está disponible en el entorno."""
    module_candidates = [
        "flamapy.interfaces.python.flama_feature_model",
        "flamapy.interfaces.python.flamapy_feature_model",
    ]
    for module_name in module_candidates:
        try:
            importlib.import_module(module_name)
            return True
        except Exception:
            continue
    return False

def test_flamapy_integration_if_available():
    """Prueba Flamapy si está disponible, si no, salta la prueba."""
    if not _flamapy_module_available():
        pytest.skip("Flamapy no está disponible en el entorno de test")

    result = _run_flamapy_satisfiable(UVL_MINIMAL)
    assert result is not None
    assert result is True

def test_flamapy_integration_returns_none_when_missing(monkeypatch):
    """Verifica comportamiento graceful cuando Flamapy no está disponible."""
    def _raise(*_args, **_kwargs):
        raise ModuleNotFoundError()

    monkeypatch.setattr(importlib, "import_module", _raise)
    assert _run_flamapy_satisfiable(UVL_MINIMAL) is None
```

**Técnicas usadas**:

| Técnica                     | Propósito                                          |
| --------------------------- | -------------------------------------------------- |
| **pytest.skip()**           | Saltar prueba si condición no se cumple            |
| **monkeypatch**             | Simular que módulo no está disponible              |
| **importlib.import_module** | Detectar disponibilidad de dependencias opcionales |

---

### 4. Pruebas de Repositorios Base

**Propósito**: Verificar métodos compartidos en repositorios base.

**Ubicación**: `backend/app/tests/repositories/test_base_repositories.py`

```python
import uuid
from unittest.mock import patch
import pytest
from app.models.domain import Domain
from app.repositories.base import BaseDomainRepository

class _DomainRepo(BaseDomainRepository):
    """Implementación concreta para pruebas."""
    pass

def test_base_domain_validate_name_unique_raises() -> None:
    """Verifica que validar nombre único levanta excepción."""
    repo = _DomainRepo()
    existing = Domain(name="Domain", description="test")
    with pytest.raises(ValueError):
        repo.validate_name_unique(existing)

def test_base_domain_validate_name_unique_allows_same_id() -> None:
    """Verifica que mismo ID es permitido (es la misma entidad)."""
    repo = _DomainRepo()
    domain_id = uuid.uuid4()
    existing = Domain(id=domain_id, name="Domain", description="test")
    repo.validate_name_unique(existing, current_domain_id=domain_id)

def test_base_user_prepare_password_uses_hash_helper() -> None:
    """Verifica que preparar contraseña usa el hash helper."""
    repo = _UserRepo()
    with patch("app.core.security.get_password_hash", return_value="hashed") as mocked:
        result = repo.prepare_password("plain")

    mocked.assert_called_once_with("plain")
    assert result == "hashed"
```

---

## Pruebas de Integración

### 1. Pruebas de Controladores (Rutas API)

**Propósito**: Verificar flujo HTTP completo (request → middleware → handler → response).

**Ubicación**: `backend/app/tests/api/routes/`

#### Estructura General

```python
from fastapi.testclient import TestClient
from app.core.config import settings

def test_feature_model_crud(
    client: TestClient,
    superuser_token_headers: dict[str, str]
) -> None:
    """Prueba CRUD completo de Feature Models."""
    # Configuración
    domain_id = _create_domain(client, superuser_token_headers)
    model_name = f"model-{random_lower_string()}"

    # CREATE
    create_payload = {...}
    create_response = client.post(
        f"{settings.API_V1_PREFIX}/feature-models/",
        headers=superuser_token_headers,
        json=create_payload,
    )
    assert create_response.status_code == 201
    created = create_response.json()
    model_id = created["id"]

    # READ (List)
    list_response = client.get(
        f"{settings.API_V1_PREFIX}/feature-models/",
        headers=superuser_token_headers,
    )
    assert list_response.status_code == 200
    data = list_response.json()
    assert any(item["id"] == model_id for item in data["data"])

    # READ (Detail)
    detail_response = client.get(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}",
        headers=superuser_token_headers,
    )
    assert detail_response.status_code == 200

    # UPDATE
    update_payload = {"name": f"{model_name}-updated"}
    update_response = client.patch(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}",
        headers=superuser_token_headers,
        json=update_payload,
    )
    assert update_response.status_code == 200

    # SPECIAL OPS (activate/deactivate)
    deactivate_response = client.patch(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/deactivate",
        headers=superuser_token_headers,
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False

    activate_response = client.patch(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/activate",
        headers=superuser_token_headers,
    )
    assert activate_response.status_code == 200
    assert activate_response.json()["is_active"] is True

    # DELETE
    delete_response = client.delete(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}",
        headers=superuser_token_headers,
    )
    assert delete_response.status_code == 200
```

#### Ejemplo: Pruebas Parametrizadas

```python
import pytest

@pytest.mark.parametrize(
    "method,endpoint,payload,expected_status",
    [
        ("patch", "/feature-models/{model_id}", {"name": "updated"}, 200),
        ("patch", "/feature-models/{model_id}/activate", None, 200),
        ("patch", "/feature-models/{model_id}/deactivate", None, 200),
    ],
)
def test_feature_model_updates(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    method: str,
    endpoint: str,
    payload: dict | None,
    expected_status: int,
) -> None:
    """Prueba múltiples operaciones de actualización."""
    model_id = _create_feature_model(client, superuser_token_headers)

    if method == "patch":
        response = client.patch(
            f"{settings.API_V1_PREFIX}{endpoint.format(model_id=model_id)}",
            headers=superuser_token_headers,
            json=payload or {},
        )

    assert response.status_code == expected_status
```

**Ventajas de pytest.mark.parametrize**:

- Reduce duplicación de código
- Aumenta cobertura con menos líneas
- Cada parámetro se ejecuta como prueba separada

#### Ejemplo: Pruebas de Autenticación y Autorización

**Archivo**: `test_deps_auth.py`

```python
import asyncio
import uuid
from unittest.mock import AsyncMock, patch
import pytest
from fastapi import HTTPException
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from app.api.deps import get_current_user

def _run(coro):
    return asyncio.run(coro)

def test_get_current_user_without_token_raises_401() -> None:
    """Verifica que sin token retorna 401."""
    user_repo = AsyncMock()
    with pytest.raises(HTTPException) as exc:
        _run(get_current_user(user_repo=user_repo, token=""))
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"

def test_get_current_user_with_expired_token_raises_401() -> None:
    """Verifica que token expirado retorna 401 con mensaje específico."""
    user_repo = AsyncMock()
    with patch("app.api.deps.jwt.decode", side_effect=ExpiredSignatureError()):
        with pytest.raises(HTTPException) as exc:
            _run(get_current_user(user_repo=user_repo, token="expired"))

    assert exc.value.status_code == 401
    assert exc.value.detail == "Token expired"

def test_get_current_user_with_invalid_token_raises_401() -> None:
    """Verifica que token inválido retorna 401."""
    user_repo = AsyncMock()
    with patch("app.api.deps.jwt.decode", side_effect=InvalidTokenError()):
        with pytest.raises(HTTPException) as exc:
            _run(get_current_user(user_repo=user_repo, token="invalid"))

    assert exc.value.status_code == 401
    assert exc.value.detail == "Could not validate credentials"

def test_get_current_user_when_user_not_found_raises_401() -> None:
    """Verifica que usuario no encontrado retorna 401."""
    user_id = uuid.uuid4()
    user_repo = AsyncMock()
    user_repo.get = AsyncMock(return_value=None)

    with patch("app.api.deps.jwt.decode", return_value={"sub": str(user_id)}):
        with pytest.raises(HTTPException) as exc:
            _run(get_current_user(user_repo=user_repo, token="ok"))

    assert exc.value.status_code == 401
    assert exc.value.detail == "User not found"

def test_get_current_user_when_user_inactive_raises_403() -> None:
    """Verifica que usuario inactivo retorna 403."""
    user_id = uuid.uuid4()
    inactive_user = SimpleNamespace(is_active=False)
    user_repo = AsyncMock()
    user_repo.get = AsyncMock(return_value=inactive_user)

    with patch("app.api.deps.jwt.decode", return_value={"sub": str(user_id)}):
        with pytest.raises(HTTPException) as exc:
            _run(get_current_user(user_repo=user_repo, token="ok"))

    assert exc.value.status_code == 403
    assert exc.value.detail == "Inactive user"
```

---

### 2. Configuración de Fixtures Globales

**Archivo**: `backend/app/tests/conftest.py`

```python
from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete
from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models.user import User

@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    """
    Fixture de base de datos para toda la sesión de pruebas.

    - Scope: session (una sola vez, al inicio)
    - autouse: True (ejecuta automáticamente)
    - Propósito: Inicializar schema y limpiar al final
    """
    with Session(engine) as session:
        init_db(session)
        yield session
        # Cleanup: eliminar todos los usuarios
        statement = delete(User)
        session.execute(statement)
        session.commit()

@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """
    Cliente HTTP de prueba para rutas API.

    - Scope: module (compartido por todas las pruebas del módulo)
    - Propósito: Hacer peticiones HTTP sin servidor externo
    """
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    """
    Headers de autenticación para superusuario.

    Propósito: Permitir pruebas que requieren autenticación admin
    """
    return get_superuser_token_headers(client)

@pytest.fixture(scope="module")
def normal_user_token_headers(
    client: TestClient,
    db: Session
) -> dict[str, str]:
    """
    Headers de autenticación para usuario normal.

    Propósito: Pruebas con permisos limitados
    """
    return authentication_token_from_email(
        client=client,
        email=settings.EMAIL_TEST_USER,
        db=db
    )
```

**Scopes de fixtures**:

| Scope        | Vida útil                      | Uso                            |
| ------------ | ------------------------------ | ------------------------------ |
| **session**  | Toda la sesión de pruebas      | BD, recursos compartidos       |
| **module**   | Todas las pruebas de un módulo | TestClient, tokens             |
| **function** | Una sola prueba                | Por defecto, datos específicos |

---

## Aislamiento y Mocking

### Estrategia de Aislamiento por Nivel

#### 1. Nivel de Excepción (aislamiento máximo)

```python
# ✅ Prueba unitaria pura - SIN dependencias
def test_domain_not_found_exception():
    domain_id = "123"
    exception = DomainNotFoundException(domain_id=domain_id)
    assert exception.status_code == 404
```

**Características**:

- No requiere BD
- No requiere servicios externos
- Ejecución < 1ms
- Aislamiento: **100%**

#### 2. Nivel de Repositorio (aislamiento parcial)

**Opción A: Con Mocks (aislamiento máximo)**

```python
def test_feature_exists_with_mock():
    session = Mock()
    repo = FeatureRepository(session)
    repo.get = AsyncMock(side_effect=[object(), None])

    assert asyncio.run(repo.exists(uuid.uuid4())) is True
    assert asyncio.run(repo.exists(uuid.uuid4())) is False
```

**Características**:

- Aislamiento: **100%**
- Velocidad: **Muy rápida** (~1-10ms)
- Cobertura: Lógica del repositorio

**Opción B: Con BD Real (cobertura máxima)**

```python
async def test_feature_crud_with_real_db():
    async with SessionLocal() as session:
        repo = FeatureRepository(session)
        feature = await repo.create(FeatureCreate(...))
        assert feature.id is not None
```

**Características**:

- Aislamiento: **Parcial** (toca BD)
- Velocidad: **Lenta** (~100-500ms)
- Cobertura: SQL + lógica

#### 3. Nivel de Controlador (integración)

```python
def test_create_domain_endpoint(client: TestClient, superuser_token_headers):
    # Las dependencias se resuelven realmente
    response = client.post(
        "/api/v1/domains/",
        headers=superuser_token_headers,
        json={"name": "Domain 1", "description": "Test"},
    )
    assert response.status_code == 201
```

**Características**:

- Aislamiento: **Mínimo** (prueba stack completo)
- Velocidad: **Lenta** (~500ms-2s)
- Cobertura: Máxima (middleware, autenticación, BD, lógica)

### Técnicas de Mocking Usadas

#### 1. **patch()**: Reemplazar función/método

```python
from unittest.mock import patch

def test_with_patch():
    with patch("app.core.security.get_password_hash", return_value="hashed"):
        result = repo.prepare_password("plain")
        assert result == "hashed"
```

**Cuándo usar**: Reemplazar funciones externas, servicios, librerías

#### 2. **monkeypatch**: Fixture de pytest

```python
def test_with_monkeypatch(monkeypatch):
    def mock_import(*args, **kwargs):
        raise ModuleNotFoundError()

    monkeypatch.setattr(importlib, "import_module", mock_import)
    result = _run_flamapy_satisfiable(UVL_CODE)
    assert result is None
```

**Cuándo usar**: Atributos, módulos, configuración

#### 3. **AsyncMock()**: Mock para async

```python
from unittest.mock import AsyncMock

async_function = AsyncMock(return_value=42)
result = await async_function()  # retorna 42
```

**Cuándo usar**: Métodos async, llamadas a BD, APIs

#### 4. **side_effect**: Secuencia de valores

```python
mock = AsyncMock(side_effect=[1, 2, 3, ValueError("error")])
await mock()  # retorna 1
await mock()  # retorna 2
await mock()  # retorna 3
await mock()  # levanta ValueError
```

**Cuándo usar**: Simular comportamiento que cambia (retry, fallback)

#### 5. **return_value**: Valor específico

```python
result_mock = Mock()
result_mock.scalar_one_or_none.return_value = expected_object
session.execute.return_value = result_mock
```

**Cuándo usar**: Métodos que retornan valores específicos

### Matriz de Aislamiento

| Tipo de Prueba         | Ubicación     | Mocks   | BD      | Dependencias | Velocidad | Cobertura |
| ---------------------- | ------------- | ------- | ------- | ------------ | --------- | --------- |
| **Excepciones**        | exceptions/   | ✅ 100% | ❌ No   | ❌ No        | ⚡⚡⚡    | Baja      |
| **Repositorio (Mock)** | repositories/ | ✅ 100% | ❌ No   | ❌ No        | ⚡⚡      | Media     |
| **Repositorio (Real)** | repositories/ | ❌ No   | ✅ Sí   | ❌ No        | ⚡        | Alta      |
| **Servicio**           | services/     | Parcial | Depende | Parcial      | ⚡        | Media     |
| **Controlador**        | api/routes/   | ❌ No   | ✅ Sí   | ✅ Sí        | 🐌        | Muy Alta  |

---

## Mejores Prácticas Implementadas

### 1. **Fixtures Reutilizables**

```python
@pytest.fixture
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    """Reutilizable en múltiples pruebas."""
    return get_superuser_token_headers(client)
```

### 2. **Helper Functions**

```python
def _create_domain(client: TestClient, headers: dict) -> str:
    """Evita duplicación de lógica de setup."""
    response = client.post(
        f"{settings.API_V1_PREFIX}/domains/",
        headers=headers,
        json={"name": f"domain-{random_lower_string()}", "description": "test"},
    )
    return response.json()["id"]
```

### 3. **Parametrización**

```python
@pytest.mark.parametrize(
    "status_code,fragment",
    [
        (404, "not found"),
        (409, "already exists"),
        (403, "permissions"),
    ],
)
def test_exception_status(status_code, fragment):
    # Reduce duplicación, aumenta cobertura
    pass
```

### 4. **Generadores para Cleanup**

```python
@pytest.fixture
def db():
    with Session(engine) as session:
        init_db(session)
        yield session
        # Cleanup aquí
        session.execute(delete(User))
        session.commit()
```

### 5. **Aserción Clara**

```python
# ✅ Bueno
assert response.status_code == 201
assert "id" in response.json()

# ❌ Malo
assert response.status_code is 201  # usa ==, no is
assert response.json()  # no específico
```

---

## Ejecución de Pruebas

### Comandos

```bash
# Todos los tests
cd backend
pytest -q

# Tests específicos de un módulo
pytest app/tests/repositories/ -v

# Con cobertura
pytest --cov=app app/tests/

# Tests de excepciones
pytest app/tests/exceptions/ -v

# Tests de integración (solo)
pytest app/tests/api/routes/ -v
```

### Configuración (en conftest.py implícitamente)

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["app/tests"]
python_files = ["test_*.py"]
```

---

## Conclusión

El proyecto Feature Model implementa una estrategia de pruebas robusta:

✅ **Excepciones**: Pruebas unitarias puras con máximo aislamiento  
✅ **Repositorios**: Mixto de mocks (lógica) y BD real (integración)  
✅ **Servicios**: Unitarias con aislamiento selectivo  
✅ **Controladores**: Integración completa con BD y autenticación

**Principios clave**:

1. **Aislamiento apropiado**: Excepciones 100%, controladores 0%
2. **Velocidad vs Cobertura**: Ajustar según nivel
3. **Reutilización**: Fixtures, helpers, parametrización
4. **Claridad**: Nombres descriptivos, una cosa por test
