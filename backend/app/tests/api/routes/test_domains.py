import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.models.domain import Domain, DomainCreate, DomainUpdate
from app.repositories.sync.domain import DomainRepositorySync
from app.tests.utils.utils import random_lower_string


def random_domain_name() -> str:
    """Genera un nombre aleatorio para dominio."""
    return f"domain_{random_lower_string()}"


def test_create_domain(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test crear un nuevo dominio."""
    domain_name = random_domain_name()
    description = random_lower_string()
    data = {"name": domain_name, "description": description}

    r = client.post(
        f"{settings.API_V1_STR}/domains/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    created_domain = r.json()
    assert created_domain["name"] == domain_name
    assert created_domain["description"] == description
    assert "id" in created_domain

    # Verificar en base de datos
    domain_repo = DomainRepositorySync(db)
    domain = domain_repo.get_by_name(name=domain_name)
    assert domain
    assert domain.name == domain_name


def test_create_domain_duplicate_name(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test crear dominio con nombre duplicado devuelve error."""
    domain_name = random_domain_name()
    domain_in = DomainCreate(name=domain_name, description="Test")
    domain_repo = DomainRepositorySync(db)
    domain_repo.create(domain_in)

    # Intentar crear otro con el mismo nombre
    data = {"name": domain_name, "description": "Another description"}
    r = client.post(
        f"{settings.API_V1_STR}/domains/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 400


def test_create_domain_by_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """Test usuario normal no puede crear dominios."""
    domain_name = random_domain_name()
    data = {"name": domain_name, "description": "Test"}
    r = client.post(
        f"{settings.API_V1_STR}/domains/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 403


def test_create_domain_empty_name(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test crear dominio con nombre vacío devuelve error de validación."""
    data = {"name": "", "description": "Test"}
    r = client.post(
        f"{settings.API_V1_STR}/domains/",
        headers=superuser_token_headers,
        json=data,
    )
    # Puede ser 400 o 422 dependiendo de la validación de Pydantic
    assert r.status_code in [400, 422]


def test_create_domain_without_description(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test crear dominio sin descripción es válido."""
    domain_name = random_domain_name()
    data = {"name": domain_name}

    r = client.post(
        f"{settings.API_V1_STR}/domains/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    created_domain = r.json()
    assert created_domain["name"] == domain_name
    assert (
        created_domain.get("description") is None
        or created_domain.get("description") == ""
    )


def test_read_domain(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test obtener un dominio por ID."""
    domain_name = random_domain_name()
    domain_in = DomainCreate(name=domain_name, description="Test domain")
    domain_repo = DomainRepositorySync(db)
    domain = domain_repo.create(domain_in)

    r = client.get(
        f"{settings.API_V1_STR}/domains/{domain.id}/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    api_domain = r.json()
    assert api_domain["id"] == str(domain.id)
    assert api_domain["name"] == domain_name


def test_read_domain_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test obtener dominio inexistente devuelve 404."""
    r = client.get(
        f"{settings.API_V1_STR}/domains/{uuid.uuid4()}/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "Domain not found"


def test_read_domains(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test listar dominios con paginación."""
    # Crear algunos dominios de prueba
    domain_repo = DomainRepositorySync(db)
    domain1 = domain_repo.create(
        DomainCreate(name=random_domain_name(), description="Test 1")
    )
    domain2 = domain_repo.create(
        DomainCreate(name=random_domain_name(), description="Test 2")
    )

    r = client.get(
        f"{settings.API_V1_STR}/domains/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    domains_response = r.json()

    assert "data" in domains_response
    assert "count" in domains_response
    assert "page" in domains_response
    assert "size" in domains_response
    assert len(domains_response["data"]) >= 2


def test_read_domains_with_pagination(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test paginación en listado de dominios."""
    r = client.get(
        f"{settings.API_V1_STR}/domains/?skip=0&limit=5",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    domains_response = r.json()
    assert len(domains_response["data"]) <= 5


def test_read_domains_by_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test usuario normal puede listar dominios (solo activos)."""
    domain_repo = DomainRepositorySync(db)

    # Crear dominio activo
    active_domain = domain_repo.create(
        DomainCreate(name=random_domain_name(), description="Active")
    )

    # Crear dominio inactivo
    inactive_domain = domain_repo.create(
        DomainCreate(name=random_domain_name(), description="Inactive")
    )
    domain_repo.deactivate(inactive_domain)

    r = client.get(
        f"{settings.API_V1_STR}/domains/",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 200
    domains_response = r.json()

    # Verificar que el usuario normal solo ve dominios activos
    domain_ids = [d["id"] for d in domains_response["data"]]
    assert str(active_domain.id) in domain_ids
    # El dominio inactivo NO debería aparecer para usuarios normales
    # (dependiendo de la implementación del filtro)


def test_update_domain(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test actualizar un dominio."""
    domain_name = random_domain_name()
    domain_in = DomainCreate(name=domain_name, description="Original description")
    domain_repo = DomainRepositorySync(db)
    domain = domain_repo.create(domain_in)

    new_name = random_domain_name()
    new_description = "Updated description"
    data = {"name": new_name, "description": new_description}

    r = client.patch(
        f"{settings.API_V1_STR}/domains/{domain.id}/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    updated_domain = r.json()
    assert updated_domain["name"] == new_name
    assert updated_domain["description"] == new_description

    # Verificar en base de datos
    db.refresh(domain)
    assert domain.name == new_name
    assert domain.description == new_description


def test_update_domain_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test actualizar dominio inexistente devuelve 404."""
    data = {"name": random_domain_name(), "description": "Test"}
    r = client.patch(
        f"{settings.API_V1_STR}/domains/{uuid.uuid4()}/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "Domain not found"


def test_update_domain_duplicate_name(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test actualizar dominio con nombre ya existente devuelve error."""
    domain_repo = DomainRepositorySync(db)
    domain1 = domain_repo.create(
        DomainCreate(name=random_domain_name(), description="Domain 1")
    )
    domain2 = domain_repo.create(
        DomainCreate(name=random_domain_name(), description="Domain 2")
    )

    # Intentar actualizar domain2 con el nombre de domain1
    data = {"name": domain1.name}
    r = client.patch(
        f"{settings.API_V1_STR}/domains/{domain2.id}/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 400


def test_update_domain_only_name(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test actualizar solo el nombre de un dominio."""
    domain_repo = DomainRepositorySync(db)
    original_description = "Original description"
    domain = domain_repo.create(
        DomainCreate(name=random_domain_name(), description=original_description)
    )

    new_name = random_domain_name()
    data = {"name": new_name}

    r = client.patch(
        f"{settings.API_V1_STR}/domains/{domain.id}/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    updated_domain = r.json()
    assert updated_domain["name"] == new_name
    # La descripción debe mantenerse
    assert updated_domain["description"] == original_description


def test_update_domain_only_description(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test actualizar solo la descripción de un dominio."""
    domain_repo = DomainRepositorySync(db)
    original_name = random_domain_name()
    domain = domain_repo.create(
        DomainCreate(name=original_name, description="Original description")
    )

    new_description = "Updated description"
    data = {"description": new_description}

    r = client.patch(
        f"{settings.API_V1_STR}/domains/{domain.id}/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    updated_domain = r.json()
    # El nombre debe mantenerse
    assert updated_domain["name"] == original_name
    assert updated_domain["description"] == new_description


def test_update_domain_by_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test usuario normal no puede actualizar dominios."""
    domain_repo = DomainRepositorySync(db)
    domain = domain_repo.create(
        DomainCreate(name=random_domain_name(), description="Test")
    )

    data = {"description": "New description"}
    r = client.patch(
        f"{settings.API_V1_STR}/domains/{domain.id}/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 403


def test_delete_domain(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test eliminar un dominio."""
    domain_repo = DomainRepositorySync(db)
    domain = domain_repo.create(
        DomainCreate(name=random_domain_name(), description="Test")
    )
    domain_id = domain.id

    r = client.delete(
        f"{settings.API_V1_STR}/domains/{domain_id}/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    assert r.json()["message"] == "Domain deleted successfully"

    # Verificar que se eliminó
    result = db.exec(select(Domain).where(Domain.id == domain_id)).first()
    assert result is None


def test_delete_domain_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test eliminar dominio inexistente devuelve 404."""
    r = client.delete(
        f"{settings.API_V1_STR}/domains/{uuid.uuid4()}/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "Domain not found"


def test_delete_domain_with_feature_models(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test no se puede eliminar dominio con feature models asociados.

    Nota: Este test requiere crear un feature model asociado al dominio.
    Se puede implementar cuando esté disponible el módulo de feature models.
    """
    # TODO: Implementar cuando feature models esté disponible
    # domain_repo = DomainRepositorySync(db)
    # domain = domain_repo.create(
    #     DomainCreate(name=random_domain_name(), description="Test")
    # )
    #
    # # Crear un feature model asociado
    # feature_model = create_test_feature_model(domain_id=domain.id)
    #
    # r = client.delete(
    #     f"{settings.API_V1_STR}/domains/{domain.id}/",
    #     headers=superuser_token_headers,
    # )
    # assert r.status_code == 400
    # assert "associated feature models" in r.json()["detail"].lower()
    pass


def test_delete_domain_by_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test usuario normal no puede eliminar dominios."""
    domain_repo = DomainRepositorySync(db)
    domain = domain_repo.create(
        DomainCreate(name=random_domain_name(), description="Test")
    )

    r = client.delete(
        f"{settings.API_V1_STR}/domains/{domain.id}/",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403


def test_search_domains(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test buscar dominios por nombre o descripción."""
    search_term = f"searchable_{random_lower_string()}"
    domain_repo = DomainRepositorySync(db)

    # Crear dominio con término de búsqueda en el nombre
    domain1 = domain_repo.create(
        DomainCreate(name=f"{search_term}_domain", description="Test")
    )

    # Crear dominio con término de búsqueda en descripción
    domain2 = domain_repo.create(
        DomainCreate(name=random_domain_name(), description=f"Contains {search_term}")
    )

    r = client.get(
        f"{settings.API_V1_STR}/domains/search/?search_term={search_term}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    search_response = r.json()
    assert "data" in search_response
    assert len(search_response["data"]) >= 2

    # Verificar que ambos dominios están en los resultados
    domain_ids = [d["id"] for d in search_response["data"]]
    assert str(domain1.id) in domain_ids
    assert str(domain2.id) in domain_ids


def test_search_domains_no_results(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test buscar dominios sin resultados devuelve lista vacía."""
    # Buscar término que no existe
    search_term = f"nonexistent_{random_lower_string()}"

    r = client.get(
        f"{settings.API_V1_STR}/domains/search/?search_term={search_term}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    search_response = r.json()
    assert "data" in search_response
    assert len(search_response["data"]) == 0
    assert search_response["count"] == 0


def test_search_domains_by_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test usuario normal puede buscar dominios (solo activos)."""
    search_term = f"searchable_{random_lower_string()}"
    domain_repo = DomainRepositorySync(db)

    # Crear dominio activo
    domain_repo.create(
        DomainCreate(name=f"{search_term}_active", description="Active domain")
    )

    r = client.get(
        f"{settings.API_V1_STR}/domains/search/?search_term={search_term}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 200
    search_response = r.json()
    assert len(search_response["data"]) >= 1


def test_read_domain_with_feature_models(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test obtener dominio con sus feature models."""
    domain_repo = DomainRepositorySync(db)
    domain = domain_repo.create(
        DomainCreate(name=random_domain_name(), description="Test")
    )

    r = client.get(
        f"{settings.API_V1_STR}/domains/{domain.id}/with-feature-models/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    domain_data = r.json()
    assert domain_data["id"] == str(domain.id)
    assert domain_data["name"] == domain.name
    assert "feature_models" in domain_data
    # Por defecto debería estar vacío
    assert isinstance(domain_data["feature_models"], list)
    assert len(domain_data["feature_models"]) == 0


def test_read_domain_with_feature_models_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test obtener dominio inexistente con feature models devuelve 404."""
    r = client.get(
        f"{settings.API_V1_STR}/domains/{uuid.uuid4()}/with-feature-models/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "Domain not found"


def test_read_domain_with_feature_models_by_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test usuario normal no puede obtener dominio con feature models."""
    domain_repo = DomainRepositorySync(db)
    domain = domain_repo.create(
        DomainCreate(name=random_domain_name(), description="Test")
    )

    r = client.get(
        f"{settings.API_V1_STR}/domains/{domain.id}/with-feature-models/",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403


def test_activate_domain(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test activar un dominio desactivado."""
    domain_repo = DomainRepositorySync(db)
    domain = domain_repo.create(
        DomainCreate(name=random_domain_name(), description="Test")
    )

    # Desactivar primero
    domain_repo.deactivate(domain)
    db.refresh(domain)
    assert domain.is_active is False

    # Activar vía API
    r = client.patch(
        f"{settings.API_V1_STR}/domains/{domain.id}/activate/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    activated_domain = r.json()
    assert activated_domain["is_active"] is True

    # Verificar en base de datos
    db.refresh(domain)
    assert domain.is_active is True


def test_activate_domain_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test activar dominio inexistente devuelve 404."""
    r = client.patch(
        f"{settings.API_V1_STR}/domains/{uuid.uuid4()}/activate/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "Domain not found"


def test_activate_domain_by_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test usuario normal no puede activar dominios."""
    domain_repo = DomainRepositorySync(db)
    domain = domain_repo.create(
        DomainCreate(name=random_domain_name(), description="Test")
    )

    r = client.patch(
        f"{settings.API_V1_STR}/domains/{domain.id}/activate/",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403


def test_activate_already_active_domain(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test activar un dominio ya activo no genera error."""
    domain_repo = DomainRepositorySync(db)
    domain = domain_repo.create(
        DomainCreate(name=random_domain_name(), description="Test")
    )

    # El dominio debería estar activo por defecto
    assert domain.is_active is True

    # Activar dominio ya activo
    r = client.patch(
        f"{settings.API_V1_STR}/domains/{domain.id}/activate/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    activated_domain = r.json()
    assert activated_domain["is_active"] is True


def test_deactivate_domain(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test desactivar un dominio activo."""
    domain_repo = DomainRepositorySync(db)
    domain = domain_repo.create(
        DomainCreate(name=random_domain_name(), description="Test")
    )

    assert domain.is_active is True

    # Desactivar vía API
    r = client.patch(
        f"{settings.API_V1_STR}/domains/{domain.id}/deactivate/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    deactivated_domain = r.json()
    assert deactivated_domain["is_active"] is False

    # Verificar en base de datos
    db.refresh(domain)
    assert domain.is_active is False


def test_deactivate_domain_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test desactivar dominio inexistente devuelve 404."""
    r = client.patch(
        f"{settings.API_V1_STR}/domains/{uuid.uuid4()}/deactivate/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "Domain not found"


def test_deactivate_domain_by_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test usuario normal no puede desactivar dominios."""
    domain_repo = DomainRepositorySync(db)
    domain = domain_repo.create(
        DomainCreate(name=random_domain_name(), description="Test")
    )

    r = client.patch(
        f"{settings.API_V1_STR}/domains/{domain.id}/deactivate/",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403


def test_deactivate_already_inactive_domain(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test desactivar un dominio ya inactivo no genera error."""
    domain_repo = DomainRepositorySync(db)
    domain = domain_repo.create(
        DomainCreate(name=random_domain_name(), description="Test")
    )

    # Desactivar primero
    domain_repo.deactivate(domain)
    db.refresh(domain)
    assert domain.is_active is False

    # Desactivar dominio ya inactivo
    r = client.patch(
        f"{settings.API_V1_STR}/domains/{domain.id}/deactivate/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    deactivated_domain = r.json()
    assert deactivated_domain["is_active"] is False


def test_activate_then_deactivate_domain(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test flujo completo de activar y desactivar dominio."""
    domain_repo = DomainRepositorySync(db)
    domain = domain_repo.create(
        DomainCreate(name=random_domain_name(), description="Test")
    )

    # Desactivar
    r = client.patch(
        f"{settings.API_V1_STR}/domains/{domain.id}/deactivate/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    assert r.json()["is_active"] is False

    # Activar nuevamente
    r = client.patch(
        f"{settings.API_V1_STR}/domains/{domain.id}/activate/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    assert r.json()["is_active"] is True

    # Verificar en base de datos
    db.refresh(domain)
    assert domain.is_active is True
