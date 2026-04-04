import uuid
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import AsyncConfigurationRepoDep, AsyncFeatureModelVersionRepoDep
from app.enums import GenerationStrategy
from app.models.common import Message
from app.models.configuration import (
    ConfigurationCreate,
    ConfigurationListResponse,
    ConfigurationPublic,
    ConfigurationPublicWithFeatures,
    ConfigurationUpdate,
)
from app.services.feature_model import (
    FeatureModelConfigurationGenerator,
    FeatureModelLogicalValidator,
)


router = APIRouter(prefix="/configurations", tags=["configurations"])


class ConfigurationValidationRequest(BaseModel):
    feature_model_version_id: uuid.UUID
    selected_features: list[uuid.UUID] = Field(default_factory=list)


class ConfigurationValidationResponse(BaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ConfigurationGenerationRequest(BaseModel):
    feature_model_version_id: uuid.UUID
    strategy: GenerationStrategy = GenerationStrategy.GREEDY
    count: int = Field(default=1, ge=1, le=100)
    diverse: bool = True
    partial_selection: Optional[dict[uuid.UUID, bool]] = None


class ConfigurationGenerationItem(BaseModel):
    success: bool
    selected_features: list[uuid.UUID] = Field(default_factory=list)
    score: float = 0.0
    iterations: int = 0
    errors: list[str] = Field(default_factory=list)


class ConfigurationGenerationResponse(BaseModel):
    results: list[ConfigurationGenerationItem] = Field(default_factory=list)


class StagedConfigurationRequest(BaseModel):
    feature_model_version_id: uuid.UUID
    partial_selection: dict[uuid.UUID, bool] = Field(default_factory=dict)


class StagedConfigurationResponse(BaseModel):
    can_select: list[uuid.UUID] = Field(default_factory=list)
    can_deselect: list[uuid.UUID] = Field(default_factory=list)
    must_select: list[uuid.UUID] = Field(default_factory=list)
    must_deselect: list[uuid.UUID] = Field(default_factory=list)


def _build_configuration_payload(
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


@router.post(
    "/",
    response_model=ConfigurationPublic,
    summary="Crear configuración",
    description="Crea y valida una configuración para una versión del modelo.",
)
async def create_configuration(
    *,
    configuration_in: ConfigurationCreate,
    configuration_repo: AsyncConfigurationRepoDep,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
) -> ConfigurationPublic:
    """
    Crea una nueva configuración.
    """
    version = await feature_model_version_repo.get_complete_with_relations(
        version_id=configuration_in.feature_model_version_id,
        include_resources=False,
    )
    if not version:
        raise HTTPException(status_code=404, detail="Feature model version not found")

    features_payload, relations_payload, constraints_payload = (
        _build_configuration_payload(version)
    )
    validator = FeatureModelLogicalValidator()
    selected = [str(feature_id) for feature_id in configuration_in.feature_ids]
    try:
        result = validator.validate_configuration(
            features=features_payload,
            relations=relations_payload,
            constraints=constraints_payload,
            selected_features=selected,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=[str(exc)]) from exc

    if not result.is_valid:
        raise HTTPException(
            status_code=400,
            detail=result.errors or ["Invalid configuration"],
        )

    configuration = await configuration_repo.create(data=configuration_in)
    return configuration


@router.get(
    "/{id}",
    response_model=ConfigurationPublicWithFeatures,
    summary="Obtener configuración",
    description="Recupera una configuración por su ID, incluyendo features y tags.",
)
async def read_configuration(
    *,
    id: uuid.UUID,
    configuration_repo: AsyncConfigurationRepoDep,
) -> ConfigurationPublicWithFeatures:
    """
    Obtiene una configuración por su ID.
    """
    db_configuration = await configuration_repo.get(configuration_id=id)
    if not db_configuration:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return db_configuration


@router.get(
    "/",
    response_model=ConfigurationListResponse,
    summary="Listar configuraciones",
    description="Lista configuraciones con paginación (skip/limit).",
)
async def list_configurations(
    *,
    skip: int = 0,
    limit: int = 100,
    configuration_repo: AsyncConfigurationRepoDep,
) -> ConfigurationListResponse:
    """
    Lista configuraciones con paginación.
    """
    items = await configuration_repo.get_all(skip=skip, limit=limit)
    total = await configuration_repo.count()
    return ConfigurationListResponse.create(
        data=items, count=total, skip=skip, limit=limit
    )


@router.put(
    "/{id}",
    response_model=ConfigurationPublic,
    summary="Actualizar configuración",
    description="Actualiza nombre, descripción y/o features asociados.",
)
async def update_configuration(
    *,
    id: uuid.UUID,
    configuration_in: ConfigurationUpdate,
    configuration_repo: AsyncConfigurationRepoDep,
) -> ConfigurationPublic:
    """
    Actualiza una configuración.
    """
    db_configuration = await configuration_repo.get(configuration_id=id)
    if not db_configuration:
        raise HTTPException(status_code=404, detail="Configuration not found")

    db_configuration = await configuration_repo.update(
        db_configuration=db_configuration,
        data=configuration_in,
    )
    return db_configuration


@router.delete(
    "/{id}",
    response_model=Message,
    summary="Eliminar configuración",
    description="Elimina una configuración existente por su ID.",
)
async def delete_configuration(
    *,
    id: uuid.UUID,
    configuration_repo: AsyncConfigurationRepoDep,
) -> Message:
    """
    Elimina una configuración por su ID.
    """
    db_configuration = await configuration_repo.get(configuration_id=id)
    if not db_configuration:
        raise HTTPException(status_code=404, detail="Configuration not found")

    await configuration_repo.delete(db_configuration=db_configuration)
    return Message(message="Configuration deleted")


@router.post(
    "/validate",
    response_model=ConfigurationValidationResponse,
    summary="Validar configuración",
    description="Valida una selección de features contra una versión del modelo.",
)
async def validate_configuration(
    *,
    payload: ConfigurationValidationRequest,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
) -> ConfigurationValidationResponse:
    """
    Valida una configuración propuesta contra una versión del modelo.
    """
    version = await feature_model_version_repo.get_complete_with_relations(
        version_id=payload.feature_model_version_id,
        include_resources=False,
    )
    if not version:
        raise HTTPException(status_code=404, detail="Feature model version not found")

    features_payload, relations_payload, constraints_payload = (
        _build_configuration_payload(version)
    )
    validator = FeatureModelLogicalValidator()
    selected = [str(feature_id) for feature_id in payload.selected_features]
    try:
        result = validator.validate_configuration(
            features=features_payload,
            relations=relations_payload,
            constraints=constraints_payload,
            selected_features=selected,
        )
    except Exception as exc:
        return ConfigurationValidationResponse(
            is_valid=False,
            errors=[str(exc)],
            warnings=[],
        )

    return ConfigurationValidationResponse(
        is_valid=result.is_valid,
        errors=result.errors,
        warnings=result.warnings,
    )


@router.post(
    "/generate",
    response_model=ConfigurationGenerationResponse,
    summary="Generar configuraciones",
    description=(
        "Genera una o varias configuraciones válidas usando una estrategia "
        "(greedy, random, beam_search, genetic, sat_enum, pairwise, uniform, stratified, cp_sat)."
    ),
)
async def generate_configuration(
    *,
    payload: ConfigurationGenerationRequest,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
) -> ConfigurationGenerationResponse:
    """
    Genera una o varias configuraciones válidas para una versión del modelo.
    """
    version = await feature_model_version_repo.get_complete_with_relations(
        version_id=payload.feature_model_version_id,
        include_resources=False,
    )
    if not version:
        raise HTTPException(status_code=404, detail="Feature model version not found")

    features_payload, relations_payload, constraints_payload = (
        _build_configuration_payload(version)
    )

    generator = FeatureModelConfigurationGenerator()
    partial_selection = (
        {str(k): v for k, v in payload.partial_selection.items()}
        if payload.partial_selection
        else None
    )

    results: list[ConfigurationGenerationItem] = []
    if payload.count == 1:
        generated = generator.generate_valid_configuration(
            features=features_payload,
            relations=relations_payload,
            constraints=constraints_payload,
            strategy=payload.strategy,
            partial_selection=partial_selection,
        )
        results.append(
            ConfigurationGenerationItem(
                success=generated.success,
                selected_features=[
                    uuid.UUID(fid) for fid in generated.selected_features
                ],
                score=generated.score,
                iterations=generated.iterations,
                errors=generated.errors,
            )
        )
    else:
        generated_list = generator.generate_multiple_configurations(
            features=features_payload,
            relations=relations_payload,
            constraints=constraints_payload,
            count=payload.count,
            diverse=payload.diverse,
            strategy=payload.strategy,
            partial_selection=partial_selection,
        )
        for generated in generated_list:
            results.append(
                ConfigurationGenerationItem(
                    success=generated.success,
                    selected_features=[
                        uuid.UUID(fid) for fid in generated.selected_features
                    ],
                    score=generated.score,
                    iterations=generated.iterations,
                    errors=generated.errors,
                )
            )

    return ConfigurationGenerationResponse(results=results)


@router.post(
    "/staged/options",
    response_model=StagedConfigurationResponse,
    summary="Staged configuration",
    description=(
        "Dadas decisiones parciales, devuelve qué features pueden seleccionarse "
        "o deseleccionarse, y cuáles quedan forzadas por las restricciones."
    ),
)
async def staged_configuration_options(
    *,
    payload: StagedConfigurationRequest,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
) -> StagedConfigurationResponse:
    """
    Calcula opciones válidas para configuración guiada (staged).
    """
    version = await feature_model_version_repo.get_complete_with_relations(
        version_id=payload.feature_model_version_id,
        include_resources=False,
    )
    if not version:
        raise HTTPException(status_code=404, detail="Feature model version not found")

    features_payload, relations_payload, constraints_payload = (
        _build_configuration_payload(version)
    )

    validator = FeatureModelLogicalValidator()
    partial = {str(k): v for k, v in payload.partial_selection.items()}
    if not validator.is_partial_selection_satisfiable(
        features=features_payload,
        relations=relations_payload,
        constraints=constraints_payload,
        partial_selection=partial,
    ):
        raise HTTPException(
            status_code=400,
            detail=["Partial selection is unsatisfiable"],
        )

    can_select: list[uuid.UUID] = []
    can_deselect: list[uuid.UUID] = []
    must_select: list[uuid.UUID] = []
    must_deselect: list[uuid.UUID] = []

    for feature in features_payload:
        feature_id = str(feature.get("id"))
        if feature_id in partial:
            if partial[feature_id]:
                must_select.append(uuid.UUID(feature_id))
            else:
                must_deselect.append(uuid.UUID(feature_id))
            continue

        partial_true = {**partial, feature_id: True}
        partial_false = {**partial, feature_id: False}

        can_true = validator.is_partial_selection_satisfiable(
            features=features_payload,
            relations=relations_payload,
            constraints=constraints_payload,
            partial_selection=partial_true,
        )
        can_false = validator.is_partial_selection_satisfiable(
            features=features_payload,
            relations=relations_payload,
            constraints=constraints_payload,
            partial_selection=partial_false,
        )

        if can_true:
            can_select.append(uuid.UUID(feature_id))
        if can_false:
            can_deselect.append(uuid.UUID(feature_id))
        if can_true and not can_false:
            must_select.append(uuid.UUID(feature_id))
        if can_false and not can_true:
            must_deselect.append(uuid.UUID(feature_id))

    return StagedConfigurationResponse(
        can_select=can_select,
        can_deselect=can_deselect,
        must_select=must_select,
        must_deselect=must_deselect,
    )
