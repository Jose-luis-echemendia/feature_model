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


def test_feature_model_analysis_summary(
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
    new_version_id = apply_response.json()["version_id"]

    response = client.post(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{new_version_id}/analysis/summary",
        headers=superuser_token_headers,
        json={},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "satisfiable" in payload
    assert "dead_features" in payload
    assert "core_features" in payload
    assert "commonality" in payload
    assert "atomic_sets" in payload
