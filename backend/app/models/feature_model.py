import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel, Column, JSON

from app.models.common import PaginatedResponse

# Adelantamos la declaración de User y Domain para evitar importaciones circulares
from app.models import User, Feature, Domain, BaseTable


# ---------------------------------------------------------------------------
# Modelo Base para FeatureModel
# ---------------------------------------------------------------------------
class FeatureModelBase(SQLModel):
    name: str = Field(index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


# ---------------------------------------------------------------------------
# Modelo de la Tabla de Base de Datos
# ---------------------------------------------------------------------------
class FeatureModel(BaseTable, FeatureModelBase, table=True):
    
    __tablename__ = "feature_model"

    # Relaciones
    domain_id: uuid.UUID = Field(foreign_key="domain.id", nullable=False)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)

    domain: "Domain" = Relationship(back_populates="feature_models")
    owner: "User" = Relationship()
    
    # Relación con las características (features)
    features: list["Feature"] = Relationship(back_populates="feature_model", sa_relationship_kwargs={"cascade": "all, delete-orphan"})



# ---------------------------------------------------------------------------
# Modelos para la API (Pydantic)
# ---------------------------------------------------------------------------
class FeatureModelCreate(FeatureModelBase):
    domain_id: uuid.UUID


class FeatureModelUpdate(FeatureModelBase):
    name: Optional[str] = None
    description: Optional[str] = None


class FeatureModelPublic(FeatureModelBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    domain_id: uuid.UUID
    created_at: datetime


class FeatureModelListResponse(PaginatedResponse[FeatureModelPublic]):
    pass
