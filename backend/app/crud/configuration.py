from sqlmodel import Session, select

from app.models import (
    Configuration,
    ConfigurationCreate,
    ConfigurationUpdate,
    Feature,
)


def create_configuration(
    *, session: Session, configuration_create: ConfigurationCreate
) -> Configuration:
    """
    Crea una nueva configuración y asocia las features.
    """
    # Obtener las features de la base de datos a partir de los IDs
    features = session.exec(
        select(Feature).where(Feature.id.in_(configuration_create.feature_ids))
    ).all()

    # Crear el objeto de configuración sin los feature_ids
    db_obj = Configuration.model_validate(
        configuration_create, update={"features": features}
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_configuration(
    *, session: Session, db_obj: Configuration, obj_in: ConfigurationUpdate
) -> Configuration:
    """
    Actualiza una configuración, incluyendo sus features asociadas.
    """
    # Actualiza los campos simples
    obj_data = obj_in.model_dump(exclude_unset=True)
    db_obj.sqlmodel_update(obj_data)

    # Actualiza las features si se proporcionan
    if "feature_ids" in obj_data and obj_data["feature_ids"] is not None:
        features = session.exec(
            select(Feature).where(Feature.id.in_(obj_data["feature_ids"]))
        ).all()
        db_obj.features = features

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_configuration_by_id(
    *, session: Session, configuration_id: int
) -> Configuration | None:
    """
    Obtiene una configuración por su ID.
    """
    return session.get(Configuration, configuration_id)
