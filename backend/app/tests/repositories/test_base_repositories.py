import uuid

import pytest

from app.models.domain import Domain
from app.models.feature_model import FeatureModel
from app.repositories.base import BaseDomainRepository, BaseFeatureModelRepository


class _DomainRepo(BaseDomainRepository):
    pass


class _FeatureModelRepo(BaseFeatureModelRepository):
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
