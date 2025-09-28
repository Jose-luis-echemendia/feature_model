from uuid import UUID
from sqlmodel import Session, select

from app.models import FeatureModel, FeatureModelCreate, FeatureModelUpdate


def get_feature_model(
    *, session: Session, feature_model_id: UUID
) -> FeatureModel | None:
    """Obtener un feature model por ID"""
    return session.get(FeatureModel, feature_model_id)


def get_feature_model_by_name(
    *, session: Session, name: str, domain_id: UUID
) -> FeatureModel | None:
    """Obtener un feature model por nombre dentro de un dominio específico"""
    statement = select(FeatureModel).where(
        FeatureModel.name == name, FeatureModel.domain_id == domain_id
    )
    return session.exec(statement).first()


def get_feature_models_by_domain(
    *, session: Session, domain_id: UUID, skip: int = 0, limit: int = 100
) -> list[FeatureModel]:
    """Obtener lista de feature models para un dominio específico con paginación"""
    statement = (
        select(FeatureModel)
        .where(FeatureModel.domain_id == domain_id)
        .offset(skip)
        .limit(limit)
    )
    return session.exec(statement).all()


def get_all_feature_models(
    *, session: Session, skip: int = 0, limit: int = 100
) -> list[FeatureModel]:
    """Obtener lista de todos los feature models con paginación"""
    statement = select(FeatureModel).offset(skip).limit(limit)
    return session.exec(statement).all()


def create_feature_model(
    *, session: Session, feature_model_create: FeatureModelCreate, owner_id: UUID
) -> FeatureModel:
    """Crear un nuevo feature model"""
    # Verificar si ya existe un modelo con el mismo nombre en el mismo dominio
    existing_model = get_feature_model_by_name(
        session=session,
        name=feature_model_create.name,
        domain_id=feature_model_create.domain_id,
    )
    if existing_model:
        raise ValueError(
            f"Ya existe un Feature Model con el nombre '{feature_model_create.name}' en este dominio."
        )

    db_obj = FeatureModel.model_validate(
        feature_model_create, update={"owner_id": owner_id}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_feature_model(
    *,
    session: Session,
    db_feature_model: FeatureModel,
    feature_model_in: FeatureModelUpdate,
) -> FeatureModel:
    """Actualizar un feature model existente"""
    # Si se está actualizando el nombre, verificar que no exista otro con el mismo nombre en el mismo dominio
    if feature_model_in.name and feature_model_in.name != db_feature_model.name:
        existing_model = get_feature_model_by_name(
            session=session,
            name=feature_model_in.name,
            domain_id=db_feature_model.domain_id,
        )
        if existing_model and existing_model.id != db_feature_model.id:
            raise ValueError(
                f"Ya existe otro Feature Model con el nombre '{feature_model_in.name}' en este dominio."
            )

    update_data = feature_model_in.model_dump(exclude_unset=True)
    db_feature_model.sqlmodel_update(update_data)
    session.add(db_feature_model)
    session.commit()
    session.refresh(db_feature_model)
    return db_feature_model


def delete_feature_model(
    *, session: Session, db_feature_model: FeatureModel
) -> FeatureModel:
    """Eliminar un feature model"""
    # Aquí podrías añadir lógica para verificar si el modelo tiene features asociadas antes de borrar
    session.delete(db_feature_model)
    session.commit()
    return db_feature_model


def count_feature_models(*, session: Session, domain_id: UUID | None = None) -> int:
    """Contar el número total de feature models, opcionalmente filtrando por dominio"""
    statement = select(FeatureModel)
    if domain_id:
        statement = statement.where(FeatureModel.domain_id == domain_id)
    return len(session.exec(statement).all())
