import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from app import crud, models
from app.api.deps import SessionDep, ModelDesignerUser, VerifiedUser
from app.models.common import Message
from app.models.feature import (
    FeatureCreate,
    FeaturePublic,
    FeatureUpdate,
    FeaturePublicWithChildren,
)
from app.crud import feature_model_version as crud_version

router = APIRouter(prefix="/features", tags=["features"])


@router.get(
    "/",
    dependencies=[Depends(VerifiedUser)],
    response_model=list[FeaturePublicWithChildren],
)
def read_features_by_model(
    *,
    session: SessionDep,
    feature_model_version_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[FeaturePublic]:
    """
    Retrieve all features for a specific feature model version, structured as a tree.
    """
    # Esta función ahora está en el CRUD para ser reutilizada y testeada más fácilmente
    root_features = crud.get_features_as_tree(
        session=session,
        feature_model_version_id=feature_model_version_id,
        skip=skip,
        limit=limit,
    )
    return root_features


@router.post("/", response_model=FeaturePublic, status_code=status.HTTP_201_CREATED)
def create_feature(
    *,
    session: SessionDep,
    feature_in: FeatureCreate,
    current_user: ModelDesignerUser,
) -> FeaturePublic:
    """
    Create a new feature within a feature model.
    Only accessible to Model Designers and Admins.
    """
    # 1. Verificar que la versión del modelo existe y que el usuario tiene permisos sobre el modelo padre
    version = crud_version.get_feature_model_version(
        session=session, version_id=feature_in.feature_model_version_id
    )
    if not version:
        raise HTTPException(status_code=404, detail="Feature Model Version not found.")

    # Refrescamos la relación para acceder a feature_model.owner_id
    session.refresh(version, ["feature_model"])
    if (
        version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 2. (Opcional pero recomendado) Verificar que el parent_id, si existe, pertenece a la misma versión del modelo
    if feature_in.parent_id:
        parent_feature = crud.get_feature(
            session=session, feature_id=feature_in.parent_id
        )
        if (
            not parent_feature
            or parent_feature.feature_model_version_id
            != feature_in.feature_model_version_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Parent feature not found or does not belong to the same model.",
            )

    try:
        # La creación ahora sigue el patrón copy-on-write y devuelve la feature en la nueva versión
        feature = crud.create_feature(
            session=session, feature_in=feature_in, user=current_user
        )
        return feature
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{feature_id}/", dependencies=[Depends(VerifiedUser)], response_model=FeaturePublic
)
def read_feature(*, feature_id: uuid.UUID, session: SessionDep) -> FeaturePublic:
    """
    Get a specific feature by ID.
    """
    feature = crud.get_feature(session=session, feature_id=feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature


@router.patch("/{feature_id}/", response_model=FeaturePublic)
def update_feature(
    *,
    feature_id: uuid.UUID,
    session: SessionDep,
    feature_in: FeatureUpdate,
    current_user: ModelDesignerUser,
) -> FeaturePublic:
    """
    Update a feature.
    """
    db_feature = crud.get_feature(session=session, feature_id=feature_id)
    if not db_feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    # Refrescamos la relación para acceder a feature_model_version y luego a feature_model
    session.refresh(db_feature, ["feature_model_version"])
    session.refresh(db_feature.feature_model_version, ["feature_model"])

    # Verificar permisos (el usuario debe ser dueño del modelo padre)
    if (
        db_feature.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        # La función ahora devuelve la feature en la *nueva* versión
        new_feature = crud.update_feature(
            session=session,
            db_feature=db_feature,
            feature_in=feature_in,
            user=current_user,
        )
        return new_feature
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{feature_id}/", response_model=Message)
def delete_feature(
    *,
    feature_id: uuid.UUID,
    session: SessionDep,
    current_user: ModelDesignerUser,
) -> Message:
    """
    Delete a feature.
    """
    db_feature = crud.get_feature(session=session, feature_id=feature_id)
    if not db_feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    session.refresh(db_feature, ["feature_model_version"])
    session.refresh(db_feature.feature_model_version, ["feature_model"])

    if (
        db_feature.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud.delete_feature(session=session, db_feature=db_feature, user=current_user)
    return Message(message="Feature deleted in new model version created successfully.")
