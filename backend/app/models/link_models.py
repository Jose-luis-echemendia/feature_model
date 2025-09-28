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
