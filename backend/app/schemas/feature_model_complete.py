"""
Schemas para la respuesta completa de Feature Model
Optimizados para renderizado de árbol en frontend
"""

import uuid
from typing import Optional, Any
from datetime import datetime

from pydantic import BaseModel, Field

from app.enums import FeatureType, ModelStatus, ResourceType, ResourceStatus


# ============================================================================
# SCHEMAS ANIDADOS PARA EL ÁRBOL
# ============================================================================


class ResourceSummary(BaseModel):
    """Resumen de un recurso asociado a una feature."""

    id: uuid.UUID
    title: str
    type: ResourceType
    content_url_or_data: Optional[dict[str, Any]] = None
    language: str
    status: ResourceStatus
    duration_minutes: Optional[int] = None


class FeatureGroupInfo(BaseModel):
    """Información de grupo (XOR, OR) para features."""

    id: uuid.UUID
    group_type: str  # "XOR" o "OR"
    min_cardinality: int
    max_cardinality: Optional[int]
    description: Optional[str] = Field(
        None,
        description="Descripción legible del grupo, ej: 'Debes elegir exactamente UNA especialización'",
    )


class FeatureTreeNode(BaseModel):
    """
    Nodo del árbol jerárquico de features.
    Estructura recursiva para renderizado completo.
    """

    id: uuid.UUID
    name: str
    type: FeatureType
    properties: dict[str, Any] = Field(
        default_factory=dict,
        description="Propiedades específicas: créditos, horas, semestre, etc.",
    )
    resource: Optional[ResourceSummary] = None
    tags: list[str] = Field(
        default_factory=list, description="Nombres de tags asociados"
    )
    group: Optional[FeatureGroupInfo] = Field(
        None, description="Si esta feature define un grupo (XOR/OR), aquí está la info"
    )
    children: list["FeatureTreeNode"] = Field(
        default_factory=list, description="Features hijas en la jerarquía"
    )

    # Metadatos útiles para el frontend
    depth: int = Field(0, description="Profundidad en el árbol (0 = raíz)")
    is_leaf: bool = Field(False, description="True si no tiene hijos")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Matemática I",
                "type": "MANDATORY",
                "properties": {
                    "creditos": 6,
                    "semestre": 1,
                    "horas_teoricas": 48,
                    "horas_practicas": 32,
                },
                "resource": {
                    "id": "223e4567-e89b-12d3-a456-426614174000",
                    "title": "Material de Matemática I",
                    "type": "PACKAGE",
                    "language": "es",
                    "status": "PUBLISHED",
                },
                "tags": ["ciencias básicas", "fundamentos"],
                "group": None,
                "children": [],
                "depth": 2,
                "is_leaf": True,
            }
        }


# Para permitir la referencia recursiva
FeatureTreeNode.model_rebuild()


class FeatureRelationInfo(BaseModel):
    """Relación entre dos features (prerequisito o exclusión)."""

    id: uuid.UUID
    type: str  # "REQUIRES" o "EXCLUDES"
    source_feature_id: uuid.UUID
    source_feature_name: str
    target_feature_id: uuid.UUID
    target_feature_name: str
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "323e4567-e89b-12d3-a456-426614174000",
                "type": "REQUIRES",
                "source_feature_id": "423e4567-e89b-12d3-a456-426614174000",
                "source_feature_name": "Matemática II",
                "target_feature_id": "523e4567-e89b-12d3-a456-426614174000",
                "target_feature_name": "Matemática I",
                "description": "Matemática II requiere haber aprobado Matemática I",
            }
        }


class ConstraintInfo(BaseModel):
    """Restricción formal sobre el feature model."""

    id: uuid.UUID
    description: Optional[str] = Field(
        None, description="Descripción en lenguaje natural"
    )
    expr_text: str = Field(description="Expresión lógica en formato texto")
    expr_cnf: Optional[dict[str, Any]] = Field(
        None, description="Forma Normal Conjuntiva (para SAT solvers)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "623e4567-e89b-12d3-a456-426614174000",
                "description": "Los créditos totales deben sumar 240",
                "expr_text": "SUM(features.properties.creditos) = 240",
                "expr_cnf": {"clauses": [[1, 2], [-1, 3]]},
            }
        }


# ============================================================================
# METADATA Y ESTADÍSTICAS
# ============================================================================


