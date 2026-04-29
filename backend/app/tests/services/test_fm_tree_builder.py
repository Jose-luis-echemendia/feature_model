import uuid

from app.enums import FeatureType, ModelStatus
from app.models import Feature, FeatureModel, FeatureModelVersion
from app.models.domain import Domain
from app.services.feature_model.fm_tree_builder import FeatureModelTreeBuilder


def _build_version_with_tree() -> FeatureModelVersion:
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
        uvl_content="namespace My_Model\n\nfeatures\n    Root",
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
    version.feature_groups = []
    version.configurations = []

    return version


def test_build_complete_response_tree_structure():
    version = _build_version_with_tree()
    builder = FeatureModelTreeBuilder(version)

    response = builder.build_complete_response()

    assert response.feature_model.name == "My Model"
    assert response.tree.name == "Root"
    assert len(response.tree.children) == 1
    assert response.tree.children[0].name == "Child"
    assert response.uvl.strip().startswith("namespace")
