from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.enums import ModelStatus
from app.tests.api.routes.fm_test_helpers import (
    create_feature_model,
    create_feature_model_version,
)


def _analysis_summary_namespace() -> SimpleNamespace:
    return SimpleNamespace(
        satisfiable=True,
        errors=[],
        warnings=[],
        dead_features=[],
        core_features=["root"],
        commonality={"root": 1.0},
        atomic_sets=[[]],
        estimated_configurations=1,
        truncated=False,
        complexity_metrics={"nodes": 1},
        uvl_validation={"valid": True},
        flamapy_engine_used=False,
    )


def test_fm_services_versions_list_and_read(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    model_id = create_feature_model(client, superuser_token_headers)
    version_id = create_feature_model_version(
        client,
        superuser_token_headers,
        model_id,
    )

    list_response = client.get(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions",
        headers=superuser_token_headers,
    )
    assert list_response.status_code == 200
    version_ids = [item["id"] for item in list_response.json()]
    assert version_id in version_ids

    read_response = client.get(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{version_id}",
        headers=superuser_token_headers,
    )
    assert read_response.status_code == 200
    assert read_response.json()["id"] == version_id


def test_fm_services_archive_and_restore_version(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    model_id = create_feature_model(client, superuser_token_headers)
    version_id = create_feature_model_version(
        client,
        superuser_token_headers,
        model_id,
    )

    async def _fake_archive(self, version):  # noqa: ANN001
        version.status = ModelStatus.ARCHIVED
        return version

    async def _fake_restore(self, version):  # noqa: ANN001
        version.status = ModelStatus.PUBLISHED
        return version

    with patch(
        "app.api.v1.routes.feature_model_version.FeatureModelVersionManager.archive_version",
        new=_fake_archive,
    ):
        archive_response = client.patch(
            f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{version_id}/archive",
            headers=superuser_token_headers,
        )
    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == ModelStatus.ARCHIVED.value

    with patch(
        "app.api.v1.routes.feature_model_version.FeatureModelVersionManager.restore_version",
        new=_fake_restore,
    ):
        restore_response = client.patch(
            f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{version_id}/restore",
            headers=superuser_token_headers,
        )
    assert restore_response.status_code == 200
    assert restore_response.json()["status"] == ModelStatus.PUBLISHED.value


def test_fm_services_analysis_compare_and_task_status(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    model_id = create_feature_model(client, superuser_token_headers)
    base_version_id = create_feature_model_version(
        client,
        superuser_token_headers,
        model_id,
    )
    target_version_id = create_feature_model_version(
        client,
        superuser_token_headers,
        model_id,
    )

    with patch(
        "app.api.v1.routes.feature_model_analysis.compare_versions",
        return_value={
            "base": _analysis_summary_namespace(),
            "target": _analysis_summary_namespace(),
            "delta": {"estimated_configurations": 0},
        },
    ):
        compare_response = client.post(
            f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{base_version_id}/analysis/compare",
            headers=superuser_token_headers,
            json={"target_version_id": target_version_id, "max_solutions": 10},
        )

    assert compare_response.status_code == 200
    compare_payload = compare_response.json()
    assert "base" in compare_payload
    assert "target" in compare_payload
    assert "delta" in compare_payload

    fake_result = SimpleNamespace(
        status="SUCCESS",
        successful=lambda: True,
        failed=lambda: False,
        result={"ok": True},
    )
    with patch(
        "app.core.celery.celery_app.AsyncResult",
        return_value=fake_result,
    ):
        status_response = client.get(
            f"{settings.API_V1_PREFIX}/feature-models/analysis/tasks/task-123",
            headers=superuser_token_headers,
        )

    assert status_response.status_code == 200
    assert status_response.json()["status"] == "SUCCESS"
    assert status_response.json()["result"] == {"ok": True}


def test_fm_services_uvl_get_generated_and_save(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    model_id = create_feature_model(client, superuser_token_headers)
    version_id = create_feature_model_version(
        client,
        superuser_token_headers,
        model_id,
    )

    with patch(
        "app.api.v1.routes.feature_model_uvl.FeatureModelExportService.export_to_uvl",
        return_value="features\n  Root",
    ):
        get_response = client.get(
            f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{version_id}/uvl",
            headers=superuser_token_headers,
        )

    assert get_response.status_code == 200
    assert get_response.json()["source"] == "generated"

    fake_task = SimpleNamespace(id="task-uvl-1")
    with (
        patch(
            "app.api.v1.routes.feature_model_uvl.FeatureModelUVLImporter.validate_uvl_only",
            return_value=None,
        ),
        patch(
            "app.api.v1.routes.feature_model_uvl.run_feature_model_analysis.delay",
            return_value=fake_task,
        ),
    ):
        save_response = client.put(
            f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions/{version_id}/uvl",
            headers=superuser_token_headers,
            json={"uvl_content": "features\n  Root"},
        )

    assert save_response.status_code == 200
    save_payload = save_response.json()
    assert save_payload["source"] == "stored"
    assert save_payload["analysis_task_id"] == "task-uvl-1"


def test_fm_services_create_version_with_invalid_source_returns_404(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    model_id = create_feature_model(client, superuser_token_headers)

    response = client.post(
        f"{settings.API_V1_PREFIX}/feature-models/{model_id}/versions",
        headers=superuser_token_headers,
        json={"source_version_id": "00000000-0000-0000-0000-000000000000"},
    )

    assert response.status_code == 404
