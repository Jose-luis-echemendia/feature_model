import pytest

from app.exceptions import InvalidConfigurationException
from app.services.feature_model.fm_logical_validator import (
    FeatureModelLogicalValidator,
)


def _simple_model_requires() -> tuple[list[dict], list[dict], list[dict]]:
    features = [
        {"id": "root", "name": "Root", "parent_id": None},
        {"id": "A", "name": "A", "parent_id": "root"},
        {"id": "B", "name": "B", "parent_id": "root"},
    ]
    relations = [
        {"parent_id": "root", "child_id": "A", "relation_type": "mandatory"},
        {"parent_id": "root", "child_id": "B", "relation_type": "optional"},
    ]
    constraints = [{"expr_text": "A REQUIRES B"}]
    return features, relations, constraints


def _simple_model_excludes() -> tuple[list[dict], list[dict], list[dict]]:
    features = [
        {"id": "root", "name": "Root", "parent_id": None},
        {"id": "A", "name": "A", "parent_id": "root"},
        {"id": "B", "name": "B", "parent_id": "root"},
    ]
    relations = [
        {"parent_id": "root", "child_id": "A", "relation_type": "mandatory"},
        {"parent_id": "root", "child_id": "B", "relation_type": "optional"},
    ]
    constraints = [{"expr_text": "A EXCLUDES B"}]
    return features, relations, constraints


def test_validate_feature_model_satisfiable():
    features, relations, constraints = _simple_model_requires()
    validator = FeatureModelLogicalValidator()

    result = validator.validate_feature_model(features, relations, constraints)

    assert result.is_valid is True
    assert result.errors == []


def test_validate_configuration_raises_on_excludes():
    features, relations, constraints = _simple_model_excludes()
    validator = FeatureModelLogicalValidator()

    with pytest.raises(InvalidConfigurationException):
        validator.validate_configuration(
            features,
            relations,
            constraints,
            selected_features=["root", "A", "B"],
        )
