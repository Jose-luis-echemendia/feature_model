"""Definición del modelo principal `FeatureModel` y sus esquemas.

Contiene la entidad que representa un conjunto de features agrupados
en un modelo de dominio. Incluye relaciones con `Domain`, `User` (owner),
features y colaboradores.
"""

import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models import PaginatedResponse, BaseTable
from .link_models import FeatureModelCollaborator

if TYPE_CHECKING:
    from .user import User
    from .domain import Domain
    from .feature_model_version import FeatureModelVersion


# ========================================================================
#              --- Modelo Base para FeatureModel ---
# ========================================================================


class FeatureModelBase(SQLModel):

    # ------------------ FIELDs ----------------------------------------

    name: str = Field(index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


# ========================================================================
#           --- Modelo de la Tabla de Base de Datos ---
# ========================================================================


class FeatureModel(BaseTable, FeatureModelBase, table=True):

    # ------------------ METADATA FOR TABLE ----------------------------------

    __tablename__ = "feature_model"

    # Relaciones
    domain_id: uuid.UUID = Field(foreign_key="domains.id", nullable=False)
    owner_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)

    # ------------------ RELATIONSHIP ----------------------------------------

    domain: "Domain" = Relationship(back_populates="feature_models")
    owner: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[FeatureModel.owner_id]"}
    )

    # Relación con las versiones del modelo
    versions: list["FeatureModelVersion"] = Relationship(
        back_populates="feature_model",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    collaborators: list["User"] = Relationship(
        back_populates="collaborating_feature_models",
        link_model=FeatureModelCollaborator,
    )


# ========================================================================================
#             --- Modelos para la API (Pydantic) ---
# ========================================================================================


class FeatureModelCreate(FeatureModelBase):
    domain_id: uuid.UUID


class FeatureModelUpdate(FeatureModelBase):
    name: Optional[str] = None
    description: Optional[str] = None


# ========================================================================
#       --- Modelos para Respuestas de los Modelos Característicos ---
# ========================================================================


class FeatureModelPublic(FeatureModelBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    domain_id: uuid.UUID
    created_at: datetime


class FeatureModelListResponse(PaginatedResponse[FeatureModelPublic]):
    pass
