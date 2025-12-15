"""Modelos para representar restricciones lógicas (constraints) del modelo.

Aquí se define la tabla `Constraint` que almacena la representación textual
y la forma normal conjuntiva (CNF) de restricciones que afectan a una
versión del modelo de características.
"""

import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, Relationship, SQLModel

from .common import BaseTable

if TYPE_CHECKING:
    from .feature_model_version import FeatureModelVersion


# ========================================================================
#           --- Modelo de Restricciones base ---
# ========================================================================

class ConstraintBase(SQLModel):
    
    # ------------------ FIELDs ----------------------------------------
    
    description: Optional[str] = Field(default=None)
    expr_text: str
    expr_cnf: Optional[list[list[int]]] = Field(default=None, sa_column=Column(JSONB))
    feature_model_version_id: uuid.UUID = Field(foreign_key="feature_model_versions.id")


# ========================================================================
#    --- Modelo para la tabla física de las Restricciones ---
# ========================================================================

class Constraint(BaseTable, ConstraintBase, table=True):
    
    # ------------------ METADATA FOR TABLE ----------------------------------

    __tablename__ = "constraints"
    
    
    # ------------------ RELATIONSHIP ----------------------------------------

    feature_model_version: "FeatureModelVersion" = Relationship(
        back_populates="constraints"
    )


# ========================================================================
#           --- Modelos para Entrada de datos de las Restricciones ---
# ========================================================================

class ConstraintCreate(SQLModel):
    feature_model_version_id: uuid.UUID
    description: Optional[str] = None
    expr_text: str


# ========================================================================
#           --- Modelos para Respuestas de las Restricciones ---
# ========================================================================

class ConstraintPublic(ConstraintBase):
    id: uuid.UUID
    created_at: Any
    created_by_id: Optional[uuid.UUID]
