from uuid import UUID
from typing import Optional
from sqlmodel import Session, select, func

from app.models import (
    Configuration,
    ConfigurationCreate,
    ConfigurationUpdate,
    Feature,
)
from app.interfaces import IConfigurationRepositorySync
from app.repositories.base import BaseConfigurationRepository


class ConfigurationRepositorySync(
    BaseConfigurationRepository, IConfigurationRepositorySync
):
    """Implementación síncrona del repositorio de configuraciones."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, data: ConfigurationCreate) -> Configuration:
        """
        Crea una nueva configuración y asocia las features.
        """
        # Obtener las features de la base de datos a partir de los IDs
        features = self.session.exec(
            select(Feature).where(Feature.id.in_(data.feature_ids))
        ).all()

        # Crear el objeto de configuración sin los feature_ids
        db_obj = Configuration.model_validate(data, update={"features": features})

        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def get(self, configuration_id: UUID) -> Configuration | None:
        """Obtener una configuración por su ID."""
        return self.session.get(Configuration, configuration_id)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Configuration]:
        """Obtener lista de configuraciones con paginación."""
        stmt = select(Configuration).offset(skip).limit(limit)
        return self.session.exec(stmt).all()

    def update(
        self, db_configuration: Configuration, data: ConfigurationUpdate
    ) -> Configuration:
        """
        Actualiza una configuración, incluyendo sus features asociadas.
        """
        # Actualiza los campos simples
        update_data = data.model_dump(exclude_unset=True)
        db_configuration.sqlmodel_update(update_data)

        # Actualiza las features si se proporcionan
        if "feature_ids" in update_data and update_data["feature_ids"] is not None:
            features = self.session.exec(
                select(Feature).where(Feature.id.in_(update_data["feature_ids"]))
            ).all()
            db_configuration.features = features

        self.session.add(db_configuration)
        self.session.commit()
        self.session.refresh(db_configuration)
        return db_configuration

    def delete(self, db_configuration: Configuration) -> None:
        """Eliminar una configuración."""
        self.session.delete(db_configuration)
        self.session.commit()

    def exists(self, configuration_id: UUID) -> bool:
        """Verificar si una configuración existe."""
        result = self.session.get(Configuration, configuration_id)
        return result is not None

    def count(self) -> int:
        """Obtener el número total de configuraciones."""
        stmt = select(func.count()).select_from(Configuration)
        return self.session.exec(stmt).one()
