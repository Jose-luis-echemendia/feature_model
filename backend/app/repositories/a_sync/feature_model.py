from uuid import UUID
from typing import Optional
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import FeatureModel, FeatureModelCreate, FeatureModelUpdate
from app.interfaces import IFeatureModelRepositoryAsync
from app.repositories.base import BaseFeatureModelRepository


class FeatureModelRepositoryAsync(
    BaseFeatureModelRepository, IFeatureModelRepositoryAsync
):
    """Implementación asíncrona del repositorio de feature models."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: FeatureModelCreate, owner_id: UUID) -> FeatureModel:
        """Crear un nuevo feature model."""
        # Verificar unicidad del nombre dentro del dominio
        existing = await self.get_by_name(data.name, data.domain_id)
        self.validate_name_unique_in_domain(existing, name=data.name)

        obj = FeatureModel.model_validate(data, update={"owner_id": owner_id})
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, feature_model_id: UUID) -> FeatureModel | None:
        """Obtener un feature model por ID con su dominio y versiones."""
        stmt = (
            select(FeatureModel)
            .options(
                selectinload(FeatureModel.domain), selectinload(FeatureModel.versions)
            )
            .where(FeatureModel.id == feature_model_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str, domain_id: UUID) -> FeatureModel | None:
        """Obtener un feature model por nombre dentro de un dominio específico."""
        stmt = select(FeatureModel).where(
            FeatureModel.name == name, FeatureModel.domain_id == domain_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[FeatureModel]:
        """Obtener lista de todos los feature models con paginación, su dominio y versiones."""
        stmt = (
            select(FeatureModel)
            .options(
                selectinload(FeatureModel.domain), selectinload(FeatureModel.versions)
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_domain(
        self, domain_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[FeatureModel]:
        """Obtener lista de feature models para un dominio específico con paginación, su dominio y versiones."""
        stmt = (
            select(FeatureModel)
            .options(
                selectinload(FeatureModel.domain), selectinload(FeatureModel.versions)
            )
            .where(FeatureModel.domain_id == domain_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(
        self, db_feature_model: FeatureModel, data: FeatureModelUpdate
    ) -> FeatureModel:
        """Actualizar un feature model existente."""
        update_data = data.model_dump(exclude_unset=True)

        # Si se está actualizando el nombre, verificar unicidad en el dominio
        if "name" in update_data and update_data["name"] != db_feature_model.name:
            existing = await self.get_by_name(
                update_data["name"], db_feature_model.domain_id
            )
            self.validate_name_unique_in_domain(
                existing, db_feature_model.id, update_data["name"]
            )

        db_feature_model.sqlmodel_update(update_data)
        self.session.add(db_feature_model)
        await self.session.commit()
        await self.session.refresh(db_feature_model)
        return db_feature_model

    async def delete(self, db_feature_model: FeatureModel) -> FeatureModel:
        """Eliminar un feature model."""
        await self.session.delete(db_feature_model)
        await self.session.commit()
        return db_feature_model

    async def exists(self, feature_model_id: UUID) -> bool:
        """Verificar si un feature model existe."""
        result = await self.session.get(FeatureModel, feature_model_id)
        return result is not None

    async def count(self, domain_id: Optional[UUID] = None) -> int:
        """Contar el número total de feature models, opcionalmente filtrando por dominio."""
        stmt = select(func.count()).select_from(FeatureModel)
        if domain_id:
            stmt = stmt.where(FeatureModel.domain_id == domain_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def has_versions_with_features(self, feature_model_id: UUID) -> bool:
        """Verificar si el feature model tiene versiones con características asociadas."""
        from app.models import FeatureModelVersion, Feature

        stmt = (
            select(func.count())
            .select_from(Feature)
            .join(FeatureModelVersion)
            .where(FeatureModelVersion.feature_model_id == feature_model_id)
        )
        result = await self.session.execute(stmt)
        count = result.scalar_one()
        return count > 0

    async def has_versions_with_configurations(self, feature_model_id: UUID) -> bool:
        """Verificar si el feature model tiene versiones con configuraciones asociadas."""
        from app.models import FeatureModelVersion, Configuration

        stmt = (
            select(func.count())
            .select_from(Configuration)
            .join(FeatureModelVersion)
            .where(FeatureModelVersion.feature_model_id == feature_model_id)
        )
        result = await self.session.execute(stmt)
        count = result.scalar_one()
        return count > 0

    async def can_be_deleted(self, feature_model_id: UUID) -> tuple[bool, str]:
        """
        Verificar si un feature model puede ser eliminado.
        Retorna una tupla (puede_eliminar, mensaje_error).
        """
        has_features = await self.has_versions_with_features(feature_model_id)
        if has_features:
            return False, "Cannot delete feature model: it has associated features"

        has_configurations = await self.has_versions_with_configurations(
            feature_model_id
        )
        if has_configurations:
            return (
                False,
                "Cannot delete feature model: it has associated configurations",
            )

        return True, ""

    async def activate(self, db_feature_model: FeatureModel) -> FeatureModel:
        """Activar un feature model."""
        db_feature_model.is_active = True
        self.session.add(db_feature_model)
        await self.session.commit()
        await self.session.refresh(db_feature_model)
        return db_feature_model

    async def deactivate(self, db_feature_model: FeatureModel) -> FeatureModel:
        """Desactivar un feature model."""
        db_feature_model.is_active = False
        self.session.add(db_feature_model)
        await self.session.commit()
        await self.session.refresh(db_feature_model)
        return db_feature_model
