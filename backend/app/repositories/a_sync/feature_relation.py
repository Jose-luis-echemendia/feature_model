from uuid import UUID
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import (
    FeatureRelation,
    FeatureRelationCreate,
    User,
)
from app.interfaces import IFeatureRelationRepositoryAsync
from app.repositories.base import BaseFeatureRelationRepository

if TYPE_CHECKING:
    from app.interfaces import (
        IFeatureRepositoryAsync,
        IFeatureModelVersionRepositoryAsync,
    )


class FeatureRelationRepositoryAsync(
    BaseFeatureRelationRepository, IFeatureRelationRepositoryAsync
):
    """Implementación asíncrona del repositorio de relaciones entre features."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        data: FeatureRelationCreate,
        user: User,
        feature_repo: "IFeatureRepositoryAsync",
        feature_model_version_repo: "IFeatureModelVersionRepositoryAsync",
    ) -> FeatureRelation:
        """
        Crea una nueva relación usando la estrategia "copy-on-write".
        Crea una nueva versión del modelo y añade la relación en esa versión.

        Nota: Utiliza funciones sync del CRUD ya que no existe versión async de create_new_version_from_existing.
        """

        def _create_relation_sync(sync_session):
            # Importar repositorio sync dentro de la función sync
            from app.repositories.sync import FeatureModelVersionRepositorySync

            sync_version_repo = FeatureModelVersionRepositorySync(sync_session)

            # 1. Validar que las features de origen y destino existen (usando el método sync)
            # Necesitamos obtener las features de forma síncrona dentro de run_sync
            from sqlmodel import select
            from app.models import Feature

            source_stmt = select(Feature).where(
                Feature.id == data.source_feature_id, Feature.is_active == True
            )
            source_feature = sync_session.exec(source_stmt).first()

            target_stmt = select(Feature).where(
                Feature.id == data.target_feature_id, Feature.is_active == True
            )
            target_feature = sync_session.exec(target_stmt).first()

            self.validate_features_exist(source_feature, target_feature)

            # 2. Validar que ambas features pertenecen a la misma versión del modelo
            self.validate_same_version(source_feature, target_feature)

            # 3. Crear una nueva versión clonando la de origen
            source_version = source_feature.feature_model_version
            new_version, old_to_new_id_map = (
                sync_version_repo.create_new_version_from_existing(
                    source_version=source_version,
                    user=user,
                    return_id_map=True,
                )
            )

            # 4. Crear la nueva relación en la nueva versión, usando los IDs re-mapeados
            new_relation = FeatureRelation(
                type=data.type,
                source_feature_id=old_to_new_id_map[data.source_feature_id],
                target_feature_id=old_to_new_id_map[data.target_feature_id],
                feature_model_version_id=new_version.id,
                created_by_id=user.id,
            )

            sync_session.add(new_relation)
            sync_session.commit()
            sync_session.refresh(new_relation)

            return new_relation

        # Ejecutar la lógica sync dentro del contexto async
        result = await self.session.run_sync(_create_relation_sync)
        return result

    async def get(self, relation_id: UUID) -> FeatureRelation | None:
        """Obtener una relación por su ID."""
        stmt = select(FeatureRelation).where(FeatureRelation.id == relation_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(
        self,
        db_relation: FeatureRelation,
        user: User,
        feature_model_version_repo: "IFeatureModelVersionRepositoryAsync",
    ) -> None:
        """
        Elimina una relación usando la estrategia "copy-on-write".
        Crea una nueva versión del modelo sin la relación especificada.

        Nota: Utiliza funciones sync del CRUD ya que no existe versión async de create_new_version_from_existing.
        """

        def _delete_relation_sync(sync_session):
            # Importar repositorio sync dentro de la función sync
            from app.repositories.sync import FeatureModelVersionRepositorySync

            sync_version_repo = FeatureModelVersionRepositorySync(sync_session)

            # 1. Crear una nueva versión a partir de la versión actual de la relación
            source_version = db_relation.feature_model_version
            new_version, old_to_new_id_map = (
                sync_version_repo.create_new_version_from_existing(
                    source_version=source_version,
                    user=user,
                    return_id_map=True,
                )
            )

            # 2. Encontrar y eliminar la relación correspondiente en la nueva versión
            # Necesitamos los nuevos IDs de las features para encontrar la relación clonada
            new_source_id = old_to_new_id_map.get(db_relation.source_feature_id)
            new_target_id = old_to_new_id_map.get(db_relation.target_feature_id)

            if not new_source_id or not new_target_id:
                # Esto no debería pasar si la clonación fue exitosa
                raise RuntimeError("Could not map old feature IDs to new ones.")

            statement = select(FeatureRelation).where(
                FeatureRelation.feature_model_version_id == new_version.id,
                FeatureRelation.source_feature_id == new_source_id,
                FeatureRelation.target_feature_id == new_target_id,
                FeatureRelation.type == db_relation.type,
            )
            relation_to_delete = sync_session.exec(statement).first()

            if relation_to_delete:
                # Lógica de Soft Delete
                relation_to_delete.is_active = False
                relation_to_delete.deleted_at = datetime.utcnow()
                relation_to_delete.updated_by_id = user.id
                sync_session.add(relation_to_delete)
                sync_session.commit()
            else:
                # Esto tampoco debería pasar. Podríamos loggear una advertencia.
                sync_session.commit()  # Hacemos commit de la nueva versión aunque no se borre nada

        # Ejecutar la lógica sync dentro del contexto async
        await self.session.run_sync(_delete_relation_sync)

    async def exists(self, relation_id: UUID) -> bool:
        """Verificar si una relación existe."""
        relation = await self.get(relation_id)
        return relation is not None
