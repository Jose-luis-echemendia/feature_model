from uuid import UUID
from typing import Optional
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import (
    Configuration,
    ConfigurationCreate,
    ConfigurationUpdate,
    Feature,
)
from app.interfaces import IConfigurationRepositoryAsync
from app.repositories.base import BaseConfigurationRepository


class ConfigurationRepositoryAsync(
    BaseConfigurationRepository, IConfigurationRepositoryAsync
):
    """Implementación asíncrona del repositorio de configuraciones."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: ConfigurationCreate) -> Configuration:
        """
        Crea una nueva configuración y asocia las features.
        """
        # Obtener las features de la base de datos a partir de los IDs
        stmt = select(Feature).where(Feature.id.in_(data.feature_ids))
        result = await self.session.execute(stmt)
        features = result.scalars().all()

        # Crear el objeto de configuración sin los feature_ids
        db_obj = Configuration.model_validate(data, update={"features": features})

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get(self, configuration_id: UUID) -> Configuration | None:
        """Obtener una configuración por su ID."""
        return await self.session.get(Configuration, configuration_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Configuration]:
        """Obtener lista de configuraciones con paginación."""
        stmt = select(Configuration).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(
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
            stmt = select(Feature).where(Feature.id.in_(update_data["feature_ids"]))
            result = await self.session.execute(stmt)
            features = result.scalars().all()
            db_configuration.features = features

        self.session.add(db_configuration)
        await self.session.commit()
        await self.session.refresh(db_configuration)
        return db_configuration

    async def delete(self, db_configuration: Configuration) -> None:
        """Eliminar una configuración."""
        await self.session.delete(db_configuration)
        await self.session.commit()

    async def exists(self, configuration_id: UUID) -> bool:
        """Verificar si una configuración existe."""
        result = await self.session.get(Configuration, configuration_id)
        return result is not None

    async def count(self) -> int:
        """Obtener el número total de configuraciones."""
        stmt = select(func.count()).select_from(Configuration)
        result = await self.session.execute(stmt)
        return result.scalar_one()
