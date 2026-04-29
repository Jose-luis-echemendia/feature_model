import uuid

import pytest

from app.enums import FeatureType, ModelStatus
from app.exceptions import InvalidVersionStateException
from app.models import Feature, FeatureModel, FeatureModelVersion
from app.models.domain import Domain
from app.services.feature_model.fm_version_manager import FeatureModelVersionManager


class _DummySession:
    def __init__(self) -> None:
        self.commits = 0
        self.refreshes = 0
        self.added = None

    async def commit(self) -> None:
        self.commits += 1

    async def refresh(self, _obj) -> None:  # noqa: ANN001
        self.refreshes += 1

    def add(self, obj) -> None:  # simple stub to emulate AsyncSession.add
        self.added = obj


def _build_feature_model() -> FeatureModel:
    domain = Domain(name="Educativo")
    feature_model = FeatureModel(
        name="My Model",
        description="Desc",
        domain_id=uuid.uuid4(),
        owner_id=uuid.uuid4(),
    )
    feature_model.domain = domain
    feature_model.versions = []
    return feature_model


def _build_version(feature_model: FeatureModel, number: int) -> FeatureModelVersion:
    version = FeatureModelVersion(
        feature_model_id=feature_model.id,
        version_number=number,
        status=ModelStatus.DRAFT,
    )
    version.features = [
        Feature(
            name="Root",
            type=FeatureType.MANDATORY,
            feature_model_version_id=version.id,
            parent_id=None,
        )
    ]
    version.feature_relations = []
    version.constraints = []
    version.feature_groups = []
    return version


@pytest.mark.asyncio
async def test_publish_version_sets_status_and_snapshot(monkeypatch):
    feature_model = _build_feature_model()
    session = _DummySession()
    manager = FeatureModelVersionManager(session, feature_model)
    version = _build_version(feature_model, 1)

    async def _fake_snapshot(_version):  # noqa: ANN001
        return {"snapshot": True}

    monkeypatch.setattr(manager, "_build_snapshot", _fake_snapshot)

    published = await manager.publish_version(version, validate=False)

    assert published.status == ModelStatus.PUBLISHED
    assert published.snapshot == {"snapshot": True}
    assert session.commits == 1


@pytest.mark.asyncio
async def test_archive_and_restore_transitions():
    feature_model = _build_feature_model()
    session = _DummySession()
    manager = FeatureModelVersionManager(session, feature_model)
    version = _build_version(feature_model, 1)
    version.status = ModelStatus.PUBLISHED

    archived = await manager.archive_version(version)
    assert archived.status == ModelStatus.ARCHIVED

    restored = await manager.restore_version(version)
    assert restored.status == ModelStatus.PUBLISHED


@pytest.mark.asyncio
async def test_archive_invalid_state_raises():
    feature_model = _build_feature_model()
    session = _DummySession()
    manager = FeatureModelVersionManager(session, feature_model)
    version = _build_version(feature_model, 1)

    with pytest.raises(InvalidVersionStateException):
        await manager.archive_version(version)


@pytest.mark.asyncio
async def test_get_latest_version_filters_by_status():
    feature_model = _build_feature_model()
    session = _DummySession()
    manager = FeatureModelVersionManager(session, feature_model)

    v1 = _build_version(feature_model, 1)
    v1.status = ModelStatus.DRAFT
    v2 = _build_version(feature_model, 2)
    v2.status = ModelStatus.PUBLISHED
    v3 = _build_version(feature_model, 3)
    v3.status = ModelStatus.PUBLISHED

    feature_model.versions = [v1, v2, v3]

    latest_published = await manager.get_latest_version(status=ModelStatus.PUBLISHED)
    assert latest_published is v3


@pytest.mark.asyncio
async def test_create_new_version_increments_and_persists(monkeypatch):
    feature_model = _build_feature_model()
    session = _DummySession()
    manager = FeatureModelVersionManager(session, feature_model)

    async def _fake_get_latest_version_number(_fm_id):  # noqa: ANN001
        return 3

    # Patch the repository method
    monkeypatch.setattr(
        manager.repository, "get_latest_version_number", _fake_get_latest_version_number
    )

    new_version = await manager.create_new_version(source_version=None)

    assert new_version.version_number == 4
    assert new_version.status == ModelStatus.DRAFT
    assert session.commits == 1
    assert session.refreshes == 1
    assert session.added is not None