class FeatureModelStatistics(BaseModel):
    """Estadísticas pre-computadas del feature model."""

    total_features: int
    mandatory_features: int
    optional_features: int
    total_groups: int
    xor_groups: int
    or_groups: int
    total_relations: int
    requires_relations: int
    excludes_relations: int
    total_constraints: int
    total_configurations: int
    max_tree_depth: int = Field(description="Profundidad máxima del árbol de features")

    class Config:
        json_schema_extra = {
            "example": {
                "total_features": 45,
                "mandatory_features": 32,
                "optional_features": 13,
                "total_groups": 5,
                "xor_groups": 3,
                "or_groups": 2,
                "total_relations": 18,
                "requires_relations": 15,
                "excludes_relations": 3,
                "total_constraints": 8,
                "total_configurations": 12,
                "max_tree_depth": 5,
            }
        }


class ResponseMetadata(BaseModel):
    """Metadatos de la respuesta del endpoint."""

    cached: bool = Field(description="Si la respuesta viene del caché")
    cache_expires_at: Optional[datetime] = None
    generated_at: datetime
    processing_time_ms: int = Field(
        description="Tiempo de procesamiento en milisegundos"
    )
    version_status: ModelStatus


# ============================================================================
# RESPUESTA COMPLETA
# ============================================================================


class FeatureModelInfo(BaseModel):
    """Información básica del feature model."""

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    domain_id: uuid.UUID
    domain_name: str
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool


class FeatureModelVersionInfo(BaseModel):
    """Información de la versión específica."""

    id: uuid.UUID
    version_number: int
    status: ModelStatus
    snapshot: Optional[dict[str, Any]] = None
    created_at: datetime


class FeatureModelCompleteResponse(BaseModel):
    """
    Respuesta completa del feature model con toda la estructura.

    Esta respuesta contiene TODO lo necesario para renderizar el árbol
    completo en el frontend, incluyendo jerarquía, grupos, relaciones
    y constraints.
    """

    feature_model: FeatureModelInfo
    version: FeatureModelVersionInfo
    tree: FeatureTreeNode = Field(
        description="Árbol jerárquico completo de features (estructura recursiva)"
    )
    relations: list[FeatureRelationInfo] = Field(
        default_factory=list,
        description="Todas las relaciones REQUIRES y EXCLUDES entre features",
    )
    constraints: list[ConstraintInfo] = Field(
        default_factory=list, description="Restricciones formales del modelo"
    )
    statistics: Optional[FeatureModelStatistics] = Field(
        None, description="Estadísticas pre-computadas (opcional)"
    )
    metadata: ResponseMetadata = Field(
        description="Metadatos de la respuesta (caché, tiempos, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "feature_model": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "Ingeniería en Ciencias Informáticas",
                    "description": "Plan de estudios completo de 5 años",
                    "domain_id": "223e4567-e89b-12d3-a456-426614174000",
                    "domain_name": "Ingeniería Informática",
                    "owner_id": "323e4567-e89b-12d3-a456-426614174000",
                    "created_at": "2025-11-24T06:36:26.897923",
                    "updated_at": "2025-11-25T10:15:30.123456",
                    "is_active": True,
                },
                "version": {
                    "id": "423e4567-e89b-12d3-a456-426614174000",
                    "version_number": 1,
                    "status": "PUBLISHED",
                    "snapshot": {},
                    "created_at": "2025-11-24T06:36:26.897923",
                },
                "tree": {
                    "id": "523e4567-e89b-12d3-a456-426614174000",
                    "name": "Plan de Estudios ICI",
                    "type": "MANDATORY",
                    "properties": {"creditos_totales": 240, "duracion_años": 5},
                    "resource": None,
                    "tags": ["obligatorio"],
                    "group": None,
                    "children": [],
                    "depth": 0,
                    "is_leaf": False,
                },
                "relations": [],
                "constraints": [],
                "statistics": {
                    "total_features": 45,
                    "mandatory_features": 32,
                    "optional_features": 13,
                    "total_groups": 5,
                    "xor_groups": 3,
                    "or_groups": 2,
                    "total_relations": 18,
                    "requires_relations": 15,
                    "excludes_relations": 3,
                    "total_constraints": 8,
                    "total_configurations": 12,
                    "max_tree_depth": 5,
                },
                "metadata": {
                    "cached": True,
                    "cache_expires_at": "2025-12-10T15:30:00Z",
                    "generated_at": "2025-12-10T15:00:00Z",
                    "processing_time_ms": 245,
                    "version_status": "PUBLISHED",
                },
            }
        }
