import uuid

from fastapi.testclient import TestClient

from app.core.config import settings


def test_feature_model_complete_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_PREFIX}/feature-models/{uuid.uuid4()}/versions/{uuid.uuid4()}/complete",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_feature_model_complete_latest_no_published(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_PREFIX}/feature-models/{uuid.uuid4()}/versions/latest/complete",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
