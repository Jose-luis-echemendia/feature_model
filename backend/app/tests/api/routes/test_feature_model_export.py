import uuid

from fastapi.testclient import TestClient

from app.core.config import settings
from app.tests.api.routes.fm_test_helpers import create_domain, create_feature_model


def test_feature_model_export_latest_no_published(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    domain_id = create_domain(client, superuser_token_headers)
    model_id = create_feature_model(client, superuser_token_headers, domain_id)

    response = client.get(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/latest/export/json",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_feature_model_export_version_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_PREFIX}/feature-models/{uuid.uuid4()}/versions/{uuid.uuid4()}/export/json",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
