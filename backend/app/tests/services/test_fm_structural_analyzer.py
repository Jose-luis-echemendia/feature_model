from app.enums import AnalysisType
from app.services.feature_model.fm_structural_analyzer import (
    FeatureModelStructuralAnalyzer,
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


def test_detect_dead_features_returns_empty():
    features, relations, constraints = _simple_model()
    analyzer = FeatureModelStructuralAnalyzer()

    dead = analyzer.detect_dead_features(features, relations, constraints)

    assert dead == []


def test_calculate_complexity_metrics_basic():
    features, relations, constraints = _simple_model()
    analyzer = FeatureModelStructuralAnalyzer()

    results = analyzer.analyze_feature_model(
        features,
        relations,
        constraints,
        analysis_types=[AnalysisType.COMPLEXITY_METRICS],
    )

    metrics = results[AnalysisType.COMPLEXITY_METRICS].metrics
    assert metrics["total_features"] == 3
    assert metrics["leaf_features"] == 2
