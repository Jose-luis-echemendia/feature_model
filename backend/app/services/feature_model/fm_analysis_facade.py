"""
Facade de análisis para Feature Models.

Provee operaciones de alto nivel combinando:
- Validación lógica (SAT/SMT)
- Análisis estructural
- Enumeración parcial de configuraciones para core/commonality/atomic
- Integración opcional con Flamapy (Python) para validar UVL
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import tempfile
import importlib

from app.enums import AnalysisType
from app.services.feature_model import (
    FeatureModelLogicalValidator,
    FeatureModelStructuralAnalyzer,
)
from app.services.feature_model.fm_uvl_importer import FeatureModelUVLImporter


@dataclass
class AnalysisSummary:
    satisfiable: bool
    errors: List[str]
    warnings: List[str]
    dead_features: List[str]
    core_features: List[str]
    commonality: Dict[str, float]
    atomic_sets: List[List[str]]
    estimated_configurations: int
    truncated: bool
    complexity_metrics: Dict[str, Any]
    uvl_validation: Optional[Dict[str, Any]] = None
    flamapy_engine_used: bool = False


def _build_payload(
    version,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    features_payload: list[dict[str, Any]] = []
    relations_payload: list[dict[str, Any]] = []
    constraints_payload: list[dict[str, Any]] = []

    for feature in version.features:
        group_data = None
        if feature.group:
            group_data = {
                "group_type": (
                    feature.group.group_type.value
                    if hasattr(feature.group.group_type, "value")
                    else str(feature.group.group_type)
                ),
                "min_cardinality": feature.group.min_cardinality,
                "max_cardinality": feature.group.max_cardinality,
            }

        features_payload.append(
            {
                "id": str(feature.id),
                "name": feature.name,
                "type": (
                    feature.type.value
                    if hasattr(feature.type, "value")
                    else str(feature.type)
                ),
                "parent_id": str(feature.parent_id) if feature.parent_id else None,
                "group_id": str(feature.group_id) if feature.group_id else None,
                "group": group_data,
            }
        )

        if feature.parent_id:
            relation_type = (
                "mandatory"
                if (
                    feature.type.value
                    if hasattr(feature.type, "value")
                    else str(feature.type)
                )
                == "mandatory"
                else "optional"
            )
            relations_payload.append(
                {
                    "parent_id": str(feature.parent_id),
                    "child_id": str(feature.id),
                    "relation_type": relation_type,
                    "group_id": str(feature.group_id) if feature.group_id else None,
                    "group_type": (
                        group_data.get("group_type") if group_data else None
                    ),
                    "min_cardinality": (
                        group_data.get("min_cardinality") if group_data else None
                    ),
                    "max_cardinality": (
                        group_data.get("max_cardinality") if group_data else None
                    ),
                }
            )

    for constraint in version.constraints:
        constraints_payload.append(
            {
                "id": str(constraint.id),
                "expr_text": constraint.expr_text,
                "expr_cnf": constraint.expr_cnf,
            }
        )

    for relation in version.feature_relations:
        relation_type = (
            relation.type.value
            if hasattr(relation.type, "value")
            else str(relation.type)
        )
        if relation_type == "requires":
            expr = f"{relation.source_feature_id} REQUIRES {relation.target_feature_id}"
        elif relation_type == "excludes":
            expr = f"{relation.source_feature_id} EXCLUDES {relation.target_feature_id}"
        else:
            continue

        constraints_payload.append(
            {
                "id": str(relation.id),
                "expr_text": expr,
                "expr_cnf": None,
            }
        )

    return features_payload, relations_payload, constraints_payload


def _run_flamapy_satisfiable(uvl_content: str) -> Optional[bool]:
    """Validación con Flamapy (API Python) usando el modelo UVL."""
    module_candidates = [
        "flamapy.interfaces.python.flama_feature_model",
        "flamapy.interfaces.python.flamapy_feature_model",
    ]
    FLAMAFeatureModel = None
    for module_name in module_candidates:
        try:
            module = importlib.import_module(module_name)
            FLAMAFeatureModel = getattr(module, "FLAMAFeatureModel", None)
            if FLAMAFeatureModel:
                break
        except Exception:
            continue
    if FLAMAFeatureModel is None:
        return None

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = f"{tmp_dir}/model.uvl"
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(uvl_content)

            fm = FLAMAFeatureModel(path)
            return bool(fm.valid())
    except Exception:
        return None


def _compute_commonality(
    configs: List[List[str]], feature_ids: List[str]
) -> Dict[str, float]:
    total = len(configs)
    if total == 0:
        return {fid: 0.0 for fid in feature_ids}

    counts = {fid: 0 for fid in feature_ids}
    for config in configs:
        for fid in config:
            if fid in counts:
                counts[fid] += 1

    return {fid: counts[fid] / total for fid in feature_ids}


def _compute_atomic_sets(
    configs: List[List[str]], feature_ids: List[str]
) -> List[List[str]]:
    if not configs:
        return []

    vectors: Dict[tuple[bool, ...], List[str]] = {}
    config_sets = [set(cfg) for cfg in configs]

    for fid in feature_ids:
        vector = tuple(fid in cfg for cfg in config_sets)
        vectors.setdefault(vector, []).append(fid)

    return [group for group in vectors.values() if len(group) > 1]


def analyze_version(
    *,
    version,
    analysis_types: Optional[List[AnalysisType]] = None,
    max_solutions: int = 100,
    include_uvl_validation: bool = True,
) -> AnalysisSummary:
    features_payload, relations_payload, constraints_payload = _build_payload(version)

    validator = FeatureModelLogicalValidator()
    analyzer = FeatureModelStructuralAnalyzer()

    logical_result = validator.validate_feature_model(
        features=features_payload,
        relations=relations_payload,
        constraints=constraints_payload,
    )

    structural_results = analyzer.analyze_feature_model(
        features=features_payload,
        relations=relations_payload,
        constraints=constraints_payload,
        analysis_types=analysis_types,
    )

    dead_features = []
    complexity_metrics: Dict[str, Any] = {}
    for analysis_type, result in structural_results.items():
        if analysis_type == AnalysisType.DEAD_FEATURES:
            dead_features = [
                issue.feature_id for issue in result.issues if issue.feature_id
            ]
        if analysis_type == AnalysisType.COMPLEXITY_METRICS:
            complexity_metrics = result.metrics or {}

    configs: List[List[str]] = []
    truncated = False
    try:
        configs = validator.enumerate_configurations(
            features=features_payload,
            relations=relations_payload,
            constraints=constraints_payload,
            max_solutions=max_solutions,
        )
        truncated = len(configs) >= max_solutions
    except Exception:
        configs = []
        truncated = True

    feature_ids = [str(f["id"]) for f in features_payload]
    commonality = _compute_commonality(configs, feature_ids)
    core_features = [fid for fid, ratio in commonality.items() if ratio == 1.0]
    atomic_sets = _compute_atomic_sets(configs, feature_ids)

    uvl_validation: Optional[Dict[str, Any]] = None
    flamapy_engine_used = False
    if include_uvl_validation and version.uvl_content:
        try:
            uvl_validation = FeatureModelUVLImporter.validate_uvl_only(
                version.uvl_content
            )
        except Exception as exc:
            uvl_validation = {"is_valid": False, "errors": [str(exc)]}

        flamapy_satisfiable = _run_flamapy_satisfiable(version.uvl_content)
        if flamapy_satisfiable is not None:
            flamapy_engine_used = True
            uvl_validation = uvl_validation or {}
            uvl_validation["flamapy_satisfiable"] = flamapy_satisfiable

    return AnalysisSummary(
        satisfiable=logical_result.is_valid,
        errors=logical_result.errors,
        warnings=logical_result.warnings,
        dead_features=dead_features,
        core_features=core_features,
        commonality=commonality,
        atomic_sets=atomic_sets,
        estimated_configurations=len(configs),
        truncated=truncated,
        complexity_metrics=complexity_metrics,
        uvl_validation=uvl_validation,
        flamapy_engine_used=flamapy_engine_used,
    )


def compare_versions(
    *,
    base_version,
    target_version,
    analysis_types: Optional[List[AnalysisType]] = None,
    max_solutions: int = 100,
) -> dict[str, Any]:
    base = analyze_version(
        version=base_version,
        analysis_types=analysis_types,
        max_solutions=max_solutions,
        include_uvl_validation=False,
    )
    target = analyze_version(
        version=target_version,
        analysis_types=analysis_types,
        max_solutions=max_solutions,
        include_uvl_validation=False,
    )

    base_dead = set(base.dead_features)
    target_dead = set(target.dead_features)
    base_core = set(base.core_features)
    target_core = set(target.core_features)

    return {
        "base": base,
        "target": target,
        "delta": {
            "dead_features_added": sorted(target_dead - base_dead),
            "dead_features_removed": sorted(base_dead - target_dead),
            "core_features_added": sorted(target_core - base_core),
            "core_features_removed": sorted(base_core - target_core),
            "configurations_delta": target.estimated_configurations
            - base.estimated_configurations,
        },
    }
