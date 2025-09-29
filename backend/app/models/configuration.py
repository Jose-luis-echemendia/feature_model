import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .common import BaseTable, PaginatedResponse
from .link_models import ConfigurationFeatureLink

if TYPE_CHECKING:
    from .feature_model_version import FeatureModelVersion
    from .feature import Feature, FeaturePublicWithChildren


# --- Modelo Principal de Configuration ---
class ConfigurationBase(SQLModel):
    name: str = Field(max_length=100)
    description: str | None = Field(default=None)
    feature_model_version_id: uuid.UUID = Field(foreign_key="feature_model_versions.id")
    feature_model_version_id: uuid.UUID = Field(
        foreign_key="feature_model_versions.id", index=True
    )


class ConfigurationCreate(ConfigurationBase):
    # Al crear una configuración, también pasaremos la lista de IDs de features
    feature_ids: list[uuid.UUID] = []


class ConfigurationUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None)
    feature_ids: list[uuid.UUID] | None = None


class Configuration(BaseTable, ConfigurationBase, table=True):

    __tablename__ = "configurations"

    # Relación de vuelta a FeatureModelVersion
    feature_model_version: "FeatureModelVersion" = Relationship(
        back_populates="configurations"
    )

    # Relación muchos-a-muchos con Feature, usando la tabla intermedia
    features: list["Feature"] = Relationship(
        back_populates="configurations", link_model=ConfigurationFeatureLink
    )


class ConfigurationPublic(ConfigurationBase):
    id: uuid.UUID


class ConfigurationListResponse(PaginatedResponse[ConfigurationPublic]):
    pass


class ConfigurationPublicWithFeatures(ConfigurationPublic):
    features: list["FeaturePublicWithChildren"] = []
