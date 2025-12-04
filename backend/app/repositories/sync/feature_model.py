from uuid import UUID
from typing import Optional
from sqlmodel import select, Session, func

from app.models import FeatureModel, FeatureModelCreate, FeatureModelUpdate
from app.interfaces import IFeatureModelRepositorySync
from app.repositories.base import BaseFeatureModelRepository


class FeatureModelRepositorySync(
    BaseFeatureModelRepository, IFeatureModelRepositorySync
):
    """Implementación síncrona del repositorio de feature models."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, data: FeatureModelCreate, owner_id: UUID) -> FeatureModel:
        """Crear un nuevo feature model."""
        # Verificar unicidad del nombre dentro del dominio
        existing = self.get_by_name(data.name, data.domain_id)
        self.validate_name_unique_in_domain(existing, name=data.name)

        obj = FeatureModel.model_validate(data, update={"owner_id": owner_id})
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get(self, feature_model_id: UUID) -> FeatureModel | None:
        """Obtener un feature model por ID."""
        return self.session.get(FeatureModel, feature_model_id)

    def get_by_name(self, name: str, domain_id: UUID) -> FeatureModel | None:
        """Obtener un feature model por nombre dentro de un dominio específico."""
        stmt = select(FeatureModel).where(
            FeatureModel.name == name, FeatureModel.domain_id == domain_id
        )
        return self.session.exec(stmt).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[FeatureModel]:
        """Obtener lista de todos los feature models con paginación."""
        stmt = select(FeatureModel).offset(skip).limit(limit)
        return self.session.exec(stmt).all()

    def get_by_domain(
        self, domain_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[FeatureModel]:
        """Obtener lista de feature models para un dominio específico con paginación."""
        stmt = (
            select(FeatureModel)
            .where(FeatureModel.domain_id == domain_id)
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(stmt).all()

    def update(
        self, db_feature_model: FeatureModel, data: FeatureModelUpdate
    ) -> FeatureModel:
        """Actualizar un feature model existente."""
        update_data = data.model_dump(exclude_unset=True)

        # Si se está actualizando el nombre, verificar unicidad en el dominio
        if "name" in update_data and update_data["name"] != db_feature_model.name:
            existing = self.get_by_name(update_data["name"], db_feature_model.domain_id)
            self.validate_name_unique_in_domain(
                existing, db_feature_model.id, update_data["name"]
            )

        db_feature_model.sqlmodel_update(update_data)
        self.session.add(db_feature_model)
        self.session.commit()
        self.session.refresh(db_feature_model)
        return db_feature_model

    def delete(self, db_feature_model: FeatureModel) -> FeatureModel:
        """Eliminar un feature model."""
        self.session.delete(db_feature_model)
        self.session.commit()
        return db_feature_model

    def exists(self, feature_model_id: UUID) -> bool:
        """Verificar si un feature model existe."""
        return self.session.get(FeatureModel, feature_model_id) is not None

    def count(self, domain_id: Optional[UUID] = None) -> int:
        """Contar el número total de feature models, opcionalmente filtrando por dominio."""
        stmt = select(func.count()).select_from(FeatureModel)
        if domain_id:
            stmt = stmt.where(FeatureModel.domain_id == domain_id)
        return self.session.exec(stmt).one()
