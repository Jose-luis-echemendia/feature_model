from uuid import UUID
from sqlmodel import Session, select

from app.models import (
    Feature,
    FeatureCreate,
    FeatureUpdate,
    FeaturePublicWithChildren,
    User,
)
from app.crud.feature_model_version import (
    create_new_version_from_existing,
    get_feature_model_version,
)


def get_feature(*, session: Session, feature_id: UUID) -> Feature | None:
    """Obtener una feature por ID."""
    return session.get(Feature, feature_id)


def get_features_by_version(
    *, session: Session, feature_model_version_id: UUID, skip: int = 0, limit: int = 100
) -> list[Feature]:
    """Obtener todas las features de una versión de modelo específica."""
    statement = (
        select(Feature)
        .where(Feature.feature_model_version_id == feature_model_version_id)
        .offset(skip)
        .limit(limit)
    )
    return session.exec(statement).all()


def get_features_as_tree(
    *, session: Session, feature_model_version_id: UUID, skip: int = 0, limit: int = 100
) -> list[FeaturePublicWithChildren]:
    """
    Obtiene las features de un modelo y las devuelve estructuradas como un árbol.
    """
    features_list = get_features_by_version(
        session=session,
        feature_model_version_id=feature_model_version_id,
        skip=skip,
        limit=limit,
    )

    feature_map = {
        str(f.id): FeaturePublicWithChildren.model_validate(f) for f in features_list
    }
    root_features = []

    for feature_public in feature_map.values():
        if feature_public.parent_id:
            parent_id_str = str(feature_public.parent_id)
            if parent_id_str in feature_map:
                feature_map[parent_id_str].children.append(feature_public)
        else:
            root_features.append(feature_public)

    return root_features


def create_feature(
    *, session: Session, feature_in: FeatureCreate, user: User
) -> Feature:
    """
    Crea una nueva feature usando la estrategia "copy-on-write".
    Crea una nueva versión del modelo y añade la nueva feature en esa versión.
    """
    # 1. Obtener la versión de origen
    source_version = get_feature_model_version(
        session=session, version_id=feature_in.feature_model_version_id
    )
    if not source_version:
        # Esta validación también está en la API, pero es bueno tenerla aquí
        raise ValueError("Source Feature Model Version not found.")

    # 2. Crear una nueva versión clonando la de origen
    new_version, old_to_new_id_map = create_new_version_from_existing(
        session=session, source_version=source_version, user=user, return_id_map=True
    )

    # 3. Preparar los datos de la nueva feature
    new_feature_data = feature_in.model_dump()
    # Asignar la feature a la *nueva* versión
    new_feature_data["feature_model_version_id"] = new_version.id

    # 4. Si hay un parent_id, re-mapearlo al ID correspondiente en la nueva versión
    if feature_in.parent_id:
        if feature_in.parent_id not in old_to_new_id_map:
            # El parent_id proporcionado no existe en la versión de origen
            raise ValueError("Parent feature not found in the source version.")
        new_feature_data["parent_id"] = old_to_new_id_map[feature_in.parent_id]

    # 5. Crear la nueva feature y guardarla
    db_obj = Feature.model_validate(new_feature_data)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_feature(
    *, session: Session, db_feature: Feature, feature_in: FeatureUpdate, user: User
) -> Feature:
    """
    Actualiza una feature usando la estrategia "copy-on-write".
    Crea una nueva versión del modelo y aplica el cambio en esa nueva versión.
    """
    # 1. Crear una nueva versión a partir de la versión actual de la feature
    source_version = db_feature.feature_model_version
    new_version = create_new_version_from_existing(
        session=session, source_version=source_version, user=user
    )

    # 2. Encontrar la feature correspondiente en la nueva versión
    # (Podríamos optimizar esto si create_new_version_from_existing devolviera el mapa de IDs)
    new_feature_to_update = next(
        (f for f in new_version.features if f.name == db_feature.name), None
    )
    if not new_feature_to_update:
        # Esto no debería ocurrir si la clonación fue exitosa
        raise RuntimeError(
            "Failed to find the corresponding feature in the new version."
        )

    # 3. Aplicar la actualización en la feature de la nueva versión
    update_data = feature_in.model_dump(exclude_unset=True)
    if "parent_id" in update_data and update_data["parent_id"] == db_feature.id:
        raise ValueError("A feature cannot be its own parent.")

    new_feature_to_update.sqlmodel_update(update_data)
    session.add(new_feature_to_update)
    session.commit()
    session.refresh(new_feature_to_update)

    return new_feature_to_update


def delete_feature(*, session: Session, db_feature: Feature, user: User) -> None:
    """
    Elimina una feature usando la estrategia "copy-on-write".
    Crea una nueva versión del modelo sin la feature especificada.
    """
    source_version = db_feature.feature_model_version
    new_version = create_new_version_from_existing(
        session=session, source_version=source_version, user=user
    )

    # Encontrar y eliminar la feature correspondiente en la nueva versión
    feature_to_delete = next(
        (f for f in new_version.features if f.name == db_feature.name), None
    )
    if feature_to_delete:
        session.delete(feature_to_delete)

    session.commit()
