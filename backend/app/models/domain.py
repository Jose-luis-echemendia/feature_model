"""Modelos que representan dominios de Feature Models.

Un `Domain` agrupa varios FeatureModels relacionados por un mismo dominio de
aplicación (por ejemplo: 'dominio educativo', 'dominio financiero'). Aquí se
definen las estructuras para base de datos y los esquemas de entrada/salida
usados por la API.
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from .common import BaseTable, PaginatedResponse

# Evita importaciones circulares para las anotaciones de tipo
if TYPE_CHECKING:
    from .feature_model import FeatureModel, FeatureModelPublic


# ========================================================================
#        --- Propiedades compartidas (Modelo Base) para Domain ---
# ========================================================================

class DomainBase(SQLModel):

    # ------------------ FIELDs ----------------------------------------

    name: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None)


# ========================================================================
#        --- Modelo de la base de datos para Domain ---
# ========================================================================
class Domain(BaseTable, DomainBase, table=True):

    # ------------------ METADATA FOR TABLE ----------------------------------

    __tablename__ = "domains"

    # ------------------ RELATIONSHIP ----------------------------------------    

    # Relación uno-a-muchos: Un dominio tiene muchos modelos de características
    feature_models: list["FeatureModel"] = Relationship(back_populates="domain")


# ========================================================================
#        --- Modelos para Entrada de Datos (API Input) para Domain ---
# ========================================================================


# Propiedades para la creación vía API
class DomainCreate(DomainBase):
    pass


# Propiedades para la actualización vía API (todas opcionales)
class DomainUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None)


# ========================================================================
#           --- Modelos para Salida de Datos (API Responses) ---
# ========================================================================


# Propiedades para retornar vía API
class DomainPublic(DomainBase):
    id: uuid.UUID


class DomainListResponse(PaginatedResponse[DomainPublic]):
    pass


# Modelo público con relaciones anidadas
class DomainPublicWithFeatureModels(DomainPublic):
    feature_models: list["FeatureModelPublic"] = []
