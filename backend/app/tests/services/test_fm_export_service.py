import uuid

from app.enums import FeatureType, ModelStatus
from app.models import Feature, FeatureModel, FeatureModelVersion
from app.models.domain import Domain
from app.services.feature_model.fm_export import FeatureModelExportService


def _build_simple_version() -> FeatureModelVersion:
    domain = Domain(name="Educativo")
    feature_model = FeatureModel(
        name="My Model",
        description="Desc",
        domain_id=uuid.uuid4(),
        owner_id=uuid.uuid4(),
    )
    feature_model.domain = domain

    version = FeatureModelVersion(
        feature_model_id=feature_model.id,
        version_number=1,
        status=ModelStatus.DRAFT,
    )
    version.feature_model = feature_model

    root = Feature(
        name="Root",
        type=FeatureType.MANDATORY,
        feature_model_version_id=version.id,
        parent_id=None,
    )
    child = Feature(
        name="Child",
        type=FeatureType.OPTIONAL,
        feature_model_version_id=version.id,
        parent_id=root.id,
    )

    version.features = [root, child]
    version.feature_relations = []
    version.constraints = []

    return version


def test_export_to_uvl_contains_root_and_optional_child():
    version = _build_simple_version()
    exporter = FeatureModelExportService(version)

    uvl = exporter.export_to_uvl()

    assert "namespace My_Model" in uvl
    assert "Root" in uvl
    assert "optional" in uvl
    assert "Child" in uvl
