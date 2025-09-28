from uuid import UUID
from sqlmodel import Session, select

from app.models import Feature, FeatureCreate, FeatureUpdate


def get_feature(*, session: Session, feature_id: UUID) -> Feature | None:
    """Obtener una feature por ID."""
    return session.get(Feature, feature_id)


def get_features_by_model(
    *, session: Session, feature_model_id: UUID, skip: int = 0, limit: int = 100
) -> list[Feature]:
    """Obtener todas las features de un feature model específico."""
    statement = (
        select(Feature)
        .where(Feature.feature_model_id == feature_model_id)
        .offset(skip)
        .limit(limit)
    )
    return session.exec(statement).all()


def create_feature(*, session: Session, feature_create: FeatureCreate) -> Feature:
    """Crear una nueva feature."""
    # Aquí se podrían añadir validaciones, como verificar que el parent_id
    # pertenece al mismo feature_model_id.
    db_obj = Feature.model_validate(feature_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_feature(
    *, session: Session, db_feature: Feature, feature_in: FeatureUpdate
) -> Feature:
    """Actualizar una feature existente."""
    update_data = feature_in.model_dump(exclude_unset=True)
    
    # Evitar que una feature se convierta en su propio padre
    if "parent_id" in update_data and update_data["parent_id"] == db_feature.id:
        raise ValueError("A feature cannot be its own parent.")

    db_feature.sqlmodel_update(update_data)
    session.add(db_feature)
    session.commit()
    session.refresh(db_feature)
    return db_feature


def delete_feature(*, session: Session, db_feature: Feature) -> Feature:
    """Eliminar una feature."""
    # La configuración de cascada en el modelo se encargará de las relaciones
    # pero podrías añadir lógica para reasignar hijos si fuera necesario.
    session.delete(db_feature)
    session.commit()
    return db_feature

