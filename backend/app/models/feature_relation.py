import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.enums import FeatureRelationType
from .common import BaseTable

if TYPE_CHECKING:
    from .feature import Feature
    from .feature_model_version import FeatureModelVersion


class FeatureRelationBase(SQLModel):
    type: FeatureRelationType = Field(index=True)
    source_feature_id: uuid.UUID = Field(foreign_key="feature.id", index=True)
    target_feature_id: uuid.UUID = Field(foreign_key="feature.id", index=True)
    feature_model_version_id: uuid.UUID = Field(foreign_key="feature_model_versions.id")


class FeatureRelationCreate(SQLModel):
    type: FeatureRelationType
    source_feature_id: uuid.UUID
    target_feature_id: uuid.UUID
    # La versión del modelo se infiere de las features, no se pasa directamente


class FeatureRelation(BaseTable, FeatureRelationBase, table=True):
    
    __tablename__ = "feature_relations"

    feature_model_version: "FeatureModelVersion" = Relationship(
        back_populates="feature_relations"
    )

    source_feature: "Feature" = Relationship(
        back_populates="source_relations",
        sa_relationship_kwargs={"foreign_keys": "[FeatureRelation.source_feature_id]"},
    )
    target_feature: "Feature" = Relationship(
        back_populates="target_relations",
        sa_relationship_kwargs={"foreign_keys": "[FeatureRelation.target_feature_id]"},
    )


class FeatureRelationPublic(FeatureRelationBase):
    id: uuid.UUID


class FeatureRelationUpdate(SQLModel):
    pass  # Las relaciones no se actualizan, se crean o eliminan
