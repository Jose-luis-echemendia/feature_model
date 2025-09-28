import uuid
from sqlmodel import Session, select

from app.models import (
    Feature,
    FeatureRelation,
    FeatureRelationCreate,
    User,
)
from app.crud.feature_model_version import create_new_version_from_existing
from app.crud.feature import get_feature


def get_feature_relation(
    *, session: Session, relation_id: uuid.UUID
) -> FeatureRelation | None:
    """Obtener una relación por su ID."""
    return session.get(FeatureRelation, relation_id)


def create_feature_relation(
    *, session: Session, relation_in: FeatureRelationCreate, user: User
) -> FeatureRelation:
    """
    Crea una nueva relación usando la estrategia "copy-on-write".
    Crea una nueva versión del modelo y añade la relación en esa versión.
    """
    # 1. Validar que las features de origen y destino existen
    source_feature = get_feature(
        session=session, feature_id=relation_in.source_feature_id
    )
    target_feature = get_feature(
        session=session, feature_id=relation_in.target_feature_id
    )

    if not source_feature or not target_feature:
        raise ValueError("Source or target feature not found.")

    # 2. Validar que ambas features pertenecen a la misma versión del modelo
    if (
        source_feature.feature_model_version_id
        != target_feature.feature_model_version_id
    ):
        raise ValueError(
            "Source and target features must belong to the same model version."
        )

    # 3. Crear una nueva versión clonando la de origen
    source_version = source_feature.feature_model_version
    new_version, old_to_new_id_map = create_new_version_from_existing(
        session=session, source_version=source_version, user=user, return_id_map=True
    )

    # 4. Crear la nueva relación en la nueva versión, usando los IDs re-mapeados
    new_relation = FeatureRelation(
        type=relation_in.type,
        source_feature_id=old_to_new_id_map[relation_in.source_feature_id],
        target_feature_id=old_to_new_id_map[relation_in.target_feature_id],
        feature_model_version_id=new_version.id,
    )

    session.add(new_relation)
    session.commit()
    session.refresh(new_relation)

    return new_relation


def delete_feature_relation(
    *, session: Session, db_relation: FeatureRelation, user: User
) -> None:
    """
    Elimina una relación usando la estrategia "copy-on-write".
    Crea una nueva versión del modelo sin la relación especificada.
    """
    # 1. Crear una nueva versión a partir de la versión actual de la relación
    source_version = db_relation.feature_model_version
    new_version, old_to_new_id_map = create_new_version_from_existing(
        session=session, source_version=source_version, user=user, return_id_map=True
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
    relation_to_delete = session.exec(statement).first()

    if relation_to_delete:
        session.delete(relation_to_delete)
        session.commit()
    else:
        # Esto tampoco debería pasar. Podríamos loggear una advertencia.
        session.commit()  # Hacemos commit de la nueva versión aunque no se borre nada
