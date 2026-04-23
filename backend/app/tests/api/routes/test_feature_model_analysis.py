from fastapi.testclient import TestClient

from app.core.config import settings
from app.tests.api.routes.fm_test_helpers import (
    create_feature_model,
    create_feature_model_version,
    sample_uvl,
)


def test_feature_model_analysis_summary(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    model_id = create_feature_model(client, superuser_token_headers)
    version_id = create_feature_model_version(client, superuser_token_headers, model_id)

    apply_response = client.post(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{version_id}/uvl/apply-to-structure",
        headers=superuser_token_headers,
        json={"uvl_content": sample_uvl()},
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
