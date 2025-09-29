import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from app import crud
from app.api.deps import SessionDep, ModelDesignerUser
from app.models.common import Message
from app.models.feature_group import FeatureGroupCreate, FeatureGroupPublic

router = APIRouter(prefix="/feature-groups", tags=["feature-groups"])


@router.post(
    "/", response_model=FeatureGroupPublic, status_code=status.HTTP_201_CREATED
)
def create_feature_group(
    *,
    session: SessionDep,
    group_in: FeatureGroupCreate,
    current_user: ModelDesignerUser,
):
    """
    Create a new feature group. This will trigger the creation of a new model version.
    Only accessible to Model Designers and Admins.
    """
    # Permisos: Verificamos que el usuario es dueño del modelo al que pertenece la feature padre.
    parent_feature = crud.get_feature(
        session=session, feature_id=group_in.parent_feature_id
    )
    if not parent_feature:
        raise HTTPException(status_code=404, detail="Parent feature not found.")

    session.refresh(parent_feature, ["feature_model_version"])
    session.refresh(parent_feature.feature_model_version, ["feature_model"])

    if (
        parent_feature.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    try:
        group = crud.create_feature_group(
            session=session, group_in=group_in, user=current_user
        )
        return group
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{group_id}/", response_model=Message)
def delete_feature_group(
    *,
    group_id: uuid.UUID,
    session: SessionDep,
    current_user: ModelDesignerUser,
):
    """
    Delete a feature group. This will trigger the creation of a new model version.
    """
    db_group = crud.get_feature_group(session=session, group_id=group_id)
    if not db_group:
        raise HTTPException(status_code=404, detail="Feature group not found.")

    session.refresh(db_group, ["feature_model_version"])
    session.refresh(db_group.feature_model_version, ["feature_model"])

    if (
        db_group.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    crud.delete_feature_group(session=session, db_group=db_group, user=current_user)
    return Message(
        message="Feature group deleted in new model version created successfully."
    )
