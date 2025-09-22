import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.enums import RelationType
from .common import BaseTable

if TYPE_CHECKING:
    from .feature import Feature


class FeatureRelationBase(SQLModel):
    feature_id: uuid.UUID = Field(foreign_key="feature.id")
    related_feature_id: uuid.UUID = Field(foreign_key="feature.id")
    relation_type: RelationType


class FeatureRelationCreate(FeatureRelationBase):
    pass


class FeatureRelationUpdate(SQLModel):
    relation_type: RelationType | None = None


class FeatureRelation(BaseTable, FeatureRelationBase, table=True):
    
    __tablename__ = "feature_relations"
    
    source_feature: "Feature" = Relationship(
        back_populates="relations",
        sa_relationship_kwargs={"foreign_keys": "[FeatureRelation.feature_id]"}
    )
    related_feature: "Feature" = Relationship(
        back_populates="related_to",
        sa_relationship_kwargs={"foreign_keys": "[FeatureRelation.related_feature_id]"}
    )


class FeatureRelationPublic(FeatureRelationBase):
    id: uuid.UUID