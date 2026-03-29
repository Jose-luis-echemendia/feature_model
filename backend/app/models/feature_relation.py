"""Relaciones entre features (requiere/excluye/implica etc.).

Define `FeatureRelation` que modela relaciones semánticas entre una feature
origen y una feature destino dentro de una misma versión del modelo.
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.enums import FeatureRelationType
from .common import BaseTable

if TYPE_CHECKING:
    from .feature import Feature
    from .feature_model_version import FeatureModelVersion


# ========================================================================
#        --- Modelo de Relaciones entre Características base ---
# ========================================================================


class FeatureRelationBase(SQLModel):

    # ------------------ FIELDs ----------------------------------------

    type: FeatureRelationType = Field(index=True)
    source_feature_id: uuid.UUID = Field(foreign_key="features.id", index=True)
    target_feature_id: uuid.UUID = Field(foreign_key="features.id", index=True)
    feature_model_version_id: uuid.UUID = Field(foreign_key="feature_model_versions.id")


# ===============================================================================
#  --- Modelo para la tabla física de las Relaciones entre Características ---
# ===============================================================================


class FeatureRelation(BaseTable, FeatureRelationBase, table=True):

    # ------------------ METADATA FOR TABLE ----------------------------------

    __tablename__ = "feature_relations"

    # ------------------ RELATIONSHIP ----------------------------------------

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


# ===================================================================================
#  --- Modelos para Entrada de datos de las Relaciones entre Características ---
# ===================================================================================


class FeatureRelationCreate(SQLModel):
    type: FeatureRelationType
    source_feature_id: uuid.UUID
    target_feature_id: uuid.UUID
    # La versión del modelo se infiere de las features, no se pasa directamente


class FeatureRelationUpdate(SQLModel):
    type: Optional[FeatureRelationType] = None
    source_feature_id: Optional[uuid.UUID] = None
    target_feature_id: Optional[uuid.UUID] = None


class FeatureRelationReplace(SQLModel):
    type: FeatureRelationType
    source_feature_id: uuid.UUID
    target_feature_id: uuid.UUID


# ===================================================================================
#  ---  Modelos para Respuestas de las Relaciones entre Características ---
# ===================================================================================


class FeatureRelationPublic(FeatureRelationBase):
    id: uuid.UUID
