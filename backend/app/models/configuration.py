import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .common import BaseTable

if TYPE_CHECKING:
    from .feature_model import FeatureModel
    from .feature import Feature, FeaturePublic


# --- Modelo para la Tabla Intermedia (Junction Table) ---
class ConfigurationFeature(SQLModel, table=True):
    
    __tablename__ = "configuration_features"
    
    # No hereda de BaseTable, es una tabla de enlace simple
    configuration_id: uuid.UUID = Field(foreign_key="configuration.id", primary_key=True)
    feature_id: uuid.UUID = Field(foreign_key="feature.id", primary_key=True)
    # enabled: bool = Field(default=True) # Puedes añadir campos extra a la relación


# --- Modelo Principal de Configuration ---
class ConfigurationBase(SQLModel):
    name: str = Field(max_length=100)
    description: str | None = Field(default=None)
    feature_model_id: uuid.UUID = Field(foreign_key="feature_model.id")


class ConfigurationCreate(ConfigurationBase):
    # Al crear una configuración, también pasaremos la lista de IDs de features
    feature_ids: list[uuid.UUID] = []


class ConfigurationUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None)
    feature_ids: list[uuid.UUID] | None = None


class Configuration(BaseTable, ConfigurationBase, table=True):
    
    __tablename__ = "configurations"
    
    # Relación de vuelta a FeatureModel
    feature_model: "FeatureModel" = Relationship(back_populates="configurations")
    
    # Relación muchos-a-muchos con Feature, usando la tabla intermedia
    features: list["Feature"] = Relationship(
        back_populates="configurations", 
        link_model=ConfigurationFeature
    )


class ConfigurationPublic(ConfigurationBase):
    id: uuid.UUID


class ConfigurationPublicWithFeatures(ConfigurationPublic):
    features: list["FeaturePublic"] = []