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


def test_feature_model_crud(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    domain_id = _create_domain(client, superuser_token_headers)
    model_name = f"model-{random_lower_string()}"

    create_payload = {
        "name": model_name,
        "description": "test model",
        "domain_id": domain_id,
    }
    create_response = client.post(
        f"{settings.API_V1_PREFIX}/feature-models/",
        headers=superuser_token_headers,
        json=create_payload,
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == model_name
    model_id = created["id"]

    list_response = client.get(
        f"{settings.API_V1_PREFIX}/feature-models/",
        headers=superuser_token_headers,
    )
    assert list_response.status_code == 200
    data = list_response.json()
    assert any(item["id"] == model_id for item in data["data"])

    detail_response = client.get(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}",
        headers=superuser_token_headers,
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == model_id

    update_payload = {"name": f"{model_name}-updated"}
    update_response = client.patch(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}",
        headers=superuser_token_headers,
        json=update_payload,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"].endswith("-updated")

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

    delete_response = client.delete(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}",
        headers=superuser_token_headers,
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Feature Model deleted successfully."


def test_feature_model_create_invalid_domain(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    payload = {
        "name": f"model-{random_lower_string()}",
        "description": "test model",
        "domain_id": "00000000-0000-0000-0000-000000000000",
    }
    response = client.post(
        f"{settings.API_V1_PREFIX}/feature-models/",
        headers=superuser_token_headers,
        json=payload,
    )
    assert response.status_code == 404
