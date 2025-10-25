import uuid

from sqlmodel import Field, SQLModel


class ConfigurationFeatureLink(SQLModel, table=True):
    """
    Association table between Configuration and Feature.
    """

    __tablename__ = "configuration_features"

    configuration_id: uuid.UUID = Field(
        foreign_key="configurations.id", primary_key=True
    )
    feature_id: uuid.UUID = Field(foreign_key="features.id", primary_key=True)


class FeatureTagLink(SQLModel, table=True):
    __tablename__ = "feature_tags"
    feature_id: uuid.UUID = Field(foreign_key="features.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)


class ConfigurationTagLink(SQLModel, table=True):
    __tablename__ = "configuration_tags"
    configuration_id: uuid.UUID = Field(foreign_key="configurations.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)