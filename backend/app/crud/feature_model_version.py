import uuid
from sqlalchemy.orm import selectinload
from datetime import datetime
from sqlmodel import Session, select

from app.models import (
    Feature,
    FeatureModelVersion,
    FeatureGroup,
    Constraint,
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
) -> (
    FeatureModelVersion
    | tuple[FeatureModelVersion, dict[uuid.UUID, uuid.UUID], dict[uuid.UUID, uuid.UUID]]
):
    """
    Crea una nueva versión de un modelo de características, clonando todas las
    features y relaciones de una versión de origen. (Copy-On-Write)

    :param session: La sesión de la base de datos.
    :param source_version: La versión del modelo a partir de la cual se creará la nueva.
    :param user: El usuario que realiza la operación.
    :param return_id_map: Si es True, devuelve también el mapa de IDs antiguos a nuevos.
    :return: La nueva versión del modelo creada, y opcionalmente los mapas de IDs.
    """
    # 1. Cargar todas las features y relaciones de la versión de origen en una sola consulta
    # para evitar múltiples accesos a la BD (lazy loading).
    source_version_with_data = session.exec(
        select(FeatureModelVersion)
        .options(
            selectinload(FeatureModelVersion.features),
            selectinload(FeatureModelVersion.feature_groups),
            selectinload(FeatureModelVersion.constraints),
            selectinload(FeatureModelVersion.feature_relations),
        )
        .where(FeatureModelVersion.id == source_version.id)
    ).one()

    # 2. Crear la nueva entidad FeatureModelVersion
    latest_version_num = get_latest_version_number(
        session=session, feature_model_id=source_version_with_data.feature_model_id
    )
    new_version = FeatureModelVersion(
        feature_model_id=source_version_with_data.feature_model_id,
        version_number=latest_version_num + 1,
        # created_by_id se hereda de BaseTable y se asigna aquí
        created_by_id=user.id,
        is_active=False,  # Las nuevas versiones son borradores por defecto
    )
    session.add(new_version)
    session.flush()  # Obtenemos el ID de la nueva versión sin hacer commit

    # 3. Duplicar todas las features en memoria primero
    # Mapeo para mantener la correspondencia entre los IDs antiguos y los nuevos
    old_to_new_feature_id_map: dict[uuid.UUID, uuid.UUID] = {}
    new_features_map: dict[uuid.UUID, Feature] = {}

    for old_feature in source_version_with_data.features:
        # Creamos una nueva feature con los mismos datos pero asociada a la nueva versión
        new_feature_data = old_feature.model_dump(
            exclude={
                "id",
                "created_at",
                "updated_at",
                "deleted_at",
                "is_active",
                "created_by_id",
                "updated_by_id",
                "feature_model_version_id",
            }
        )
        new_feature = Feature(
            **new_feature_data,
            feature_model_version_id=new_version.id,
            created_by_id=user.id,
        )
        # Generamos un ID de cliente para poder mapear antes de hacer flush
        new_feature.id = uuid.uuid4()
        old_to_new_feature_id_map[old_feature.id] = new_feature.id
        new_features_map[new_feature.id] = new_feature

    # 4. Re-mapear los parent_id en las nuevas features (aún en memoria)
    for new_feature in new_features_map.values():
        if new_feature.parent_id and new_feature.parent_id in old_to_new_feature_id_map:
            new_feature.parent_id = old_to_new_feature_id_map[new_feature.parent_id]

    # 5. Duplicar los grupos de features (aún en memoria)
    old_to_new_group_id_map: dict[uuid.UUID, uuid.UUID] = {}
    new_groups_map: dict[uuid.UUID, FeatureGroup] = {}
    for old_group in source_version_with_data.feature_groups:
        new_group_data = old_group.model_dump(
            exclude={
                "id",
                "created_at",
                "updated_at",
                "deleted_at",
                "is_active",
                "created_by_id",
                "updated_by_id",
                "feature_model_version_id",
            }
        )
        # Re-mapear el parent_feature_id al nuevo ID
        new_group_data["parent_feature_id"] = old_to_new_feature_id_map[
            old_group.parent_feature_id
        ]
        new_group = FeatureGroup(
            **new_group_data,
            feature_model_version_id=new_version.id,
            created_by_id=user.id,
        )
        new_group.id = uuid.uuid4()
        old_to_new_group_id_map[old_group.id] = new_group.id
        new_groups_map[new_group.id] = new_group

    # 6. Re-mapear los group_id en las nuevas features (aún en memoria)
    for new_feature in new_features_map.values():
        if new_feature.group_id and new_feature.group_id in old_to_new_group_id_map:
            new_feature.group_id = old_to_new_group_id_map[new_feature.group_id]

    session.add_all(new_features_map.values())
    session.add_all(new_groups_map.values())

    # 7. Duplicar todas las constraints complejas
    new_constraints = []
    for old_constraint in source_version_with_data.constraints:
        new_constraint_data = old_constraint.model_dump(
            exclude={
                "id",
                "created_at",
                "updated_at",
                "deleted_at",
                "is_active",
                "created_by_id",
                "updated_by_id",
                "feature_model_version_id",
            }
        )
        new_constraint = Constraint(
            **new_constraint_data,
            feature_model_version_id=new_version.id,
            created_by_id=user.id,
        )
        new_constraints.append(new_constraint)
    session.add_all(new_constraints)

    # 8. Duplicar todas las relaciones, usando los nuevos IDs de features
    new_relations = []
    for old_relation in source_version_with_data.feature_relations:
        new_relation = FeatureRelation(
            feature_model_version_id=new_version.id,
            source_feature_id=old_to_new_feature_id_map[old_relation.source_feature_id],
            target_feature_id=old_to_new_feature_id_map[old_relation.target_feature_id],
            type=old_relation.type,
            created_by_id=user.id,
        )
        new_relations.append(new_relation)
    session.add_all(new_relations)

    # 9. Hacer commit de todos los cambios en una sola transacción
    session.commit()
    session.refresh(new_version)

    if return_id_map:
        return new_version, old_to_new_feature_id_map, old_to_new_group_id_map
    return new_version
