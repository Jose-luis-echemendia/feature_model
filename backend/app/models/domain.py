from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

from .common import BaseTable


class DomainBase(SQLModel):
    name: str
    description: Optional[str] = None


class DomainCreate(DomainBase):
    pass


class DomainUpdate(DomainBase):
    pass


class Domain(BaseTable, DomainBase, table=True):

    __tablename__ = "domains"


    feature_models: list["FeatureModel"] = Relationship(back_populates="domain")
