
import uuid
from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

from .common import BaseTable
from .link_models import FeatureTagLink, ConfigurationTagLink

if TYPE_CHECKING:
    from .feature import Feature
    from .configuration import Configuration

class TagBase(SQLModel):
    name: str = Field(unique=True, index=True, max_length=50)
    description: str | None = Field(default=None)

class Tag(BaseTable, TagBase, table=True):
    __tablename__ = "tags"

    # Relaciones de vuelta
    features: list["Feature"] = Relationship(back_populates="tags", link_model=FeatureTagLink)
    configurations: list["Configuration"] = Relationship(back_populates="tags", link_model=ConfigurationTagLink)

class TagCreate(TagBase):
    pass

class TagPublic(TagBase):
    id: uuid.UUID