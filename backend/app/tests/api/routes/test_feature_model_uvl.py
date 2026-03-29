import uuid

from fastapi.testclient import TestClient

from app.core.config import settings


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
