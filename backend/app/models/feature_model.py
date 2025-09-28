import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.common import PaginatedResponse

# Adelantamos la declaración de User y Domain para evitar importaciones circulares
from app.models.user import User
from app.models.domain import Domain


# ---------------------------------------------------------------------------
# Modelo Base para FeatureModel
# ---------------------------------------------------------------------------
class FeatureModelBase(SQLModel):
    name: str = Field(index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


# ---------------------------------------------------------------------------
# Modelo de la Tabla de Base de Datos
# ---------------------------------------------------------------------------
class FeatureModel(FeatureModelBase, table=True):
    __tablename__ = "feature_model"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None)

    # Relaciones
    domain_id: uuid.UUID = Field(foreign_key="domain.id", nullable=False)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)

    domain: "Domain" = Relationship(back_populates="feature_models")
    owner: "User" = Relationship()


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
