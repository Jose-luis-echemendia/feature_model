import uuid

from fastapi.testclient import TestClient

from app.core.config import settings
from app.tests.utils.utils import random_lower_string


def _create_domain(client: TestClient, headers: dict[str, str]) -> str:
    data = {"name": f"domain-{random_lower_string()}", "description": "test"}
    response = client.post(
        f"{settings.API_V1_PREFIX}/domains/",
        headers=headers,
        json=data,
    )
    assert 200 <= response.status_code < 300
    return response.json()["id"]


def _create_feature_model(
    client: TestClient, headers: dict[str, str], domain_id: str
) -> str:
    payload = {
        "name": f"model-{random_lower_string()}",
        "description": "test model",
        "domain_id": domain_id,
    }
    response = client.post(
        f"{settings.API_V1_PREFIX}/feature-models/",
        headers=headers,
        json=payload,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_feature_model_statistics_latest_no_published(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    domain_id = _create_domain(client, superuser_token_headers)
    model_id = _create_feature_model(client, superuser_token_headers, domain_id)

    response = client.get(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/latest/statistics",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_feature_model_statistics_version_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    domain_id = _create_domain(client, superuser_token_headers)
    model_id = _create_feature_model(client, superuser_token_headers, domain_id)

    response = client.get(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{uuid.uuid4()}/statistics",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_feature_model_statistics_model_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_PREFIX}/feature-models/{uuid.uuid4()}/versions/{uuid.uuid4()}/statistics",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
