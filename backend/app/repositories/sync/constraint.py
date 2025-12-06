from uuid import UUID
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import Session, select

from app.models import (
    Constraint,
    ConstraintCreate,
    User,
)
from app.interfaces import IConstraintRepositorySync
from app.repositories.base import BaseConstraintRepository

if TYPE_CHECKING:
    from app.interfaces.sync import IFeatureModelVersionRepositorySync


class ConstraintRepositorySync(BaseConstraintRepository, IConstraintRepositorySync):
    """Implementación síncrona del repositorio de constraints."""

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        data: ConstraintCreate,
        user: User,
        feature_model_version_repo: "IFeatureModelVersionRepositorySync",
    ) -> Constraint:
        """
        Crea una nueva constraint usando la estrategia "copy-on-write".
        Crea una nueva versión del modelo y añade la constraint en esa versión.
        """
        # 1. Obtener la versión de origen
        source_version = feature_model_version_repo.get(
            version_id=data.feature_model_version_id
        )
        self.validate_feature_model_version_exists(source_version)

        # 2. Crear una nueva versión clonando la de origen
        new_version, _, _ = feature_model_version_repo.create_new_version_from_existing(
            source_version=source_version,
            user=user,
            return_id_map=True,
        )

        # 3. Crear la nueva constraint en la nueva versión
        new_constraint = Constraint(
            description=data.description,
            expr_text=data.expr_text,
            feature_model_version_id=new_version.id,
            created_by_id=user.id,
        )

        self.session.add(new_constraint)
        self.session.commit()
        self.session.refresh(new_constraint)

        return new_constraint

    def get(self, constraint_id: UUID) -> Constraint | None:
        """Obtener una constraint por su ID."""
        return self.session.get(Constraint, constraint_id)

    def delete(
        self,
        db_constraint: Constraint,
        user: User,
        feature_model_version_repo: "IFeatureModelVersionRepositorySync",
    ) -> None:
        """
        Elimina una constraint usando la estrategia "copy-on-write".
        Crea una nueva versión del modelo sin la constraint especificada.
        """
        # 1. Crear una nueva versión a partir de la versión actual de la constraint
        source_version = db_constraint.feature_model_version
        new_version, _, _ = feature_model_version_repo.create_new_version_from_existing(
            source_version=source_version,
            user=user,
            return_id_map=True,
        )

        # 2. Encontrar y eliminar la constraint correspondiente en la nueva versión
        statement = select(Constraint).where(
            Constraint.feature_model_version_id == new_version.id,
            Constraint.expr_text == db_constraint.expr_text,
        )
        constraint_to_delete = self.session.exec(statement).first()

        if constraint_to_delete:
            # Lógica de Soft Delete
            constraint_to_delete.is_active = False
            constraint_to_delete.deleted_at = datetime.utcnow()
            constraint_to_delete.updated_by_id = user.id
            self.session.add(constraint_to_delete)
            self.session.commit()
        else:
            self.session.commit()

    def exists(self, constraint_id: UUID) -> bool:
        """Verificar si una constraint existe."""
        constraint = self.get(constraint_id)
        return constraint is not None
