import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy.dialects.postgresql import JSONB

from .common import BaseTable
from app.enums import ModelStatus

if TYPE_CHECKING:
    from .feature_model import FeatureModel
    from .feature import Feature
    from .feature_group import FeatureGroup
    from .constraint import Constraint
    from .feature_relation import FeatureRelation
    from .configuration import Configuration
    from .user import User


class FeatureModelVersionBase(SQLModel):
    version_number: int = Field(default=1, index=True)
    snapshot: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    feature_model_id: uuid.UUID = Field(foreign_key="feature_model.id")
    status: ModelStatus = Field(default=ModelStatus.DRAFT)

class FeatureModelVersionCreate(SQLModel):
    feature_model_id: uuid.UUID


class FeatureModelVersionUpdate(SQLModel):
    is_active: Optional[bool] = None


class FeatureModelVersion(BaseTable, FeatureModelVersionBase, table=True):

    __tablename__ = "feature_model_versions"

    feature_model: "FeatureModel" = Relationship(back_populates="versions")

    # Relaciones de vuelta desde los elementos que pertenecen a esta versión
    features: list["Feature"] = Relationship(back_populates="feature_model_version")
    feature_groups: list["FeatureGroup"] = Relationship(
        back_populates="feature_model_version"
    )
    feature_relations: list["FeatureRelation"] = Relationship(
        back_populates="feature_model_version"
    )
    constraints: list["Constraint"] = Relationship(
        back_populates="feature_model_version"
    )
    configurations: list["Configuration"] = Relationship(
        back_populates="feature_model_version"
    )


class FeatureModelVersionPublic(FeatureModelVersionBase):
    id: uuid.UUID
    created_at: Any  # Para que Pydantic lo valide
    created_by_id: Optional[uuid.UUID]
