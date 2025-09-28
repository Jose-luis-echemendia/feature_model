import uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.enums import FeatureGroupType
from .common import BaseTable

if TYPE_CHECKING:
    from .feature import Feature
    from .feature_model_version import FeatureModelVersion


class FeatureGroupBase(SQLModel):
    group_type: FeatureGroupType = Field(index=True)
    min_cardinality: int = Field(default=1)
    max_cardinality: Optional[int] = Field(default=None)  # 1 para XOR, >1 para OR
    parent_feature_id: uuid.UUID = Field(foreign_key="features.id")
    feature_model_version_id: uuid.UUID = Field(foreign_key="feature_model_versions.id")


class FeatureGroup(BaseTable, FeatureGroupBase, table=True):
    
    __tablename__ = "feature_groups"

    # Relación de vuelta a la versión del modelo
    feature_model_version: "FeatureModelVersion" = Relationship(
        back_populates="feature_groups"
    )

    # Relación con la feature padre que define este grupo
    parent_feature: "Feature" = Relationship(back_populates="child_groups")

    # Relación con las features que son miembros de este grupo
    member_features: list["Feature"] = Relationship(back_populates="group")


class FeatureGroupCreate(SQLModel):
    group_type: FeatureGroupType
    parent_feature_id: uuid.UUID
    min_cardinality: int = 1
    max_cardinality: Optional[int] = None


class FeatureGroupPublic(FeatureGroupBase):
    id: uuid.UUID
