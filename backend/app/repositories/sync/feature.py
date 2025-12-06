from uuid import UUID
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import select, Session, func

from app.models import (
    Feature,
    FeatureCreate,
    FeatureUpdate,
    FeaturePublicWithChildren,
    User,
)
from app.interfaces import IFeatureRepositorySync
from app.repositories.base import BaseFeatureRepository

if TYPE_CHECKING:
    from app.interfaces.sync import (
        IFeatureModelVersionRepositorySync,
        IFeatureGroupRepositorySync,
    )


class FeatureRepositorySync(BaseFeatureRepository, IFeatureRepositorySync):
    """Implementación síncrona del repositorio de features."""

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        data: FeatureCreate,
        user: User,
        feature_model_version_repo: "IFeatureModelVersionRepositorySync",
    ) -> Feature:
        """
        Crea una nueva feature usando la estrategia "copy-on-write".
        Crea una nueva versión del modelo y añade la nueva feature en esa versión.
        """
        # 1. Obtener la versión de origen
        source_version = feature_model_version_repo.get(
            version_id=data.feature_model_version_id
        )
        if not source_version:
            raise ValueError("Source Feature Model Version not found.")

        # 2. Crear una nueva versión clonando la de origen
        new_version, old_to_new_id_map = (
            feature_model_version_repo.create_new_version_from_existing(
                source_version=source_version,
                user=user,
                return_id_map=True,
            )
        )

        # 3. Preparar los datos de la nueva feature
        new_feature_data = data.model_dump()
        new_feature_data["feature_model_version_id"] = new_version.id

        # 4. Si hay un parent_id, re-mapearlo al ID correspondiente en la nueva versión
        if data.parent_id:
            if data.parent_id not in old_to_new_id_map:
                raise ValueError("Parent feature not found in the source version.")
            new_feature_data["parent_id"] = old_to_new_id_map[data.parent_id]

        # 5. Crear la nueva feature y guardarla
        db_obj = Feature.model_validate(new_feature_data)
        db_obj.created_by_id = user.id
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def get(self, feature_id: UUID) -> Feature | None:
        """Obtener una feature por ID (solo activas)."""
        stmt = select(Feature).where(
            Feature.id == feature_id, Feature.is_active == True
        )
        return self.session.exec(stmt).first()

    def get_by_version(
        self, feature_model_version_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Feature]:
        """Obtener todas las features de una versión de modelo específica."""
        stmt = (
            select(Feature)
            .where(Feature.is_active == True)
            .where(Feature.feature_model_version_id == feature_model_version_id)
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(stmt).all()

    def get_as_tree(
        self, feature_model_version_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[FeaturePublicWithChildren]:
        """Obtiene las features de un modelo y las devuelve estructuradas como un árbol."""
        features_list = self.get_by_version(
            feature_model_version_id=feature_model_version_id, skip=skip, limit=limit
        )
        return self.build_feature_tree(features_list)

    def update(
        self,
        db_feature: Feature,
        data: FeatureUpdate,
        user: User,
        feature_model_version_repo: "IFeatureModelVersionRepositorySync",
        feature_group_repo: "IFeatureGroupRepositorySync",
    ) -> Feature:
        """
        Actualiza una feature usando la estrategia "copy-on-write".
        Crea una nueva versión del modelo y aplica el cambio en esa nueva versión.
        """
        # Validar parent_id no sea el mismo feature
        if data.parent_id:
            self.validate_parent_not_self(db_feature.id, data.parent_id)

        # 1. Crear una nueva versión a partir de la versión actual de la feature
        source_version = db_feature.feature_model_version
        (
            new_version,
            old_to_new_feature_id_map,
            old_to_new_group_id_map,
        ) = feature_model_version_repo.create_new_version_from_existing(
            source_version=source_version,
            user=user,
            return_id_map=True,
        )

        # 2. Encontrar la feature correspondiente en la nueva versión
        new_feature_id = old_to_new_feature_id_map.get(db_feature.id)
        if not new_feature_id:
            raise RuntimeError(
                "Failed to find the corresponding feature in the new version."
            )
        new_feature_to_update = self.get(feature_id=new_feature_id)

        if not new_feature_to_update:
            raise RuntimeError("Could not fetch the cloned feature from the database.")

        # 3. Aplicar la actualización
        update_data = data.model_dump(exclude_unset=True)

        # 3.1. Re-mapear parent_id si se está cambiando
        if "parent_id" in update_data and update_data["parent_id"]:
            update_data["parent_id"] = old_to_new_feature_id_map.get(
                update_data["parent_id"]
            )

        # 3.2. Re-mapear group_id si se está cambiando
        if "group_id" in update_data and update_data["group_id"]:
            old_group = feature_group_repo.get(group_id=update_data["group_id"])
            if not old_group or old_group.feature_model_version_id != source_version.id:
                raise ValueError(
                    "Group not found or does not belong to the same model version."
                )
            update_data["group_id"] = old_to_new_group_id_map.get(
                update_data["group_id"]
            )

        # 4. Aplicar los datos actualizados y guardar
        new_feature_to_update.sqlmodel_update(update_data)
        new_feature_to_update.updated_at = datetime.utcnow()
        new_feature_to_update.updated_by_id = user.id
        self.session.add(new_feature_to_update)
        self.session.commit()
        self.session.refresh(new_feature_to_update)

        return new_feature_to_update

    def delete(
        self,
        db_feature: Feature,
        user: User,
        feature_model_version_repo: "IFeatureModelVersionRepositorySync",
    ) -> None:
        """
        Elimina una feature usando la estrategia "copy-on-write".
        Crea una nueva versión del modelo sin la feature especificada.
        """
        source_version = db_feature.feature_model_version
        new_version = feature_model_version_repo.create_new_version_from_existing(
            source_version=source_version, user=user
        )

        # Encontrar y eliminar la feature correspondiente en la nueva versión
        feature_to_delete = next(
            (f for f in new_version.features if f.name == db_feature.name), None
        )
        if feature_to_delete:
            self.session.delete(feature_to_delete)

        self.session.commit()

    def exists(self, feature_id: UUID) -> bool:
        """Verificar si una feature existe y está activa."""
        feature = self.get(feature_id)
        return feature is not None

    def count(self, feature_model_version_id: Optional[UUID] = None) -> int:
        """Contar el número total de features activas, opcionalmente filtrando por versión."""
        stmt = (
            select(func.count()).select_from(Feature).where(Feature.is_active == True)
        )
        if feature_model_version_id:
            stmt = stmt.where(
                Feature.feature_model_version_id == feature_model_version_id
            )
        return self.session.exec(stmt).one()
