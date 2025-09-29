import uuid
from sqlmodel import Session, select

from app.models import (
    Constraint,
    ConstraintCreate,
    User,
)
from app.crud.feature_model_version import (
    create_new_version_from_existing,
    get_feature_model_version,
)


def get_constraint(*, session: Session, constraint_id: uuid.UUID) -> Constraint | None:
    """Obtener una constraint por su ID."""
    return session.get(Constraint, constraint_id)


def create_constraint(
    *, session: Session, constraint_in: ConstraintCreate, user: User
) -> Constraint:
    """
    Crea una nueva constraint usando la estrategia "copy-on-write".
    Crea una nueva versión del modelo y añade la constraint en esa versión.
    """
    # 1. Obtener la versión de origen
    source_version = get_feature_model_version(
        session=session, version_id=constraint_in.feature_model_version_id
    )
    if not source_version:
        raise ValueError("Source Feature Model Version not found.")

    # 2. Crear una nueva versión clonando la de origen
    new_version, _, _ = create_new_version_from_existing(
        session=session, source_version=source_version, user=user, return_id_map=True
    )

    # 3. Crear la nueva constraint en la nueva versión
    new_constraint = Constraint(
        description=constraint_in.description,
        expr_text=constraint_in.expr_text,
        feature_model_version_id=new_version.id,
        created_by_id=user.id,
    )

    session.add(new_constraint)
    session.commit()
    session.refresh(new_constraint)

    return new_constraint


def delete_constraint(
    *, session: Session, db_constraint: Constraint, user: User
) -> None:
    """
    Elimina una constraint usando la estrategia "copy-on-write".
    Crea una nueva versión del modelo sin la constraint especificada.
    """
    # 1. Crear una nueva versión a partir de la versión actual de la constraint
    source_version = db_constraint.feature_model_version
    new_version, _, _ = create_new_version_from_existing(
        session=session, source_version=source_version, user=user, return_id_map=True
    )

    # 2. Encontrar y eliminar la constraint correspondiente en la nueva versión
    statement = select(Constraint).where(
        Constraint.feature_model_version_id == new_version.id,
        Constraint.expr_text == db_constraint.expr_text,
    )
    constraint_to_delete = session.exec(statement).first()

    if constraint_to_delete:
        session.delete(constraint_to_delete)
        session.commit()
    else:
        session.commit()
