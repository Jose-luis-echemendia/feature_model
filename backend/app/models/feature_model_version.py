import uuid
from typing import TYPE_CHECKING, Any

from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy.dialects.postgresql import JSONB

from .common import BaseTable

if TYPE_CHECKING:
    from .feature_model import FeatureModel
    from .feature import Feature
    from .feature_group import FeatureGroup
    from .feature_relation import FeatureRelation
    from .configuration import Configuration
    from .user import User


class FeatureModelVersionBase(SQLModel):
    version_number: int = Field(default=1, index=True)
    is_active: bool = Field(default=False)
    snapshot: dict[str, Any] | None = Field(default=None, sa_column=Column(JSONB))
    feature_model_id: uuid.UUID = Field(foreign_key="feature_model.id")


class FeatureModelVersionCreate(SQLModel):
    feature_model_id: uuid.UUID


class FeatureModelVersionUpdate(SQLModel):
    is_active: bool | None = None


class FeatureModelVersion(BaseTable, FeatureModelVersionBase, table=True):
    __tablename__ = "feature_model_versions"

    feature_model: "FeatureModel" = Relationship(back_populates="versions")

    # Relación con el usuario que creó la versión
    created_by_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    created_by: "User" = Relationship()

    # Relaciones de vuelta desde los elementos que pertenecen a esta versión
    features: list["Feature"] = Relationship(back_populates="feature_model_version")
    feature_groups: list["FeatureGroup"] = Relationship(
        back_populates="feature_model_version"
    )
    feature_relations: list["FeatureRelation"] = Relationship(
        back_populates="feature_model_version"
    )
    configurations: list["Configuration"] = Relationship(
        back_populates="feature_model_version"
    )


class FeatureModelVersionPublic(FeatureModelVersionBase):
    id: uuid.UUID
    created_at: Any  # Para que Pydantic lo valide
    created_by_id: uuid.UUID | None
