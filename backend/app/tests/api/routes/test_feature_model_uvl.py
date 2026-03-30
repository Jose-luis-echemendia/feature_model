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


def _create_feature_model(client: TestClient, headers: dict[str, str]) -> str:
    domain_id = _create_domain(client, headers)
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


def _sample_uvl() -> str:
    return """namespace TestModel

features
    Root
        mandatory
            A
        optional
            B

constraints
    A => B
"""


def test_feature_model_uvl_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    model_id = uuid.uuid4()
    version_id = uuid.uuid4()

    response = client.get(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{version_id}/uvl",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404

    response = client.put(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{version_id}/uvl",
        headers=superuser_token_headers,
        json={"uvl_content": "features"},
    )
    assert response.status_code == 404

    response = client.post(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{version_id}/uvl/sync-from-structure",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_feature_model_uvl_diff(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    model_id = _create_feature_model(client, superuser_token_headers)
    version_id = _create_feature_model_version(
        client, superuser_token_headers, model_id
    )

    response = client.post(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{version_id}/uvl/diff",
        headers=superuser_token_headers,
        json={"uvl_content": _sample_uvl()},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "root" in payload["features_added"]
    assert "a" in payload["features_added"]
    assert "b" in payload["features_added"]
    assert ["a", "b", "requires"] in payload["relations_added"]


def test_feature_model_uvl_apply_and_diff_empty(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    model_id = _create_feature_model(client, superuser_token_headers)
    version_id = _create_feature_model_version(
        client, superuser_token_headers, model_id
    )

    apply_response = client.post(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{version_id}/uvl/apply-to-structure",
        headers=superuser_token_headers,
        json={"uvl_content": _sample_uvl()},
    )

    assert apply_response.status_code == 201
    applied = apply_response.json()
    assert applied["source"] == "applied"
    new_version_id = applied["version_id"]

    diff_response = client.post(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{new_version_id}/uvl/diff",
        headers=superuser_token_headers,
        json={"uvl_content": _sample_uvl()},
    )

    assert diff_response.status_code == 200
    diff_payload = diff_response.json()
    assert diff_payload["features_added"] == []
    assert diff_payload["features_removed"] == []
    assert diff_payload["relations_added"] == []
    assert diff_payload["relations_removed"] == []
