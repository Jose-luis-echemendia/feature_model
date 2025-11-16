"""Tablas intermedias (association/link models) usadas en relaciones M2M.

Este módulo contiene pequeñas tablas de asociación que no requieren
entidades propias más allá de las claves foráneas. Se usan para modelar
relaciones many-to-many (collaborators, feature-tags, configuration-tags,
etc.).
"""

import uuid

from sqlmodel import Field, SQLModel


# ========================================================================
#     --- Modelos LINKs asociativos para relacionar tablas ---
# ========================================================================


class FeatureModelCollaborator(SQLModel, table=True):
    """
    Tabla de asociación que otorga permisos de edición a un usuario
    sobre un FeatureModel específico.
    """

    __tablename__ = "feature_model_collaborators"

    feature_model_id: uuid.UUID = Field(
        foreign_key="feature_model.id", primary_key=True
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", primary_key=True)


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
    """
    Tabla de asociación entre las etiquetas y las características
    """

    __tablename__ = "feature_tags"

    feature_id: uuid.UUID = Field(foreign_key="features.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)


class ConfigurationTagLink(SQLModel, table=True):
    """
    Tabla de asociación entre las etiquetas y las configuraciones
    """

    __tablename__ = "configuration_tags"

    configuration_id: uuid.UUID = Field(
        foreign_key="configurations.id", primary_key=True
    )
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)
