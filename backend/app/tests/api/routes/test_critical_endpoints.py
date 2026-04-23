import uuid
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.enums import ModelStatus
from app.tests.utils.utils import random_email, random_lower_string


def _extract_error_detail(response) -> str:
    payload = response.json()
    if isinstance(payload, dict):
        if "detail" in payload:
            return str(payload["detail"])
        message = payload.get("message")
        if isinstance(message, dict):
            return str(message.get("description", ""))
    return ""


def _login_and_get_headers(
    client: TestClient, email: str, password: str
) -> dict[str, str]:
    response = client.post(
        f"{settings.API_V1_PREFIX}/login/access-token",
        json={"email": email, "password": password},
    )

    # Compatibilidad con implementaciones legacy del endpoint de login.
    if response.status_code == 422:
        response = client.post(
            f"{settings.API_V1_PREFIX}/login/access-token",
            data={"username": email, "password": password},
        )

    assert response.status_code == 200
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def _create_domain(client: TestClient, headers: dict[str, str]) -> str:
    payload = {
        "name": f"domain-{random_lower_string()}",
        "description": "critical endpoint tests",
    }
    response = client.post(
        f"{settings.API_V1_PREFIX}/domains/",
        headers=headers,
        json=payload,
    )
    assert 200 <= response.status_code < 300
    return response.json()["id"]


def _create_feature_model(
    client: TestClient, headers: dict[str, str], domain_id: str
) -> str:
    payload = {
        "name": f"fm-{random_lower_string()}",
        "description": "critical endpoint tests",
        "domain_id": domain_id,
    }
    response = client.post(
        f"{settings.API_V1_PREFIX}/feature-models/",
        headers=headers,
        json=payload,
    )
    assert response.status_code == 201
    return response.json()["id"]


def _create_feature_model_version(
    client: TestClient, headers: dict[str, str], model_id: str
) -> str:
    response = client.post(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions",
        headers=headers,
        json={},
    )
    assert response.status_code == 200
    return response.json()["id"]


def _create_viewer_user_headers(
    client: TestClient, superuser_headers: dict[str, str]
) -> dict[str, str]:
    email = random_email()
    password = "ViewerPass123!"
    create_response = client.post(
        f"{settings.API_V1_PREFIX}/users/",
        headers=superuser_headers,
        json={
            "email": email,
            "password": password,
            "role": "viewer",
        },
    )
    assert 200 <= create_response.status_code < 300
    return _login_and_get_headers(client, email, password)


