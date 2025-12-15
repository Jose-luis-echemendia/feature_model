import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import (
    AsyncFeatureRepoDep,
    AsyncFeatureRelationRepoDep,
    AsyncFeatureModelVersionRepoDep,
    ModelDesignerUser,
)
from app.models.common import Message
from app.models.feature_relation import FeatureRelationCreate, FeatureRelationPublic

router = APIRouter(prefix="/feature-relations", tags=["feature-relations"])


@router.post(
    "/", response_model=FeatureRelationPublic, status_code=status.HTTP_201_CREATED
)
async def create_feature_relation(
    *,
    relation_in: FeatureRelationCreate,
    current_user: ModelDesignerUser,
    feature_repo: AsyncFeatureRepoDep,
    feature_relation_repo: AsyncFeatureRelationRepoDep,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
):
    """
    Create a new feature relation. This will trigger the creation of a new model version.
    Only accessible to Model Designers and Admins.
    """
    # Permisos: Verificamos que el usuario es dueño del modelo al que pertenecen las features.
    # La lógica del repositorio se encarga de las validaciones de consistencia.
    source_feature = await feature_repo.get(feature_id=relation_in.source_feature_id)
    if not source_feature:
        raise HTTPException(status_code=404, detail="Source feature not found.")

    # Cargar las relaciones necesarias para la verificación de permisos
    await feature_repo.session.refresh(source_feature, ["feature_model_version"])
    await feature_repo.session.refresh(
        source_feature.feature_model_version, ["feature_model"]
    )

    if (
        source_feature.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    try:
        relation = await feature_relation_repo.create(
            data=relation_in,
            user=current_user,
            feature_repo=feature_repo,
            feature_model_version_repo=feature_model_version_repo,
        )
        return relation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{relation_id}/", response_model=Message)
async def delete_feature_relation(
    *,
    relation_id: uuid.UUID,
    current_user: ModelDesignerUser,
    feature_relation_repo: AsyncFeatureRelationRepoDep,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
):
    """
    Delete a feature relation. This will trigger the creation of a new model version.
    """
    db_relation = await feature_relation_repo.get(relation_id=relation_id)
    if not db_relation:
        raise HTTPException(status_code=404, detail="Feature relation not found.")

    # Cargar las relaciones necesarias para la verificación de permisos
    await feature_relation_repo.session.refresh(db_relation, ["feature_model_version"])
    await feature_relation_repo.session.refresh(
        db_relation.feature_model_version, ["feature_model"]
    )

    if (
        db_relation.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    await feature_relation_repo.delete(
        db_relation=db_relation,
        user=current_user,
        feature_model_version_repo=feature_model_version_repo,
    )
    return Message(
        message="Feature relation deleted in new model version created successfully."
    )
