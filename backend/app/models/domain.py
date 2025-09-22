import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .common import BaseTable

# Evita importaciones circulares para las anotaciones de tipo
if TYPE_CHECKING:
    from .feature_model import FeatureModel, FeatureModelPublic


# Propiedades compartidas
class DomainBase(SQLModel):
    name: str = Field(max_length=100, index=True)
    description: str | None = Field(default=None)


# Propiedades para la creación vía API
class DomainCreate(DomainBase):
    pass


# Propiedades para la actualización vía API (todas opcionales)
class DomainUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None)


# Modelo de la base de datos
class Domain(BaseTable, DomainBase, table=True):
    
    __tablename__ = "domains"
    
    # Relación uno-a-muchos: Un dominio tiene muchos modelos de características
    feature_models: list["FeatureModel"] = Relationship(back_populates="domain")


# Propiedades para retornar vía API
class DomainPublic(DomainBase):
    id: uuid.UUID

# Modelo público con relaciones anidadas
class DomainPublicWithFeatureModels(DomainPublic):
    feature_models: list["FeatureModelPublic"] = []