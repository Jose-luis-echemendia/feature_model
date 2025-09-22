import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .common import BaseTable

if TYPE_CHECKING:
    from .domain import Domain, DomainPublic
    from .feature import Feature, FeaturePublic
    from .configuration import Configuration, ConfigurationPublic


class FeatureModelBase(SQLModel):
    name: str = Field(max_length=100)
    description: str | None = Field(default=None)
    domain_id: uuid.UUID = Field(foreign_key="domain.id")


class FeatureModelCreate(FeatureModelBase):
    pass


class FeatureModelUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None)


class FeatureModel(BaseTable, FeatureModelBase, table=True):
    
    __tablename__ = "feature_models"
    
    # Relación de vuelta a Domain
    domain: "Domain" = Relationship(back_populates="feature_models")
    
    # Relación uno-a-muchos con Feature
    features: list["Feature"] = Relationship(back_populates="feature_model")
    
    # Relación uno-a-muchos con Configuration
    configurations: list["Configuration"] = Relationship(back_populates="feature_model")


class FeatureModelPublic(FeatureModelBase):
    id: uuid.UUID

class FeatureModelPublicWithDetails(FeatureModelPublic):
    domain: "DomainPublic"
    features: list["FeaturePublic"] = []
    configurations: list["ConfigurationPublic"] = []