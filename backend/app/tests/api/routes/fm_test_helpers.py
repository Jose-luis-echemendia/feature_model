from fastapi.testclient import TestClient

from app.core.config import settings
from app.tests.utils.utils import random_lower_string


def create_domain(client: TestClient, headers: dict[str, str]) -> str:
    payload = {
        "name": f"domain-{random_lower_string()}",
        "description": "fm test domain",
    }
    response = client.post(
        f"{settings.API_V1_PREFIX}/domains/",
        headers=headers,
        json=payload,
    )
    assert 200 <= response.status_code < 300
    return response.json()["id"]


def create_feature_model(
    client: TestClient,
    headers: dict[str, str],
    domain_id: str | None = None,
) -> str:
    if domain_id is None:
        domain_id = create_domain(client, headers)

    payload = {
        "name": f"model-{random_lower_string()}",
        "description": "fm test model",
        "domain_id": domain_id,
    }
    response = client.post(
        f"{settings.API_V1_PREFIX}/feature-models/",
        headers=headers,
        json=payload,
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_feature_model_version(
    client: TestClient,
    headers: dict[str, str],
    model_id: str,
) -> str:
    response = client.post(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions",
        headers=headers,
        json={},
    )
    assert response.status_code == 200
    return response.json()["id"]


def sample_uvl() -> str:
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
