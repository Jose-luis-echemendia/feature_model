import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, Relationship, SQLModel

from .common import BaseTable

if TYPE_CHECKING:
    from .feature_model_version import FeatureModelVersion
    from .user import User


class ConstraintBase(SQLModel):
    description: str | None = Field(default=None)
    expr_text: str
    expr_cnf: list[list[int]] | None = Field(default=None, sa_column=Column(JSONB))
    feature_model_version_id: uuid.UUID = Field(foreign_key="feature_model_versions.id")


class Constraint(BaseTable, ConstraintBase, table=True):
    __tablename__ = "constraints"

    feature_model_version: "FeatureModelVersion" = Relationship(
        back_populates="constraints"
    )


class ConstraintCreate(SQLModel):
    feature_model_version_id: uuid.UUID
    description: str | None = None
    expr_text: str


class ConstraintPublic(ConstraintBase):
    id: uuid.UUID
    created_at: Any
    created_by_id: uuid.UUID | None
