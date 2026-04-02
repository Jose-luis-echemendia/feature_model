"""Endpoints explícitos de validación para Feature Models."""

import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.deps import (
    AsyncCurrentUser,
    AsyncFeatureModelVersionRepoDep,
    get_verified_user,
)
from app.enums import AnalysisType
from app.exceptions import (
    FeatureModelVersionNotFoundException,
    BusinessLogicException,
    ForbiddenException,
)
from app.services.feature_model import (
    FeatureModelLogicalValidator,
    FeatureModelStructuralAnalyzer,
)


router = APIRouter(
    prefix="/feature-models",
    tags=["validation"],
    dependencies=[Depends(get_verified_user)],
)


class ValidationIssue(BaseModel):
    issue_type: str
    severity: str
    feature_id: Optional[str] = None
    description: str
    recommendation: Optional[str] = None


class LogicalValidationResponse(BaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    satisfying_assignment: Optional[dict[str, bool]] = None


class StructureValidationResponse(BaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)


class ConfigurationValidationRequest(BaseModel):
    selected_features: list[uuid.UUID] = Field(
        default_factory=list,
        description="IDs de features seleccionadas en la configuración a validar.",
    )


class StructuralAnalysisRequest(BaseModel):
    analysis_types: Optional[list[AnalysisType]] = Field(
        default=None,
        description="Tipos de análisis a ejecutar. Si se omite, se ejecutan todos.",
    )


class StructuralAnalysisItem(BaseModel):
    analysis_type: AnalysisType
    issues: list[ValidationIssue] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)


class StructuralAnalysisResponse(BaseModel):
    is_valid: bool
    results: list[StructuralAnalysisItem] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class FullValidationResponse(BaseModel):
    logical: LogicalValidationResponse
    structure: StructureValidationResponse
    analysis: StructuralAnalysisResponse


async def _get_version_for_validation(
    *,
    model_id: uuid.UUID,
    version_id: uuid.UUID,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
):
    version = await version_repo.get_complete_with_relations(
        version_id=version_id,
        include_resources=False,
    )

    if not version:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

    if version.feature_model_id != model_id:
        raise BusinessLogicException(
            detail="Version does not belong to the specified feature model"
        )

    feature_model = version.feature_model
    if not feature_model.is_active:
        if feature_model.owner_id != current_user.id and not current_user.is_superuser:
            raise ForbiddenException(
                detail="This feature model is inactive and you don't have permission to validate it"
            )

    return version


