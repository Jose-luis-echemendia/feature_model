from app.enums import GenerationStrategy
from app.services.feature_model.fm_configuration_generator import (
    FeatureModelConfigurationGenerator,
)


def _simple_model() -> tuple[list[dict], list[dict], list[dict]]:
    features = [
        {"id": "root", "name": "Root", "parent_id": None},
        {"id": "A", "name": "A", "parent_id": "root"},
        {"id": "B", "name": "B", "parent_id": "root"},
    ]
    relations = [
        {"parent_id": "root", "child_id": "A", "relation_type": "mandatory"},
        {"parent_id": "root", "child_id": "B", "relation_type": "optional"},
    ]
    constraints: list[dict] = []
    return features, relations, constraints


def test_generate_valid_configuration_greedy_includes_mandatory():
    features, relations, constraints = _simple_model()
    generator = FeatureModelConfigurationGenerator()

    result = generator.generate_valid_configuration(
        features,
        relations,
        constraints,
        strategy=GenerationStrategy.GREEDY,
    )

    assert result.success is True
    assert result.configuration.get("root") is True
    assert result.configuration.get("A") is True
