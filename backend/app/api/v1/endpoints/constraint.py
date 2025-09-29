import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from app import crud
from app.api.deps import SessionDep, ModelDesignerUser
from app.models.common import Message
from app.models.constraint import ConstraintCreate, ConstraintPublic

router = APIRouter(prefix="/constraints", tags=["constraints"])


@router.post("/", response_model=ConstraintPublic, status_code=status.HTTP_201_CREATED)
def create_constraint(
    *,
    session: SessionDep,
    constraint_in: ConstraintCreate,
    current_user: ModelDesignerUser,
):
    """
    Create a new complex constraint. This will trigger the creation of a new model version.
    """
    # Permisos: Verificamos que el usuario es dueño del modelo.
    version = crud.get_feature_model_version(
        session=session, version_id=constraint_in.feature_model_version_id
    )
    if not version:
        raise HTTPException(status_code=404, detail="Feature Model Version not found.")

    session.refresh(version, ["feature_model"])
    if (
        version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    try:
        constraint = crud.create_constraint(
            session=session, constraint_in=constraint_in, user=current_user
        )
        return constraint
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{constraint_id}/", response_model=Message)
def delete_constraint(
    *,
    constraint_id: uuid.UUID,
    session: SessionDep,
    current_user: ModelDesignerUser,
):
    """
    Delete a complex constraint. This will trigger the creation of a new model version.
    """
    db_constraint = crud.get_constraint(session=session, constraint_id=constraint_id)
    if not db_constraint:
        raise HTTPException(status_code=404, detail="Constraint not found.")

    session.refresh(db_constraint, ["feature_model_version"])
    session.refresh(db_constraint.feature_model_version, ["feature_model"])

    if (
        db_constraint.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    crud.delete_constraint(
        session=session, db_constraint=db_constraint, user=current_user
    )
    return Message(
        message="Constraint deleted in new model version created successfully."
    )
