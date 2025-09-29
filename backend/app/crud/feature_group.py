import uuid
from datetime import datetime
from sqlmodel import Session, select

from app.models import (
    FeatureGroup,
    FeatureGroupCreate,
    User,
)
from app.crud.feature_model_version import create_new_version_from_existing


def get_feature_group(*, session: Session, group_id: uuid.UUID) -> FeatureGroup | None:
    """Obtener un grupo de características por su ID."""
    return session.get(FeatureGroup, group_id)


def create_feature_group(
    *, session: Session, group_in: FeatureGroupCreate, user: User
) -> FeatureGroup:
    """
    Crea un nuevo grupo de características usando la estrategia "copy-on-write".
    Crea una nueva versión del modelo y añade el grupo en esa versión.
    """
    # Importación local para romper el ciclo
    from app.crud.feature import get_feature

    # 1. Validar que la feature padre existe
    parent_feature = get_feature(session=session, feature_id=group_in.parent_feature_id)
    if not parent_feature:
        raise ValueError("Parent feature not found.")

    # 2. Crear una nueva versión clonando la de origen (la de la feature padre)
    source_version = parent_feature.feature_model_version
    new_version, old_to_new_id_map = create_new_version_from_existing(
        session=session, source_version=source_version, user=user, return_id_map=True
    )

    # 3. Obtener el nuevo ID de la feature padre en la versión clonada
    new_parent_feature_id = old_to_new_id_map.get(group_in.parent_feature_id)
    if not new_parent_feature_id:
        raise RuntimeError("Cloned parent feature could not be found.")

    # 4. Crear el nuevo grupo en la nueva versión
    new_group = FeatureGroup(
        group_type=group_in.group_type,
        parent_feature_id=new_parent_feature_id,
        min_cardinality=group_in.min_cardinality,
        max_cardinality=group_in.max_cardinality,
        feature_model_version_id=new_version.id,
        created_by_id=user.id,
    )

    session.add(new_group)
    session.commit()
    session.refresh(new_group)

    return new_group


def delete_feature_group(
    *, session: Session, db_group: FeatureGroup, user: User
) -> None:
    """
    Elimina un grupo de características usando la estrategia "copy-on-write".
    Crea una nueva versión del modelo sin el grupo especificado.
    """
    # 1. Crear una nueva versión a partir de la versión actual del grupo
    source_version = db_group.feature_model_version
    new_version, old_to_new_id_map = create_new_version_from_existing(
        session=session, source_version=source_version, user=user, return_id_map=True
    )

    # 2. Encontrar el grupo correspondiente en la nueva versión para eliminarlo.
    # Para ello, buscamos un grupo con el mismo tipo y cuyo padre sea el clon del padre original.
    original_parent_id = db_group.parent_feature_id
    new_parent_id = old_to_new_id_map.get(original_parent_id)

    if not new_parent_id:
        raise RuntimeError("Could not map old parent feature ID to a new one.")

    statement = select(FeatureGroup).where(
        FeatureGroup.feature_model_version_id == new_version.id,
        FeatureGroup.parent_feature_id == new_parent_id,
        FeatureGroup.group_type == db_group.group_type,
        # Podríamos añadir más condiciones si varios grupos del mismo tipo pueden tener el mismo padre
    )
    group_to_delete = session.exec(statement).first()

    if group_to_delete:
        # Lógica de Soft Delete
        group_to_delete.is_active = False
        group_to_delete.deleted_at = datetime.utcnow()
        group_to_delete.updated_by_id = user.id
        # NOTA: Las features que eran miembros de este grupo ahora apuntarán a un grupo inactivo.
        # Esto es correcto, ya que la nueva versión es un snapshot.
        session.add(group_to_delete)
        session.commit()
    else:
        # Esto no debería pasar. Hacemos commit de la nueva versión de todas formas.
        session.commit()
