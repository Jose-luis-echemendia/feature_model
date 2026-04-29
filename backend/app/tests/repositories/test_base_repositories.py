import uuid
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from app.models.domain import Domain
from app.models.feature_model import FeatureModel
from app.repositories.base import (
    BaseConstraintRepository,
    BaseDomainRepository,
    BaseFeatureGroupRepository,
    BaseFeatureModelRepository,
    BaseFeatureRelationRepository,
    BaseFeatureRepository,
    BaseUserRepository,
)


class _DomainRepo(BaseDomainRepository):
    pass


class _FeatureModelRepo(BaseFeatureModelRepository):
    pass


class _UserRepo(BaseUserRepository):
    pass


class _FeatureRepo(BaseFeatureRepository):
    pass


class _FeatureRelationRepo(BaseFeatureRelationRepository):
    pass


class _FeatureGroupRepo(BaseFeatureGroupRepository):
    pass


class _ConstraintRepo(BaseConstraintRepository):
    pass


def test_base_domain_validate_name_unique_raises() -> None:
    repo = _DomainRepo()
    existing = Domain(name="Domain", description="test")
    with pytest.raises(ValueError):
        repo.validate_name_unique(existing)


def test_base_domain_validate_name_unique_allows_same_id() -> None:
    repo = _DomainRepo()
    domain_id = uuid.uuid4()
    existing = Domain(id=domain_id, name="Domain", description="test")
    repo.validate_name_unique(existing, current_domain_id=domain_id)


def test_base_feature_model_validate_name_unique_in_domain() -> None:
    repo = _FeatureModelRepo()
    existing = FeatureModel(
        name="Model",
        description="test",
        domain_id=uuid.uuid4(),
        owner_id=uuid.uuid4(),
    )
    with pytest.raises(ValueError):
        repo.validate_name_unique_in_domain(existing, name="Model")


def test_base_feature_model_validate_name_unique_in_domain_allows_same_id() -> None:
    repo = _FeatureModelRepo()
    model_id = uuid.uuid4()
    existing = FeatureModel(
        id=model_id,
        name="Model",
        description="test",
        domain_id=uuid.uuid4(),
        owner_id=uuid.uuid4(),
    )
    repo.validate_name_unique_in_domain(
        existing, current_model_id=model_id, name="Model"
    )


def test_base_user_validate_email_unique_raises() -> None:
    repo = _UserRepo()
    with pytest.raises(ValueError):
        repo.validate_email_unique(existing_user=object())


def test_base_user_prepare_password_uses_hash_helper() -> None:
    repo = _UserRepo()
    with patch("app.core.security.get_password_hash", return_value="hashed") as mocked:
        result = repo.prepare_password("plain")
    mocked.assert_called_once_with("plain")
    assert result == "hashed"


def test_base_user_set_active_status_changes_flag() -> None:
    repo = _UserRepo()
    user = SimpleNamespace(is_active=True)
    repo._set_active_status(user, False)
    assert user.is_active is False


def test_base_feature_validate_parent_not_self_raises() -> None:
    repo = _FeatureRepo()
    feature_id = uuid.uuid4()
    with pytest.raises(ValueError):
        repo.validate_parent_not_self(feature_id, feature_id)


def test_base_feature_build_feature_tree_groups_children(monkeypatch) -> None:
    repo = _FeatureRepo()
    root_id = uuid.uuid4()
    child_id = uuid.uuid4()

    class _PublicFeature:
        def __init__(self, feat_id, parent_id):
            self.id = feat_id
            self.parent_id = parent_id
            self.children = []

    from app.models import FeaturePublicWithChildren

    monkeypatch.setattr(
        FeaturePublicWithChildren,
        "model_validate",
        staticmethod(lambda feature: _PublicFeature(feature.id, feature.parent_id)),
    )

    features = [
        SimpleNamespace(id=root_id, parent_id=None),
        SimpleNamespace(id=child_id, parent_id=root_id),
    ]

    roots = repo.build_feature_tree(features)
    assert len(roots) == 1
    assert roots[0].id == root_id
    assert len(roots[0].children) == 1
    assert roots[0].children[0].id == child_id


def test_base_feature_relation_validate_features_exist_raises() -> None:
    repo = _FeatureRelationRepo()
    with pytest.raises(ValueError):
        repo.validate_features_exist(source_feature=None, target_feature=object())


def test_base_feature_relation_validate_same_version_raises() -> None:
    repo = _FeatureRelationRepo()
    source = SimpleNamespace(feature_model_version_id=uuid.uuid4())
    target = SimpleNamespace(feature_model_version_id=uuid.uuid4())
    with pytest.raises(ValueError):
        repo.validate_same_version(source, target)


def test_base_feature_group_validate_parent_exists_raises() -> None:
    repo = _FeatureGroupRepo()
    with pytest.raises(ValueError):
        repo.validate_parent_feature_exists(parent_feature=None)


def test_base_constraint_validate_version_exists_raises() -> None:
    repo = _ConstraintRepo()
    with pytest.raises(ValueError):
        repo.validate_feature_model_version_exists(version=None)
