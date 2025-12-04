from uuid import UUID
from typing import Optional
from sqlmodel import select, Session, func

from app.models import Domain, DomainCreate, DomainUpdate, DomainPublicWithFeatureModels
from app.interfaces import IDomainRepositorySync
from app.repositories.base import BaseDomainRepository


class DomainRepositorySync(BaseDomainRepository, IDomainRepositorySync):
    """Implementación síncrona del repositorio de dominios."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, data: DomainCreate) -> Domain:
        """Crear un nuevo dominio."""
        # Verificar unicidad del nombre
        existing = self.get_by_name(data.name)
        self.validate_name_unique(existing)

        obj = Domain.model_validate(data)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get(self, domain_id: UUID) -> Domain | None:
        """Obtener un dominio por ID."""
        return self.session.get(Domain, domain_id)

    def get_by_name(self, name: str) -> Domain | None:
        """Obtener un dominio por nombre."""
        stmt = select(Domain).where(Domain.name == name)
        return self.session.exec(stmt).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Domain]:
        """Obtener lista de dominios con paginación."""
        stmt = select(Domain).offset(skip).limit(limit)
        return self.session.exec(stmt).all()

    def update(self, db_domain: Domain, data: DomainUpdate) -> Domain:
        """Actualizar un dominio existente."""
        update_data = data.model_dump(exclude_unset=True)

        # Si se está actualizando el nombre, verificar unicidad
        if "name" in update_data and update_data["name"] != db_domain.name:
            existing = self.get_by_name(update_data["name"])
            self.validate_name_unique(existing, db_domain.id)

        db_domain.sqlmodel_update(update_data)
        self.session.add(db_domain)
        self.session.commit()
        self.session.refresh(db_domain)
        return db_domain

    def delete(self, db_domain: Domain) -> Domain:
        """Eliminar un dominio."""
        self.session.delete(db_domain)
        self.session.commit()
        return db_domain

    def get_with_feature_models(
        self, domain_id: UUID
    ) -> DomainPublicWithFeatureModels | None:
        """Obtener un dominio con sus modelos de características relacionados."""
        domain = self.session.get(Domain, domain_id)
        if not domain:
            return None

        # SQLModel carga las relaciones automáticamente cuando se acceden
        return DomainPublicWithFeatureModels.model_validate(domain)

    def exists(self, domain_id: UUID) -> bool:
        """Verificar si un dominio existe."""
        return self.session.get(Domain, domain_id) is not None

    def count(self) -> int:
        """Obtener el número total de dominios."""
        stmt = select(func.count()).select_from(Domain)
        return self.session.exec(stmt).one()

    def search(self, search_term: str, skip: int = 0, limit: int = 100) -> list[Domain]:
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
        return self.session.exec(stmt).all()

    def count_search(self, search_term: str) -> int:
        """Contar resultados de búsqueda por nombre o descripción."""
        stmt = (
            select(func.count())
            .select_from(Domain)
            .where(
                (Domain.name.ilike(f"%{search_term}%"))
                | (Domain.description.ilike(f"%{search_term}%"))
            )
        )
        return self.session.exec(stmt).one()