def _build_validation_payload(
    version,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    features_payload: list[dict[str, Any]] = []
    relations_payload: list[dict[str, Any]] = []
    constraints_payload: list[dict[str, Any]] = []

    # Features + relaciones jerárquicas
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

    # Constraints explícitas
    for constraint in version.constraints:
        constraints_payload.append(
            {
                "id": str(constraint.id),
                "expr_text": constraint.expr_text,
                "expr_cnf": constraint.expr_cnf,
            }
        )

    # Relaciones cross-tree como constraints REQUIRES/EXCLUDES
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


@router.post(
    "/{model_id}/versions/{version_id}/validation/model",
    response_model=LogicalValidationResponse,
    summary="Validar consistencia lógica global del modelo",
    description=(
        "Valida la consistencia lógica y la satisfacibilidad global del Feature Model. "
        "Incluye jerarquía, grupos, relaciones cross-tree y constraints."
    ),
)
async def validate_feature_model_logic(
    *,
    model_id: uuid.UUID,
    version_id: uuid.UUID,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> LogicalValidationResponse:
    """
    Ejecuta validación lógica global del modelo.

    Retorna `is_valid`, errores, advertencias y una asignación satisfactoria
    de ejemplo cuando aplica.
    """
    version = await _get_version_for_validation(
        model_id=model_id,
        version_id=version_id,
        version_repo=version_repo,
        current_user=current_user,
    )
    features, relations, constraints = _build_validation_payload(version)

    validator = FeatureModelLogicalValidator()
    try:
        result = validator.validate_feature_model(features, relations, constraints)
        return LogicalValidationResponse(
            is_valid=result.is_valid,
            errors=result.errors,
            warnings=result.warnings,
            satisfying_assignment=result.satisfying_assignment,
        )
    except Exception as exc:
        return LogicalValidationResponse(
            is_valid=False,
            errors=[str(exc)],
            warnings=[],
            satisfying_assignment=None,
        )


@router.post(
    "/{model_id}/versions/{version_id}/validation/structure",
    response_model=StructureValidationResponse,
    summary="Validar estructura de árbol del modelo",
    description=(
        "Verifica que el árbol del modelo sea válido: raíz única, sin ciclos y "
        "sin features huérfanas."
    ),
)
async def validate_feature_model_structure(
    *,
    model_id: uuid.UUID,
    version_id: uuid.UUID,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> StructureValidationResponse:
    """
    Valida la estructura del árbol del Feature Model.

    Revisa raíz única, ausencia de ciclos y conectividad total.
    """
    version = await _get_version_for_validation(
        model_id=model_id,
        version_id=version_id,
        version_repo=version_repo,
        current_user=current_user,
    )
    features, relations, _ = _build_validation_payload(version)

    analyzer = FeatureModelStructuralAnalyzer()
    try:
        analyzer.validate_tree_structure(features, relations)
        return StructureValidationResponse(is_valid=True, errors=[])
    except Exception as exc:
        return StructureValidationResponse(is_valid=False, errors=[str(exc)])


@router.post(
    "/{model_id}/versions/{version_id}/validation/configuration",
    response_model=LogicalValidationResponse,
    summary="Validar una configuración concreta de features",
    description=(
        "Valida una configuración propuesta por el usuario contra el modelo "
        "(constraints, relaciones y cardinalidades)."
    ),
)
async def validate_feature_model_configuration(
    *,
    model_id: uuid.UUID,
    version_id: uuid.UUID,
    payload: ConfigurationValidationRequest,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> LogicalValidationResponse:
    """
    Valida una configuración específica de features seleccionadas.

    Devuelve errores si la selección viola constraints, relaciones o grupos.
    """
    version = await _get_version_for_validation(
        model_id=model_id,
        version_id=version_id,
        version_repo=version_repo,
        current_user=current_user,
    )
    features, relations, constraints = _build_validation_payload(version)

    validator = FeatureModelLogicalValidator()
    selected = [str(feature_id) for feature_id in payload.selected_features]

    try:
        result = validator.validate_configuration(
            features=features,
            relations=relations,
            constraints=constraints,
            selected_features=selected,
        )
        return LogicalValidationResponse(
            is_valid=result.is_valid,
            errors=result.errors,
            warnings=result.warnings,
            satisfying_assignment=result.satisfying_assignment,
        )
    except Exception as exc:
        return LogicalValidationResponse(
            is_valid=False,
            errors=[str(exc)],
            warnings=[],
            satisfying_assignment=None,
        )


@router.post(
    "/{model_id}/versions/{version_id}/validation/analysis",
    response_model=StructuralAnalysisResponse,
    summary="Ejecutar análisis estructural del modelo",
    description=(
        "Ejecuta análisis estructural: dead features, redundancias, relaciones "
        "implícitas, dependencias transitivas, SCC y métricas de complejidad."
    ),
)
async def validate_feature_model_analysis(
    *,
    model_id: uuid.UUID,
    version_id: uuid.UUID,
    payload: StructuralAnalysisRequest,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> StructuralAnalysisResponse:
    """
    Ejecuta análisis estructural detallado del modelo.

    Permite filtrar por `analysis_types` o ejecutar todos si se omite.
    """
    version = await _get_version_for_validation(
        model_id=model_id,
        version_id=version_id,
        version_repo=version_repo,
        current_user=current_user,
    )
    features, relations, constraints = _build_validation_payload(version)

    analyzer = FeatureModelStructuralAnalyzer()

    try:
        raw_results = analyzer.analyze_feature_model(
            features=features,
            relations=relations,
            constraints=constraints,
            analysis_types=payload.analysis_types,
        )

        results: list[StructuralAnalysisItem] = []
        all_valid = True
        for analysis_type, result in raw_results.items():
            issues = [
                ValidationIssue(
                    issue_type=issue.issue_type,
                    severity=issue.severity,
                    feature_id=issue.feature_id,
                    description=issue.description,
                    recommendation=issue.recommendation,
                )
                for issue in result.issues
            ]
            if issues:
                all_valid = False

            results.append(
                StructuralAnalysisItem(
                    analysis_type=analysis_type,
                    issues=issues,
                    metrics=result.metrics,
                )
            )

        return StructuralAnalysisResponse(
            is_valid=all_valid,
            results=results,
            errors=[],
        )
    except Exception as exc:
        return StructuralAnalysisResponse(
            is_valid=False,
            results=[],
            errors=[str(exc)],
        )


@router.post(
    "/{model_id}/versions/{version_id}/validation/full",
    response_model=FullValidationResponse,
    summary="Validación integral: lógica + estructura + análisis",
    description=(
        "Ejecuta validación integral del Feature Model: lógica global, estructura "
        "del árbol y análisis estructural completo en una sola llamada."
    ),
)
async def validate_feature_model_full(
    *,
    model_id: uuid.UUID,
    version_id: uuid.UUID,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> FullValidationResponse:
    """
    Ejecuta validación integral del Feature Model.

    Combina validación lógica, estructura de árbol y análisis estructural.
    """
    version = await _get_version_for_validation(
        model_id=model_id,
        version_id=version_id,
        version_repo=version_repo,
        current_user=current_user,
    )
    features, relations, constraints = _build_validation_payload(version)

    validator = FeatureModelLogicalValidator()
    analyzer = FeatureModelStructuralAnalyzer()

    # Lógica
    try:
        logical_result = validator.validate_feature_model(
            features, relations, constraints
        )
        logical_response = LogicalValidationResponse(
            is_valid=logical_result.is_valid,
            errors=logical_result.errors,
            warnings=logical_result.warnings,
            satisfying_assignment=logical_result.satisfying_assignment,
        )
    except Exception as exc:
        logical_response = LogicalValidationResponse(
            is_valid=False,
            errors=[str(exc)],
            warnings=[],
            satisfying_assignment=None,
        )

    # Estructura
    try:
        analyzer.validate_tree_structure(features, relations)
        structure_response = StructureValidationResponse(is_valid=True, errors=[])
    except Exception as exc:
        structure_response = StructureValidationResponse(
            is_valid=False, errors=[str(exc)]
        )

    # Análisis estructural
    try:
        raw_results = analyzer.analyze_feature_model(features, relations, constraints)
        analysis_items: list[StructuralAnalysisItem] = []
        analysis_is_valid = True
        for analysis_type, result in raw_results.items():
            issues = [
                ValidationIssue(
                    issue_type=issue.issue_type,
                    severity=issue.severity,
                    feature_id=issue.feature_id,
                    description=issue.description,
                    recommendation=issue.recommendation,
                )
                for issue in result.issues
            ]
            if issues:
                analysis_is_valid = False

            analysis_items.append(
                StructuralAnalysisItem(
                    analysis_type=analysis_type,
                    issues=issues,
                    metrics=result.metrics,
                )
            )

        analysis_response = StructuralAnalysisResponse(
            is_valid=analysis_is_valid,
            results=analysis_items,
            errors=[],
        )
    except Exception as exc:
        analysis_response = StructuralAnalysisResponse(
            is_valid=False,
            results=[],
            errors=[str(exc)],
        )

    return FullValidationResponse(
        logical=logical_response,
        structure=structure_response,
        analysis=analysis_response,
    )
