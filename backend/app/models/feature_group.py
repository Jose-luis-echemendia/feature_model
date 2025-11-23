"""Modelos para FeatureGroup: definición de grupos XOR/OR y cardinalidades.

Un `FeatureGroup` representa una agrupación de features definida por una
feature padre (por ejemplo para XOR/OR). Aquí se definen la tabla y los
esquemas públicos/creación usados en la API.
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.enums import FeatureGroupType
from .common import BaseTable

if TYPE_CHECKING:
    from .feature import Feature
    from .feature_model_version import FeatureModelVersion


# ========================================================================
#          --- Modelo de Grupos de Características base ---
# ========================================================================


class FeatureGroupBase(SQLModel):

    # ------------------ FIELDs ----------------------------------------

    group_type: FeatureGroupType = Field(index=True)
    min_cardinality: int = Field(default=1)
    max_cardinality: Optional[int] = Field(default=None)  # 1 para XOR, >1 para OR
    parent_feature_id: uuid.UUID = Field(foreign_key="features.id")
    feature_model_version_id: uuid.UUID = Field(foreign_key="feature_model_versions.id")


# ========================================================================
#   --- Modelo para la tabla física de Grupos de Características ---
# ========================================================================


class FeatureGroup(BaseTable, FeatureGroupBase, table=True):

    # ------------------ METADATA FOR TABLE ----------------------------------

    __tablename__ = "feature_groups"

    # ------------------ RELATIONSHIP ----------------------------------------

    # Relación de vuelta a la versión del modelo
    feature_model_version: "FeatureModelVersion" = Relationship(
        back_populates="feature_groups"
    )

    # Relación con la feature padre que define este grupo
    parent_feature: "Feature" = Relationship(
        back_populates="child_groups",
        sa_relationship_kwargs={"foreign_keys": "[FeatureGroup.parent_feature_id]"},
    )

    # Relación con las features que son miembros de este grupo
    member_features: list["Feature"] = Relationship(
        back_populates="group",
        sa_relationship_kwargs={"foreign_keys": "[Feature.group_id]"},
    )


# ========================================================================
#   --- Modelos para Entrada de datos de Grupos de Características ---
# ========================================================================


class FeatureGroupCreate(SQLModel):
    group_type: FeatureGroupType
    parent_feature_id: uuid.UUID
    min_cardinality: int = 1
    max_cardinality: Optional[int] = None


# ========================================================================
#    --- Modelos para Respuestas de Grupos de Características ---
# ========================================================================


class FeatureGroupPublic(FeatureGroupBase):
    id: uuid.UUID
