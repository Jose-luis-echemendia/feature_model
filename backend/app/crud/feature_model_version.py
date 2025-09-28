import uuid
from sqlmodel import Session, select

from app.models import (
    Feature,
    FeatureModelVersion,
    FeatureRelation,
    User,
)


def get_feature_model_version(
    *, session: Session, version_id: uuid.UUID
) -> FeatureModelVersion | None:
    """Obtener una versión de modelo por su ID."""
    return session.get(FeatureModelVersion, version_id)


def get_latest_version_number(*, session: Session, feature_model_id: uuid.UUID) -> int:
    """Obtener el número de la última versión para un modelo."""
    statement = select(FeatureModelVersion.version_number).where(
        FeatureModelVersion.feature_model_id == feature_model_id
    )
    max_version = session.exec(statement).max()
    return max_version or 0


def create_new_version_from_existing(
    *,
    session: Session,
    source_version: FeatureModelVersion,
    user: User,
    return_id_map: bool = False,
) -> FeatureModelVersion | tuple[FeatureModelVersion, dict[uuid.UUID, uuid.UUID]]:
    """
    Crea una nueva versión de un modelo de características, clonando todas las
    features y relaciones de una versión de origen. (Copy-On-Write)

    :param session: La sesión de la base de datos.
    :param source_version: La versión del modelo a partir de la cual se creará la nueva.
    :param user: El usuario que realiza la operación.
    :param return_id_map: Si es True, devuelve también el mapa de IDs antiguos a nuevos.
    :return: La nueva versión del modelo creada.
    """
    session.refresh(source_version, ["features", "feature_relations"])

    # 1. Crear la nueva entidad FeatureModelVersion
    latest_version_num = get_latest_version_number(
        session=session, feature_model_id=source_version.feature_model_id
    )
    new_version = FeatureModelVersion(
        feature_model_id=source_version.feature_model_id,
        version_number=latest_version_num + 1,
        created_by_id=user.id,
        is_active=False,  # Las nuevas versiones son borradores por defecto
    )
    session.add(new_version)
    session.commit()
    session.refresh(new_version)

    # 2. Duplicar todas las features de la versión de origen a la nueva
    # Mapeo para mantener la correspondencia entre los IDs antiguos y los nuevos
    old_to_new_feature_id_map: dict[uuid.UUID, uuid.UUID] = {}

    for old_feature in source_version.features:
        # Creamos una nueva feature con los mismos datos pero asociada a la nueva versión
        new_feature_data = old_feature.model_dump(
            exclude={"id", "created_at", "updated_at", "feature_model_version_id"}
        )
        new_feature = Feature(
            **new_feature_data, feature_model_version_id=new_version.id
        )
        session.add(new_feature)
        session.flush()  # Usamos flush para obtener el nuevo ID sin hacer commit

        # Guardamos la correspondencia de IDs
        old_to_new_feature_id_map[old_feature.id] = new_feature.id

    # 3. Re-mapear los parent_id en las nuevas features
    # Hacemos un SELECT de las nuevas features para actualizarlas
    new_features_list = session.exec(
        select(Feature).where(Feature.feature_model_version_id == new_version.id)
    ).all()
    for feature in new_features_list:
        if feature.parent_id and feature.parent_id in old_to_new_feature_id_map:
            feature.parent_id = old_to_new_feature_id_map[feature.parent_id]
            session.add(feature)

    # 4. Duplicar todas las relaciones, usando los nuevos IDs de features
    for old_relation in source_version.feature_relations:
        new_relation = FeatureRelation(
            feature_model_version_id=new_version.id,
            source_feature_id=old_to_new_feature_id_map[old_relation.source_feature_id],
            target_feature_id=old_to_new_feature_id_map[old_relation.target_feature_id],
            type=old_relation.type,
        )
        session.add(new_relation)

    # 5. Hacer commit de todos los cambios (nuevas features, parents y relaciones)
    session.commit()
    session.refresh(new_version)

    if return_id_map:
        return new_version, old_to_new_feature_id_map
    return new_version
