import uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.enums import FeatureType
from .common import BaseTable, PaginatedResponse

if TYPE_CHECKING:
    from .feature_model_version import FeatureModelVersion
    from .configuration import Configuration
    from .feature_relation import FeatureRelation


# ---------------------------------------------------------------------------
# Modelo Base para Feature
# ---------------------------------------------------------------------------
class FeatureBase(SQLModel):
    name: str = Field(max_length=100)
    type: FeatureType
    feature_model_version_id: uuid.UUID = Field(foreign_key="feature_model_versions.id")
    # Clave foránea para la jerarquía padre-hijo (auto-referencia)
    parent_id: uuid.UUID | None = Field(default=None, foreign_key="feature.id")


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

    # Relaciones muchos-a-muchos con Configuration
    configurations: list["Configuration"] = Relationship(
        back_populates="features", link_model="configuration_features"
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
