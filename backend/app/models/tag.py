"""Modelos para etiquetas (tags) y sus relaciones con features/configurations.

Las etiquetas permiten clasificar features y configuraciones con texto
libre; este módulo define la tabla `Tag` y los esquemas de creación y
presentación usados por la API.
"""

import uuid

from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship

# --- imports APP ---
from .common import BaseTable
from .link_models import FeatureTagLink, ConfigurationTagLink

if TYPE_CHECKING:
    from .feature import Feature
    from .configuration import Configuration


# ========================================================================
#           --- Modelo de Etiquetas base ---
# ========================================================================
class TagBase(SQLModel):

    # ------------------ FIELDs ----------------------------------------

    name: str = Field(unique=True, index=True, max_length=50)
    description: Optional[str] = Field(default=None)


# ========================================================================
#           --- Modelo para la tabla física de Etiquetas ---
# ========================================================================
class Tag(BaseTable, TagBase, table=True):

    # ------------------ METADATA FOR TABLE ----------------------------------
    __tablename__ = "tags"

    # ------------------ RELATIONSHIP ----------------------------------------

    # Relaciones de vuelta
    features: list["Feature"] = Relationship(
        back_populates="tags", link_model=FeatureTagLink
    )
    configurations: list["Configuration"] = Relationship(
        back_populates="tags", link_model=ConfigurationTagLink
    )


# ========================================================================
#        --- Modelos para Entrada de datos de las Etiquetas ---
# ========================================================================


class TagCreate(TagBase):
    pass


# ========================================================================
#           --- Modelos para Respuestas de Etiquetas ---
# ========================================================================


class TagPublic(TagBase):
    id: uuid.UUID
