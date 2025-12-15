import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import (
    AsyncConstraintRepoDep,
    AsyncFeatureModelVersionRepoDep,
    ModelDesignerUser,
)
from app.models.common import Message
from app.models.constraint import ConstraintCreate, ConstraintPublic

router = APIRouter(prefix="/constraints", tags=["constraints"])


@router.post("/", response_model=ConstraintPublic, status_code=status.HTTP_201_CREATED)
async def create_constraint(
    *,
    constraint_in: ConstraintCreate,
    current_user: ModelDesignerUser,
    constraint_repo: AsyncConstraintRepoDep,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
):
    """
    Create a new complex constraint. This will trigger the creation of a new model version.
    """
    # Permisos: Verificamos que el usuario es dueño del modelo.
    version = await feature_model_version_repo.get(
        version_id=constraint_in.feature_model_version_id
    )
    if not version:
        raise HTTPException(status_code=404, detail="Feature Model Version not found.")

    # Cargar las relaciones necesarias para la verificación de permisos
    await feature_model_version_repo.session.refresh(version, ["feature_model"])

    if (
        version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    try:
        constraint = await constraint_repo.create(
            data=constraint_in,
            user=current_user,
            feature_model_version_repo=feature_model_version_repo,
        )
        return constraint
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{constraint_id}/", response_model=Message)
async def delete_constraint(
    *,
    constraint_id: uuid.UUID,
    current_user: ModelDesignerUser,
    constraint_repo: AsyncConstraintRepoDep,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
):
    """
    Delete a complex constraint. This will trigger the creation of a new model version.
    """
    db_constraint = await constraint_repo.get(constraint_id=constraint_id)
    if not db_constraint:
        raise HTTPException(status_code=404, detail="Constraint not found.")

    # Cargar las relaciones necesarias para la verificación de permisos
    await constraint_repo.session.refresh(db_constraint, ["feature_model_version"])
    await constraint_repo.session.refresh(
        db_constraint.feature_model_version, ["feature_model"]
    )

    if (
        db_constraint.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    await constraint_repo.delete(
        db_constraint=db_constraint,
        user=current_user,
        feature_model_version_repo=feature_model_version_repo,
    )
    return Message(
        message="Constraint deleted in new model version created successfully."
    )
