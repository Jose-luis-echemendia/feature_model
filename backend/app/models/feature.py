import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Index, UniqueConstraint
from sqlalchemy import UniqueConstraint
from sqlmodel import Column, Field, Relationship, SQLModel

from app.enums import FeatureType
from .common import BaseTable, PaginatedResponse
from .link_models import ConfigurationFeatureLink

if TYPE_CHECKING:
    from .feature_model_version import FeatureModelVersion
    from .configuration import Configuration
    from .feature_group import FeatureGroup
    from .feature_relation import FeatureRelation


# ---------------------------------------------------------------------------
# Modelo Base para Feature
# ---------------------------------------------------------------------------
class FeatureBase(SQLModel):
    name: str = Field(max_length=100)
    type: FeatureType
    metadata: dict | None = Field(default=None, sa_column=Column(JSONB))
    feature_model_version_id: uuid.UUID = Field(foreign_key="feature_model_versions.id")
    metadata: dict | None = Field(default=None, sa_column=Column(JSONB, index=True, sa_column_kwargs={"postgresql_using": "gin"}))
    feature_model_version_id: uuid.UUID = Field(
        foreign_key="feature_model_versions.id", index=True
    )
    # Clave foránea para la jerarquía padre-hijo (auto-referencia)
    parent_id: uuid.UUID | None = Field(default=None, foreign_key="features.id")
    # Clave foránea para indicar pertenencia a un grupo XOR/OR
    group_id: uuid.UUID | None = Field(default=None, foreign_key="feature_groups.id")



# ---------------------------------------------------------------------------
# Modelo de la Tabla de Base de Datos
# ---------------------------------------------------------------------------


class Feature(BaseTable, FeatureBase, table=True):

    __tablename__ = "features"

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
    group: Optional["FeatureGroup"] = Relationship(back_populates="member_features")

    # Relación con los grupos de hijos que esta feature define
    child_groups: list["FeatureGroup"] = Relationship(back_populates="parent_feature")

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

    __table_args__ = (
        UniqueConstraint(
            "feature_model_version_id", "name", name="uq_feature_version_name"
        ),
    )


# ---------------------------------------------------------------------------
# Modelos para la API (Pydantic)
# ---------------------------------------------------------------------------


class FeatureCreate(FeatureBase):
    # Hereda todo de FeatureBase, no necesita campos adicionales para la creación
    pass


class FeatureUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    type: FeatureType | None = None
    parent_id: uuid.UUID | None = None
    group_id: uuid.UUID | None = None


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
