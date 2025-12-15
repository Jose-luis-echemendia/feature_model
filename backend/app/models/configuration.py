"""Modelos relacionados con las Configuraciones de un Feature Model.

Contiene los modelos de base, la tabla de base de datos `Configuration` y
los esquemas Pydantic/SQLModel usados por la API para crear, actualizar y
mostrar configuraciones (incluye relaciones con features y tags).
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from .common import BaseTable, PaginatedResponse
from .link_models import ConfigurationFeatureLink, ConfigurationTagLink

if TYPE_CHECKING:
    from .feature_model_version import FeatureModelVersion
    from .feature import Feature, FeaturePublicWithChildren
    from .tag import Tag, TagPublic


# ========================================================================
#           --- Modelo de Configuración base ---
# ========================================================================


# --- Modelo Principal de Configuration ---
class ConfigurationBase(SQLModel):

    # ------------------ FIELDs ----------------------------------------

    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None)
    feature_model_version_id: uuid.UUID = Field(foreign_key="feature_model_versions.id")
    feature_model_version_id: uuid.UUID = Field(
        foreign_key="feature_model_versions.id", index=True
    )


# ========================================================================
#      --- Modelo para la tabla física de Configuraciones ---
# ========================================================================

class Configuration(BaseTable, ConfigurationBase, table=True):

    # ------------------ METADATA FOR TABLE ----------------------------------

    __tablename__ = "configurations"

    # ------------------ RELATIONSHIP ----------------------------------------

    tags: list["Tag"] = Relationship(
        back_populates="configurations", link_model=ConfigurationTagLink
    )

    # Relación de vuelta a FeatureModelVersion
    feature_model_version: "FeatureModelVersion" = Relationship(
        back_populates="configurations"
    )

    # Relación muchos-a-muchos con Feature, usando la tabla intermedia
    features: list["Feature"] = Relationship(
        back_populates="configurations", link_model=ConfigurationFeatureLink
    )


# ========================================================================
#       --- Modelos para Entrada de datos de Configuraciones ---
# ========================================================================

class ConfigurationCreate(ConfigurationBase):
    # Al crear una configuración, también pasaremos la lista de IDs de features
    feature_ids: list[uuid.UUID] = []


class ConfigurationUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None)
    feature_ids: Optional[list[uuid.UUID]] = None



# ========================================================================
#           --- Modelos para Respuestas de Configuraciones ---
# ========================================================================

class ConfigurationPublic(ConfigurationBase):
    id: uuid.UUID


class ConfigurationListResponse(PaginatedResponse[ConfigurationPublic]):
    pass


class ConfigurationPublicWithFeatures(ConfigurationPublic):
    features: list["FeaturePublicWithChildren"] = []
    tags: list["TagPublic"] = []
