from uuid import UUID
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import Session, select

from app.models import (
    FeatureRelation,
    FeatureRelationCreate,
    User,
)
from app.interfaces import IFeatureRelationRepositorySync
from app.repositories.base import BaseFeatureRelationRepository

if TYPE_CHECKING:
    from app.interfaces import IFeatureRepositorySync


class FeatureRelationRepositorySync(
    BaseFeatureRelationRepository, IFeatureRelationRepositorySync
):
    """Implementación síncrona del repositorio de relaciones entre features."""

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        data: FeatureRelationCreate,
        user: User,
        feature_repo: "IFeatureRepositorySync",
    ) -> FeatureRelation:
        """
        Crea una nueva relación usando la estrategia "copy-on-write".
        Crea una nueva versión del modelo y añade la relación en esa versión.
        """
        from app.crud.feature_model_version import create_new_version_from_existing

        # 1. Validar que las features de origen y destino existen
        source_feature = feature_repo.get(feature_id=data.source_feature_id)
        target_feature = feature_repo.get(feature_id=data.target_feature_id)

        self.validate_features_exist(source_feature, target_feature)

        # 2. Validar que ambas features pertenecen a la misma versión del modelo
        self.validate_same_version(source_feature, target_feature)

        # 3. Crear una nueva versión clonando la de origen
        source_version = source_feature.feature_model_version
        new_version, old_to_new_id_map = create_new_version_from_existing(
            session=self.session,
            source_version=source_version,
            user=user,
            return_id_map=True,
        )

        # 4. Crear la nueva relación en la nueva versión, usando los IDs re-mapeados
        new_relation = FeatureRelation(
            type=data.type,
            source_feature_id=old_to_new_id_map[data.source_feature_id],
            target_feature_id=old_to_new_id_map[data.target_feature_id],
            feature_model_version_id=new_version.id,
            created_by_id=user.id,
        )

        self.session.add(new_relation)
        self.session.commit()
        self.session.refresh(new_relation)

        return new_relation

    def get(self, relation_id: UUID) -> FeatureRelation | None:
        """Obtener una relación por su ID."""
        return self.session.get(FeatureRelation, relation_id)

    def delete(self, db_relation: FeatureRelation, user: User) -> None:
        """
        Elimina una relación usando la estrategia "copy-on-write".
        Crea una nueva versión del modelo sin la relación especificada.
        """
        from app.crud.feature_model_version import create_new_version_from_existing

        # 1. Crear una nueva versión a partir de la versión actual de la relación
        source_version = db_relation.feature_model_version
        new_version, old_to_new_id_map = create_new_version_from_existing(
            session=self.session,
            source_version=source_version,
            user=user,
            return_id_map=True,
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
        relation_to_delete = self.session.exec(statement).first()

        if relation_to_delete:
            # Lógica de Soft Delete
            relation_to_delete.is_active = False
            relation_to_delete.deleted_at = datetime.utcnow()
            relation_to_delete.updated_by_id = user.id
            self.session.add(relation_to_delete)
            self.session.commit()
        else:
            # Esto tampoco debería pasar. Podríamos loggear una advertencia.
            self.session.commit()  # Hacemos commit de la nueva versión aunque no se borre nada

    def exists(self, relation_id: UUID) -> bool:
        """Verificar si una relación existe."""
        relation = self.get(relation_id)
        return relation is not None
