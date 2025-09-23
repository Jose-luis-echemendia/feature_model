import uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.enums import FeatureType
from .common import BaseTable
from .configuration import ConfigurationFeature

if TYPE_CHECKING:
    from .feature_model import FeatureModel
    from .feature_relation import FeatureRelation
    from .configuration import Configuration


class FeatureBase(SQLModel):
    name: str = Field(max_length=100)
    type: FeatureType
    feature_model_id: uuid.UUID = Field(foreign_key="feature_model.id")
    # Clave foránea para la jerarquía padre-hijo (auto-referencia)
    parent_id: uuid.UUID | None = Field(default=None, foreign_key="feature.id")


class FeatureCreate(FeatureBase):
    pass


class FeatureUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    type: FeatureType | None = None
    parent_id: uuid.UUID | None = None


class Feature(BaseTable, FeatureBase, table=True):

    __tablename__ = "features"

    # Relación de vuelta a FeatureModel
    feature_model: "FeatureModel" = Relationship(back_populates="features")

    # Relaciones para la jerarquía (auto-referencia)
    parent: Optional["Feature"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs=dict(
            remote_side="Feature.id"
        ),  # Esencial para SQLAlchemy
    )
    children: list["Feature"] = Relationship(back_populates="parent")

    # Relaciones para requires/excludes
    relations: list["FeatureRelation"] = Relationship(
        back_populates="source_feature",
        sa_relationship_kwargs={"foreign_keys": "FeatureRelation.feature_id"},
    )
    related_to: list["FeatureRelation"] = Relationship(
        back_populates="related_feature",
        sa_relationship_kwargs={"foreign_keys": "FeatureRelation.related_feature_id"},
    )

    # Relación muchos-a-muchos con Configuration
    configurations: list["Configuration"] = Relationship(
        back_populates="features", link_model=ConfigurationFeature
    )


class FeaturePublic(FeatureBase):
    id: uuid.UUID


# Modelo público recursivo para mostrar la jerarquía completa
class FeaturePublicWithChildren(FeaturePublic):
    children: list["FeaturePublicWithChildren"] = []


# Actualizar referencias de tipos después de la definición de la clase
FeaturePublicWithChildren.model_rebuild()
