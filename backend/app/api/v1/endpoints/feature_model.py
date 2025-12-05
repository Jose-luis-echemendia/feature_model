import uuid

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_cache.decorator import cache

from app.api.deps import (
    AsyncFeatureModelRepoDep,
    AsyncDomainRepoDep,
    AsyncCurrentUser,
    ModelDesignerUser,
    VerifiedUser,
)
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
@cache(expire=300)  # Cache por 5 minutos
async def read_feature_models(
    feature_model_repo: AsyncFeatureModelRepoDep,
    skip: int = 0,
    limit: int = 100,
    domain_id: Optional[uuid.UUID] = None,
) -> FeatureModelListResponse:
    """
    Retrieve all feature models.
    - `domain_id`: Optionally filter models by a specific domain.
    """
    if domain_id:
        models = await feature_model_repo.get_by_domain(
            domain_id=domain_id, skip=skip, limit=limit
        )
        count = await feature_model_repo.count(domain_id=domain_id)
    else:
        models = await feature_model_repo.get_all(skip=skip, limit=limit)
        count = await feature_model_repo.count()

    return FeatureModelListResponse.create(
        data=models,
        count=count,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/", response_model=FeatureModelPublic, status_code=status.HTTP_201_CREATED
)
async def create_feature_model(
    *,
    feature_model_repo: AsyncFeatureModelRepoDep,
    domain_repo: AsyncDomainRepoDep,
    model_in: FeatureModelCreate,
    current_user: AsyncCurrentUser,
) -> FeatureModelPublic:
    """
    Create a new feature model.
    Accessible only to Model Designers and Admins.
    """
    # Verificar que el usuario tiene permisos (MODEL_DESIGNER o ADMIN)
    from app.enums import UserRole

    if current_user.role not in [
        UserRole.MODEL_DESIGNER,
        UserRole.ADMIN,
        UserRole.DEVELOPER,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Only Model Designers and Admins can create feature models.",
        )

    # Verificar que el dominio existe
    domain = await domain_repo.get(model_in.domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found.")

    try:
        model = await feature_model_repo.create(data=model_in, owner_id=current_user.id)
        return model
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{model_id}/",
    dependencies=[Depends(VerifiedUser)],
    response_model=FeatureModelPublic,
)
@cache(expire=300)  # Cache por 5 minutos
async def read_feature_model(
    *, model_id: uuid.UUID, feature_model_repo: AsyncFeatureModelRepoDep
) -> FeatureModelPublic:
    """
    Get a specific feature model by ID.
    """
    model = await feature_model_repo.get(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Feature Model not found")
    return model


@router.patch("/{model_id}/", response_model=FeatureModelPublic)
async def update_feature_model(
    *,
    model_id: uuid.UUID,
    feature_model_repo: AsyncFeatureModelRepoDep,
    model_in: FeatureModelUpdate,
    current_user: AsyncCurrentUser,
) -> FeatureModelPublic:
    """
    Update a feature model.
    """
    # Verificar que el usuario tiene permisos (MODEL_DESIGNER o ADMIN)
    from app.enums import UserRole

    if current_user.role not in [
        UserRole.MODEL_DESIGNER,
        UserRole.ADMIN,
        UserRole.DEVELOPER,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Only Model Designers and Admins can update feature models.",
        )

    db_model = await feature_model_repo.get(model_id)
    if not db_model:
        raise HTTPException(status_code=404, detail="Feature Model not found")

    # Verificar si el usuario es el propietario o un admin
    if db_model.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        updated_model = await feature_model_repo.update(
            db_feature_model=db_model, data=model_in
        )
        return updated_model
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{model_id}/", response_model=Message)
async def delete_feature_model(
    *,
    model_id: uuid.UUID,
    feature_model_repo: AsyncFeatureModelRepoDep,
    current_user: AsyncCurrentUser,
) -> Message:
    """
    Delete a feature model.
    """
    # Verificar que el usuario tiene permisos (MODEL_DESIGNER o ADMIN)
    from app.enums import UserRole

    if current_user.role not in [
        UserRole.MODEL_DESIGNER,
        UserRole.ADMIN,
        UserRole.DEVELOPER,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Only Model Designers and Admins can delete feature models.",
        )

    db_model = await feature_model_repo.get(model_id)
    if not db_model:
        raise HTTPException(status_code=404, detail="Feature Model not found")

    if db_model.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    await feature_model_repo.delete(db_model)
    return Message(message="Feature Model deleted successfully.")
