from uuid import UUID
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import (
    Constraint,
    ConstraintCreate,
    User,
)
from app.interfaces import IConstraintRepositoryAsync
from app.repositories.base import BaseConstraintRepository

if TYPE_CHECKING:
    from app.interfaces.a_sync import IFeatureModelVersionRepositoryAsync


class ConstraintRepositoryAsync(BaseConstraintRepository, IConstraintRepositoryAsync):
    """Implementación asíncrona del repositorio de constraints."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        data: ConstraintCreate,
        user: User,
        feature_model_version_repo: "IFeatureModelVersionRepositoryAsync",
    ) -> Constraint:
        """
        Crea una nueva constraint usando la estrategia "copy-on-write".
        Crea una nueva versión del modelo y añade la constraint en esa versión.

        Nota: Utiliza funciones sync del CRUD ya que no existe versión async de create_new_version_from_existing.
        """

        def _create_constraint_sync(sync_session):
            # Importar repositorio sync dentro de la función sync
            from app.repositories.sync import FeatureModelVersionRepositorySync

            sync_version_repo = FeatureModelVersionRepositorySync(sync_session)

            # 1. Obtener la versión de origen
            source_version = sync_version_repo.get(
                version_id=data.feature_model_version_id
            )
            self.validate_feature_model_version_exists(source_version)

            # 2. Crear una nueva versión clonando la de origen
            new_version, _, _ = sync_version_repo.create_new_version_from_existing(
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

            sync_session.add(new_constraint)
            sync_session.commit()
            sync_session.refresh(new_constraint)

            return new_constraint

        # Ejecutar la lógica sync dentro del contexto async
        result = await self.session.run_sync(_create_constraint_sync)
        return result

    async def get(self, constraint_id: UUID) -> Constraint | None:
        """Obtener una constraint por su ID."""
        stmt = select(Constraint).where(Constraint.id == constraint_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(
        self,
        db_constraint: Constraint,
        user: User,
        feature_model_version_repo: "IFeatureModelVersionRepositoryAsync",
    ) -> None:
        """
        Elimina una constraint usando la estrategia "copy-on-write".
        Crea una nueva versión del modelo sin la constraint especificada.

        Nota: Utiliza funciones sync del CRUD ya que no existe versión async de create_new_version_from_existing.
        """

        def _delete_constraint_sync(sync_session):
            # Importar repositorio sync dentro de la función sync
            from app.repositories.sync import FeatureModelVersionRepositorySync

            sync_version_repo = FeatureModelVersionRepositorySync(sync_session)

            # 1. Crear una nueva versión a partir de la versión actual de la constraint
            source_version = db_constraint.feature_model_version
            new_version, _, _ = sync_version_repo.create_new_version_from_existing(
                source_version=source_version,
                user=user,
                return_id_map=True,
            )

            # 2. Encontrar y eliminar la constraint correspondiente en la nueva versión
            statement = select(Constraint).where(
                Constraint.feature_model_version_id == new_version.id,
                Constraint.expr_text == db_constraint.expr_text,
            )
            constraint_to_delete = sync_session.exec(statement).first()

            if constraint_to_delete:
                # Lógica de Soft Delete
                constraint_to_delete.is_active = False
                constraint_to_delete.deleted_at = datetime.utcnow()
                constraint_to_delete.updated_by_id = user.id
                sync_session.add(constraint_to_delete)
                sync_session.commit()
            else:
                sync_session.commit()

        # Ejecutar la lógica sync dentro del contexto async
        await self.session.run_sync(_delete_constraint_sync)

    async def exists(self, constraint_id: UUID) -> bool:
        """Verificar si una constraint existe."""
        constraint = await self.get(constraint_id)
        return constraint is not None
