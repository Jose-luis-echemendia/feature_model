from uuid import UUID
from typing import Optional
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Domain, DomainCreate, DomainUpdate, DomainPublicWithFeatureModels
from app.interfaces import IDomainRepositoryAsync
from app.repositories.base import BaseDomainRepository


class DomainRepositoryAsync(BaseDomainRepository, IDomainRepositoryAsync):
    """Implementación asíncrona del repositorio de dominios."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: DomainCreate) -> Domain:
        """Crear un nuevo dominio."""
        # Verificar unicidad del nombre
        existing = await self.get_by_name(data.name)
        self.validate_name_unique(existing)

        obj = Domain.model_validate(data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, domain_id: UUID) -> Domain | None:
        """Obtener un dominio por ID."""
        return await self.session.get(Domain, domain_id)

    async def get_by_name(self, name: str) -> Domain | None:
        """Obtener un dominio por nombre."""
        stmt = select(Domain).where(Domain.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Domain]:
        """Obtener lista de dominios con paginación."""
        stmt = select(Domain).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, db_domain: Domain, data: DomainUpdate) -> Domain:
        """Actualizar un dominio existente."""
        update_data = data.model_dump(exclude_unset=True)

        # Si se está actualizando el nombre, verificar unicidad
        if "name" in update_data and update_data["name"] != db_domain.name:
            existing = await self.get_by_name(update_data["name"])
            self.validate_name_unique(existing, db_domain.id)

        db_domain.sqlmodel_update(update_data)
        self.session.add(db_domain)
        await self.session.commit()
        await self.session.refresh(db_domain)
        return db_domain

    async def delete(self, db_domain: Domain) -> Domain:
        """Eliminar un dominio."""
        await self.session.delete(db_domain)
        await self.session.commit()
        return db_domain

    async def get_with_feature_models(
        self, domain_id: UUID
    ) -> DomainPublicWithFeatureModels | None:
        """Obtener un dominio con sus modelos de características relacionados."""
        domain = await self.session.get(Domain, domain_id)
        if not domain:
            return None

        # SQLModel carga las relaciones automáticamente cuando se acceden
        return DomainPublicWithFeatureModels.model_validate(domain)

    async def exists(self, domain_id: UUID) -> bool:
        """Verificar si un dominio existe."""
        result = await self.session.get(Domain, domain_id)
        return result is not None

    async def count(self) -> int:
        """Obtener el número total de dominios."""
        stmt = select(func.count()).select_from(Domain)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def search(
        self, search_term: str, skip: int = 0, limit: int = 100
    ) -> list[Domain]:
        """Buscar dominios por nombre o descripción."""
        stmt = (
            select(Domain)
            .where(
                (Domain.name.ilike(f"%{search_term}%"))
                | (Domain.description.ilike(f"%{search_term}%"))
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_search(self, search_term: str) -> int:
        """Contar resultados de búsqueda por nombre o descripción."""
        stmt = (
            select(func.count())
            .select_from(Domain)
            .where(
                (Domain.name.ilike(f"%{search_term}%"))
                | (Domain.description.ilike(f"%{search_term}%"))
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
