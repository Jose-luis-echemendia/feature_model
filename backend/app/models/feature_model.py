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
    is_active: Optional[bool] = None


# ========================================================================
#       --- Modelos para Respuestas de los Modelos Característicos ---
# ========================================================================


class VersionInfo(SQLModel):
    """Información básica de una versión."""

    id: uuid.UUID
    version_number: int
    status: str
    created_at: datetime


class FeatureModelPublic(FeatureModelBase):
    """Schema completo para detalle de un feature model individual."""

    id: uuid.UUID
    owner_id: uuid.UUID
    domain_id: uuid.UUID
    domain_name: str
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    versions_count: int
    versions: list[VersionInfo]


class LatestVersionInfo(SQLModel):
    """Información de la última versión para el listado."""

    id: uuid.UUID
    version_number: int
    status: str


class FeatureModelListItem(SQLModel):
    """Schema optimizado para listado de feature models (sin descripción)."""

    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    domain_id: uuid.UUID
    domain_name: str
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    versions_count: int
    latest_version: Optional[LatestVersionInfo]


class FeatureModelListResponse(PaginatedResponse[FeatureModelListItem]):
    pass
