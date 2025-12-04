import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import (
    AsyncFeatureRepoDep,
    AsyncFeatureModelRepoDep,
    AsyncCurrentUser,
    VerifiedUser,
)
from app.models import (
    FeatureCreate,
    FeaturePublic,
    FeatureUpdate,
    FeaturePublicWithChildren,
    Message,
)


router = APIRouter(prefix="/features", tags=["features"])


@router.get(
    "/",
    dependencies=[Depends(VerifiedUser)],
    response_model=list[FeaturePublicWithChildren],
)
async def read_features_by_model(
    *,
    feature_repo: AsyncFeatureRepoDep,
    feature_model_version_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[FeaturePublicWithChildren]:
    """
    Retrieve all features for a specific feature model version, structured as a tree.
    """
    root_features = await feature_repo.get_as_tree(
        feature_model_version_id=feature_model_version_id,
        skip=skip,
        limit=limit,
    )
    return root_features


@router.post("/", response_model=FeaturePublic, status_code=status.HTTP_201_CREATED)
async def create_feature(
    *,
    feature_repo: AsyncFeatureRepoDep,
    feature_model_repo: AsyncFeatureModelRepoDep,
    feature_in: FeatureCreate,
    current_user: AsyncCurrentUser,
) -> FeaturePublic:
    """
    Create a new feature within a feature model.
    Only accessible to Model Designers and Admins.
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
            detail="Not enough permissions. Only Model Designers and Admins can create features.",
        )

    # 1. Verificar que la versión del modelo existe
    # Primero obtenemos el feature model para verificar la versión
    # Por ahora, asumimos que feature_in.feature_model_version_id es válido
    # Nota: El repositorio de feature ya valida esto internamente

    # 2. Validar parent_id si existe (el repositorio también lo hace)
    if feature_in.parent_id:
        parent_feature = await feature_repo.get(feature_in.parent_id)
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
        # La creación sigue el patrón copy-on-write
        feature = await feature_repo.create(data=feature_in, user=current_user)
        return feature
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{feature_id}/", dependencies=[Depends(VerifiedUser)], response_model=FeaturePublic
)
async def read_feature(
    *, feature_id: uuid.UUID, feature_repo: AsyncFeatureRepoDep
) -> FeaturePublic:
    """
    Get a specific feature by ID.
    """
    feature = await feature_repo.get(feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature


@router.patch("/{feature_id}/", response_model=FeaturePublic)
async def update_feature(
    *,
    feature_id: uuid.UUID,
    feature_repo: AsyncFeatureRepoDep,
    feature_in: FeatureUpdate,
    current_user: AsyncCurrentUser,
) -> FeaturePublic:
    """
    Update a feature.
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
            detail="Not enough permissions. Only Model Designers and Admins can update features.",
        )

    db_feature = await feature_repo.get(feature_id)
    if not db_feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    # Nota: Las validaciones de group_id se podrían mover al repositorio
    # Por ahora, mantenemos la validación básica aquí
    # La validación completa de permisos y relaciones se hace en el repositorio

    try:
        # La función devuelve la feature en la *nueva* versión
        new_feature = await feature_repo.update(
            db_feature=db_feature,
            data=feature_in,
            user=current_user,
        )
        return new_feature
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{feature_id}/", response_model=Message)
async def delete_feature(
    *,
    feature_id: uuid.UUID,
    feature_repo: AsyncFeatureRepoDep,
    current_user: AsyncCurrentUser,
) -> Message:
    """
    Delete a feature.
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
            detail="Not enough permissions. Only Model Designers and Admins can delete features.",
        )

    db_feature = await feature_repo.get(feature_id)
    if not db_feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    await feature_repo.delete(db_feature=db_feature, user=current_user)
    return Message(message="Feature deleted in new model version created successfully.")
