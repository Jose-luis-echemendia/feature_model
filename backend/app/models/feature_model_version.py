"""Versiones de `FeatureModel` y estructuras relacionadas.

Cada `FeatureModel` puede tener varias versiones (`FeatureModelVersion`) que
almacenan snapshots, estado y relaciones a las features/constraints/
configurations correspondientes. Aquí se definen las tablas y esquemas
para la creación y publicación de versiones.
"""

import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy.dialects.postgresql import JSONB

from .common import BaseTable
from app.enums import ModelStatus

if TYPE_CHECKING:
    from .feature import Feature
    from .feature_model import FeatureModel
    from .feature_group import FeatureGroup
    from .feature_relation import FeatureRelation
    from .constraint import Constraint
    from .configuration import Configuration
    
    
# ========================================================================
#  --- Modelo base para el versionado de los Modelos Característicos ---
# ========================================================================


class FeatureModelVersionBase(SQLModel):
    
    # ------------------ FIELDs ----------------------------------------

    version_number: int = Field(default=1, index=True)
    snapshot: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    feature_model_id: uuid.UUID = Field(foreign_key="feature_model.id")
    status: ModelStatus = Field(default=ModelStatus.DRAFT)



# =======================================================================================
#  --- Modelo para la tabla física de las versiones de los Modelos Característicos ---
# =======================================================================================

class FeatureModelVersion(BaseTable, FeatureModelVersionBase, table=True):

    # ------------------ METADATA FOR TABLE ----------------------------------

    __tablename__ = "feature_model_versions"
    
    
    # ------------------ RELATIONSHIP ----------------------------------------

    feature_model: "FeatureModel" = Relationship(back_populates="versions")

    # Relaciones de vuelta desde los elementos que pertenecen a esta versión
    features: list["Feature"] = Relationship(back_populates="feature_model_version")
    feature_groups: list["FeatureGroup"] = Relationship(
        back_populates="feature_model_version"
    )
    feature_relations: list["FeatureRelation"] = Relationship(
        back_populates="feature_model_version"
    )
    constraints: list["Constraint"] = Relationship(
        back_populates="feature_model_version"
    )
    configurations: list["Configuration"] = Relationship(
        back_populates="feature_model_version"
    )


# ===========================================================================================
#  --- Modelos para Entrada de datos de las versiones de los Modelos Característicos ---
# ===========================================================================================

class FeatureModelVersionCreate(SQLModel):
    feature_model_id: uuid.UUID


class FeatureModelVersionUpdate(SQLModel):
    is_active: Optional[bool] = None


# ========================================================================================
#  --- Modelos para Respuestas de las versiones de los Modelos Característicos ---
# ========================================================================================

class FeatureModelVersionPublic(FeatureModelVersionBase):
    id: uuid.UUID
    created_at: Any  # Para que Pydantic lo valide
    created_by_id: Optional[uuid.UUID]
