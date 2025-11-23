"""Definición del modelo `Feature` y esquemas relacionados.

Incluye la entidad de base de datos `Feature` con sus relaciones (jerarquía
padre/hijo, grupos, tags, configuraciones) y los modelos Pydantic/SQLModel
para las operaciones de creación, actualización y presentación en la API.
"""

import uuid
from typing import TYPE_CHECKING, Optional, Dict, Any

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import UniqueConstraint, Index
from sqlmodel import Column, Field, Relationship, SQLModel

from app.enums import FeatureType
from .common import BaseTable, PaginatedResponse
from .link_models import ConfigurationFeatureLink, FeatureTagLink

if TYPE_CHECKING:
    from .resource import Resource
    from .configuration import Configuration
    from .feature_model_version import FeatureModelVersion
    from .feature_group import FeatureGroup
    from .feature_relation import FeatureRelation
    from .tag import Tag


# ========================================================================
#               --- Modelo Base para Feature ---
# ========================================================================
class FeatureBase(SQLModel):

    # ------------------ FIELDs ----------------------------------------

    name: str = Field(max_length=100)
    type: FeatureType
    properties: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    feature_model_version_id: uuid.UUID = Field(
        foreign_key="feature_model_versions.id", index=True
    )
    # Clave foránea para la jerarquía padre-hijo (auto-referencia)
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="features.id")
    # Clave foránea para indicar pertenencia a un grupo XOR/OR
    group_id: Optional[uuid.UUID] = Field(default=None, foreign_key="feature_groups.id")
    # Clave foránea para indicar si la características es un recurso (ARCHIVO MEDIA)
    resource_id: Optional[uuid.UUID] = Field(default=None, foreign_key="resources.id")


# ========================================================================
#             --- Modelo de la Tabla de Base de Datos ---
# ========================================================================


class Feature(BaseTable, FeatureBase, table=True):

    # ------------------ METADATA FOR TABLE ----------------------------------------

    __tablename__ = "features"

    __table_args__ = (
        UniqueConstraint(
            "feature_model_version_id", "name", name="uq_feature_version_name"
        ),
        Index("ix_features_properties_gin", "properties", postgresql_using="gin"),
    )

    # ------------------ RELATIONSHIP ----------------------------------------

    tags: list["Tag"] = Relationship(
        back_populates="features", link_model=FeatureTagLink
    )

    # Relación de vuelta a FeatureModelVersion
    feature_model_version: "FeatureModelVersion" = Relationship(
        back_populates="features"
    )

    # Relaciones para la jerarquía (auto-referencia)
    parent: Optional["Feature"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs=dict(remote_side="Feature.id"),
    )
    children: list["Feature"] = Relationship(back_populates="parent")

    # Relación con el grupo al que pertenece esta feature
    group: Optional["FeatureGroup"] = Relationship(
        back_populates="member_features",
        sa_relationship_kwargs={"foreign_keys": "[Feature.group_id]"},
    )

    # Relación con los grupos de hijos que esta feature define
    child_groups: list["FeatureGroup"] = Relationship(
        back_populates="parent_feature",
        sa_relationship_kwargs={"foreign_keys": "[FeatureGroup.parent_feature_id]"},
    )

    # Relaciones muchos-a-muchos con Configuration
    configurations: list["Configuration"] = Relationship(
        back_populates="features", link_model=ConfigurationFeatureLink
    )

    # Relaciones donde esta feature es el origen o el destino
    source_relations: list["FeatureRelation"] = Relationship(
        back_populates="source_feature",
        sa_relationship_kwargs={"foreign_keys": "[FeatureRelation.source_feature_id]"},
    )
    target_relations: list["FeatureRelation"] = Relationship(
        back_populates="target_feature",
        sa_relationship_kwargs={"foreign_keys": "[FeatureRelation.target_feature_id]"},
    )

    # Relacion Para poder acceder al objeto Resource completo desde una Feature
    resource: Optional["Resource"] = Relationship(back_populates="features")


# ========================================================================
#           --- Modelos para la API (Pydantic) ---
# ========================================================================


class FeatureCreate(FeatureBase):
    # Hereda todo de FeatureBase, no necesita campos adicionales para la creación
    pass


class FeatureUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    type: Optional[FeatureType] = None
    parent_id: Optional[uuid.UUID] = None
    group_id: Optional[uuid.UUID] = None


# ========================================================================
#       --- Modelos para Respuestas de las Características ---
# ========================================================================


class FeaturePublic(FeatureBase):
    id: uuid.UUID


class FeatureListResponse(PaginatedResponse[FeaturePublic]):
    pass


# Modelo público recursivo para mostrar la jerarquía completa
class FeaturePublicWithChildren(FeaturePublic):
    children: list["FeaturePublicWithChildren"] = []
    # Aquí podrías añadir también las relaciones si quisieras mostrarlas en el árbol


# Actualizar referencias de tipos después de la definición de la clase
FeaturePublicWithChildren.model_rebuild()