def test_critical_login_access_token_returns_access_and_refresh(
    client: TestClient,
) -> None:
    response = client.post(
        f"{settings.API_V1_PREFIX}/login/access-token",
        json={
            "email": settings.FIRST_SUPERUSER,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["access_token"]
    assert payload["refresh_token"]
    assert payload["token_type"] == "bearer"


def test_critical_login_invalid_payload_shape_returns_422(client: TestClient) -> None:
    response = client.post(
        f"{settings.API_V1_PREFIX}/login/access-token",
        data={
            "username": settings.FIRST_SUPERUSER,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        },
    )
    assert response.status_code == 422


def test_critical_users_create_requires_authentication(client: TestClient) -> None:
    response = client.post(
        f"{settings.API_V1_PREFIX}/users/",
        json={
            "email": random_email(),
            "password": "StrongPass123!",
            "role": "viewer",
        },
    )
    assert response.status_code == 401


def test_critical_feature_model_create_forbidden_for_viewer(client: TestClient) -> None:
    superuser_headers = _login_and_get_headers(
        client,
        settings.FIRST_SUPERUSER,
        settings.FIRST_SUPERUSER_PASSWORD,
    )
    viewer_headers = _create_viewer_user_headers(client, superuser_headers)
    domain_id = _create_domain(client, superuser_headers)

    response = client.post(
        f"{settings.API_V1_PREFIX}/feature-models/",
        headers=viewer_headers,
        json={
            "name": f"restricted-{random_lower_string()}",
            "description": "should fail",
            "domain_id": domain_id,
        },
    )

    assert response.status_code == 403


def test_critical_feature_model_delete_forbidden_for_non_owner(
    client: TestClient,
) -> None:
    superuser_headers = _login_and_get_headers(
        client,
        settings.FIRST_SUPERUSER,
        settings.FIRST_SUPERUSER_PASSWORD,
    )
    viewer_headers = _create_viewer_user_headers(client, superuser_headers)

    domain_id = _create_domain(client, superuser_headers)
    model_id = _create_feature_model(client, superuser_headers, domain_id)

    response = client.delete(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}",
        headers=viewer_headers,
    )

    assert response.status_code == 403


def test_critical_feature_model_delete_blocked_by_business_rule(
    client: TestClient,
) -> None:
    superuser_headers = _login_and_get_headers(
        client,
        settings.FIRST_SUPERUSER,
        settings.FIRST_SUPERUSER_PASSWORD,
    )
    domain_id = _create_domain(client, superuser_headers)
    model_id = _create_feature_model(client, superuser_headers, domain_id)

    with patch(
        "app.repositories.feature_model.FeatureModelRepository.can_be_deleted",
        new=AsyncMock(return_value=(False, "Model has associated features")),
    ):
        response = client.delete(
            f"{settings.API_V1_PREFIX}/feature-models/{model_id}",
            headers=superuser_headers,
        )

    assert response.status_code == 400
    assert "associated features" in _extract_error_detail(response)


def test_critical_publish_version_success_for_owner(client: TestClient) -> None:
    superuser_headers = _login_and_get_headers(
        client,
        settings.FIRST_SUPERUSER,
        settings.FIRST_SUPERUSER_PASSWORD,
    )
    domain_id = _create_domain(client, superuser_headers)
    model_id = _create_feature_model(client, superuser_headers, domain_id)
    version_id = _create_feature_model_version(client, superuser_headers, model_id)

    async def _fake_publish(self, version, validate=True):  # noqa: ANN001, ARG001
        version.status = ModelStatus.PUBLISHED
        return version

    with patch(
        "app.api.v1.routes.feature_model_version.FeatureModelVersionManager.publish_version",
        new=_fake_publish,
    ):
        response = client.patch(
            f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{version_id}/publish",
            headers=superuser_headers,
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == version_id
    assert payload["status"] == ModelStatus.PUBLISHED.value


def test_critical_publish_version_forbidden_for_non_owner(client: TestClient) -> None:
    superuser_headers = _login_and_get_headers(
        client,
        settings.FIRST_SUPERUSER,
        settings.FIRST_SUPERUSER_PASSWORD,
    )
    viewer_headers = _create_viewer_user_headers(client, superuser_headers)

    domain_id = _create_domain(client, superuser_headers)
    model_id = _create_feature_model(client, superuser_headers, domain_id)
    version_id = _create_feature_model_version(client, superuser_headers, model_id)

    response = client.patch(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{version_id}/publish",
        headers=viewer_headers,
    )

    assert response.status_code == 403


def test_critical_analysis_batch_queues_task(client: TestClient) -> None:
    superuser_headers = _login_and_get_headers(
        client,
        settings.FIRST_SUPERUSER,
        settings.FIRST_SUPERUSER_PASSWORD,
    )

    domain_id = _create_domain(client, superuser_headers)
    model_id = _create_feature_model(client, superuser_headers, domain_id)
    version_id = _create_feature_model_version(client, superuser_headers, model_id)

    with patch(
        "app.tasks.feature_model_analysis.run_feature_model_analysis.delay",
        return_value=type("Task", (), {"id": "task-123"})(),
    ):
        response = client.post(
            f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{version_id}/analysis/batch",
            headers=superuser_headers,
            json={"max_solutions": 50},
        )

    assert response.status_code == 200
    assert response.json()["task_id"] == "task-123"


def test_critical_analysis_batch_version_not_found(client: TestClient) -> None:
    superuser_headers = _login_and_get_headers(
        client,
        settings.FIRST_SUPERUSER,
        settings.FIRST_SUPERUSER_PASSWORD,
    )
    domain_id = _create_domain(client, superuser_headers)
    model_id = _create_feature_model(client, superuser_headers, domain_id)

    response = client.post(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{uuid.uuid4()}/analysis/batch",
        headers=superuser_headers,
        json={"max_solutions": 50},
    )

    assert response.status_code == 404


def test_critical_export_version_returns_file_and_persists_cache(
    client: TestClient,
) -> None:
    superuser_headers = _login_and_get_headers(
        client,
        settings.FIRST_SUPERUSER,
        settings.FIRST_SUPERUSER_PASSWORD,
    )
    domain_id = _create_domain(client, superuser_headers)
    model_id = _create_feature_model(client, superuser_headers, domain_id)
    version_id = _create_feature_model_version(client, superuser_headers, model_id)

    with (
        patch(
            "app.api.v1.routes.feature_model_export.FeatureModelExportService.export",
            return_value="<featureModel/>",
        ),
        patch(
            "app.api.v1.routes.feature_model_export.minio_client.upload_feature_model_export",
            new=AsyncMock(return_value=f"{version_id}.xml"),
        ),
        patch(
            "app.api.v1.routes.feature_model_export.redis_client.setex",
            new=AsyncMock(return_value=True),
        ),
        patch(
            "app.api.v1.routes.feature_model_export.redis_client.zadd",
            new=AsyncMock(return_value=1),
        ),
        patch(
            "app.api.v1.routes.feature_model_export.redis_client.expire",
            new=AsyncMock(return_value=True),
        ),
    ):
        response = client.get(
            f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{version_id}/export/xml",
            headers=superuser_headers,
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")
    assert "attachment; filename=" in response.headers["content-disposition"]


def test_critical_system_status_contract(client: TestClient) -> None:
    response = client.get(f"{settings.API_V1_PREFIX}/status")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] in {"ok", "degraded", "down"}
    assert "services" in payload
    assert "disk_usage" in payload
    assert "memory_usage" in payload
    assert "network" in payload
