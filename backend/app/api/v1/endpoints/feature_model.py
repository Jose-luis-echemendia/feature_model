import uuid

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app import crud
from app.api.deps import SessionDep, ModelDesignerUser, VerifiedUser
from app.models.common import Message
from app.models.feature_model import (
    FeatureModelCreate,
    FeatureModelListResponse,
    FeatureModelPublic,
    FeatureModelUpdate,
)

router = APIRouter(prefix="/feature-models", tags=["feature-models"])


@router.get(
    "/", dependencies=[Depends(VerifiedUser)], response_model=FeatureModelListResponse
)
def read_feature_models(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    domain_id: Optional[uuid.UUID] = None,
) -> FeatureModelListResponse:
    """
    Retrieve all feature models.
    - `domain_id`: Optionally filter models by a specific domain.
    """
    if domain_id:
        models = crud.get_feature_models_by_domain(
            session=session, domain_id=domain_id, skip=skip, limit=limit
        )
        count = crud.count_feature_models(session=session, domain_id=domain_id)
    else:
        models = crud.get_all_feature_models(session=session, skip=skip, limit=limit)
        count = crud.count_feature_models(session=session)

    return FeatureModelListResponse(data=models, count=count)


@router.post(
    "/", response_model=FeatureModelPublic, status_code=status.HTTP_201_CREATED
)
def create_feature_model(
    *,
    session: SessionDep,
    model_in: FeatureModelCreate,
    current_user: ModelDesignerUser,
) -> FeatureModelPublic:
    """
    Create a new feature model.
    Accessible only to Model Designers and Admins.
    """
    # Verificar que el dominio existe
    domain = crud.get_domain(session=session, domain_id=model_in.domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found.")

    try:
        model = crud.create_feature_model(
            session=session, feature_model_create=model_in, owner_id=current_user.id
        )
        return model
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{model_id}/",
    dependencies=[Depends(VerifiedUser)],
    response_model=FeatureModelPublic,
)
def read_feature_model(
    *, model_id: uuid.UUID, session: SessionDep
) -> FeatureModelPublic:
    """
    Get a specific feature model by ID.
    """
    model = crud.get_feature_model(session=session, feature_model_id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Feature Model not found")
    return model


@router.patch("/{model_id}/", response_model=FeatureModelPublic)
def update_feature_model(
    *,
    model_id: uuid.UUID,
    session: SessionDep,
    model_in: FeatureModelUpdate,
    current_user: ModelDesignerUser,
) -> FeatureModelPublic:
    """
    Update a feature model.
    """
    db_model = crud.get_feature_model(session=session, feature_model_id=model_id)
    if not db_model:
        raise HTTPException(status_code=404, detail="Feature Model not found")
    # Opcional: verificar si el usuario es el propietario o un admin
    if db_model.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        updated_model = crud.update_feature_model(
            session=session, db_feature_model=db_model, feature_model_in=model_in
        )
        return updated_model
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{model_id}/", response_model=Message)
def delete_feature_model(
    *, model_id: uuid.UUID, session: SessionDep, current_user: ModelDesignerUser
) -> Message:
    """
    Delete a feature model.
    """
    db_model = crud.get_feature_model(session=session, feature_model_id=model_id)
    if not db_model:
        raise HTTPException(status_code=404, detail="Feature Model not found")
    if db_model.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud.delete_feature_model(session=session, db_feature_model=db_model)
    return Message(detail="Feature Model deleted successfully.")
