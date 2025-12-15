import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import (
    AsyncFeatureRepoDep,
    AsyncFeatureGroupRepoDep,
    AsyncFeatureModelVersionRepoDep,
    ModelDesignerUser,
)
from app.models.common import Message
from app.models.feature_group import FeatureGroupCreate, FeatureGroupPublic

router = APIRouter(prefix="/feature-groups", tags=["feature-groups"])


@router.post(
    "/", response_model=FeatureGroupPublic, status_code=status.HTTP_201_CREATED
)
async def create_feature_group(
    *,
    group_in: FeatureGroupCreate,
    current_user: ModelDesignerUser,
    feature_repo: AsyncFeatureRepoDep,
    feature_group_repo: AsyncFeatureGroupRepoDep,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
):
    """
    Create a new feature group. This will trigger the creation of a new model version.
    Only accessible to Model Designers and Admins.
    """
    # Permisos: Verificamos que el usuario es dueño del modelo al que pertenece la feature padre.
    parent_feature = await feature_repo.get(feature_id=group_in.parent_feature_id)
    if not parent_feature:
        raise HTTPException(status_code=404, detail="Parent feature not found.")

    # Cargar las relaciones necesarias para la verificación de permisos
    await feature_repo.session.refresh(parent_feature, ["feature_model_version"])
    await feature_repo.session.refresh(
        parent_feature.feature_model_version, ["feature_model"]
    )

    if (
        parent_feature.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    try:
        group = await feature_group_repo.create(
            data=group_in,
            user=current_user,
            feature_repo=feature_repo,
            feature_model_version_repo=feature_model_version_repo,
        )
        return group
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{group_id}/", response_model=Message)
async def delete_feature_group(
    *,
    group_id: uuid.UUID,
    current_user: ModelDesignerUser,
    feature_group_repo: AsyncFeatureGroupRepoDep,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
):
    """
    Delete a feature group. This will trigger the creation of a new model version.
    """
    db_group = await feature_group_repo.get(group_id=group_id)
    if not db_group:
        raise HTTPException(status_code=404, detail="Feature group not found.")

    # Cargar las relaciones necesarias para la verificación de permisos
    await feature_group_repo.session.refresh(db_group, ["feature_model_version"])
    await feature_group_repo.session.refresh(
        db_group.feature_model_version, ["feature_model"]
    )

    if (
        db_group.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    await feature_group_repo.delete(
        db_group=db_group,
        user=current_user,
        feature_model_version_repo=feature_model_version_repo,
    )
    return Message(
        message="Feature group deleted in new model version created successfully."
    )
