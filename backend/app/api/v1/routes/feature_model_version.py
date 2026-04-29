import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from pydantic import BaseModel
from sqlmodel import select

from app.api.deps import (
    AsyncFeatureModelRepoDep,
    AsyncFeatureModelVersionRepoDep,
    ModelDesignerUser,
    VerifiedUser,
)
from app.exceptions import (
    FeatureModelNotFoundException,
    FeatureModelVersionNotFoundException,
    ForbiddenException,
)
from app.models.feature_model_version import (
    FeatureModelVersionPublic,
    FeatureModelVersion,
)
from app.services.feature_model import FeatureModelVersionManager
from app.core.cache import user_key_builder

router = APIRouter(
    prefix="/feature-models",
    tags=["Feature Models - Versions"],
)


class FeatureModelVersionCreateRequest(BaseModel):
    source_version_id: Optional[uuid.UUID] = None
    description: Optional[str] = None


@router.get(
    "/{model_id}/versions",
    dependencies=[Depends(VerifiedUser)],
    response_model=list[FeatureModelVersionPublic],
)
@cache(expire=300, key_builder=user_key_builder)
async def list_feature_model_versions(
    *,
    model_id: uuid.UUID,
    feature_model_repo: AsyncFeatureModelRepoDep,
    version_repo: AsyncFeatureModelVersionRepoDep,
) -> list[FeatureModelVersionPublic]:
    """Listar todas las versiones de un Feature Model."""
    model = await feature_model_repo.get(model_id)
    if not model:
        raise FeatureModelNotFoundException(model_id=str(model_id))

    stmt = select(FeatureModelVersion).where(
        FeatureModelVersion.feature_model_id == model_id
    )
    result = await version_repo.session.execute(stmt)
    return result.scalars().all()


@router.get(
    "/{model_id}/versions/{version_id}",
    dependencies=[Depends(VerifiedUser)],
    response_model=FeatureModelVersionPublic,
)
@cache(expire=300, key_builder=user_key_builder)
async def read_feature_model_version(
    *,
    model_id: uuid.UUID,
    version_id: uuid.UUID,
    feature_model_repo: AsyncFeatureModelRepoDep,
    version_repo: AsyncFeatureModelVersionRepoDep,
) -> FeatureModelVersionPublic:
    """Obtener una versión específica de un Feature Model."""
    model = await feature_model_repo.get(model_id)
    if not model:
        raise FeatureModelNotFoundException(model_id=str(model_id))

    version = await version_repo.get(version_id)
    if not version or version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

    return version


@router.post(
    "/{model_id}/versions",
    dependencies=[Depends(ModelDesignerUser)],
    response_model=FeatureModelVersionPublic,
)
async def create_feature_model_version(
    *,
    model_id: uuid.UUID,
    payload: FeatureModelVersionCreateRequest,
    feature_model_repo: AsyncFeatureModelRepoDep,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: ModelDesignerUser,
) -> FeatureModelVersionPublic:
    """Crear una nueva versión de un Feature Model (copy-on-write)."""
    model = await feature_model_repo.get(model_id)
    if not model:
        raise FeatureModelNotFoundException(model_id=str(model_id))

    if model.owner_id != current_user.id and not current_user.is_superuser:
        raise ForbiddenException(detail="Not enough permissions to create versions")

    source_version = None
    if payload.source_version_id:
        source_version = await version_repo.get(payload.source_version_id)
        if not source_version or source_version.feature_model_id != model_id:
            raise FeatureModelVersionNotFoundException(
                version_id=str(payload.source_version_id)
            )

    manager = FeatureModelVersionManager(
        session=version_repo.session,
        feature_model=model,
        user=current_user,
    )
    new_version = await manager.create_new_version(
        source_version=source_version,
        description=payload.description,
    )
    return new_version


@router.patch(
    "/{model_id}/versions/{version_id}/publish",
    dependencies=[Depends(ModelDesignerUser)],
    response_model=FeatureModelVersionPublic,
)
async def publish_feature_model_version(
    *,
    model_id: uuid.UUID,
    version_id: uuid.UUID,
    feature_model_repo: AsyncFeatureModelRepoDep,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: ModelDesignerUser,
) -> FeatureModelVersionPublic:
    """Publicar una versión (cambia estado a PUBLISHED y genera snapshot)."""
    model = await feature_model_repo.get(model_id)
    if not model:
        raise FeatureModelNotFoundException(model_id=str(model_id))

    if model.owner_id != current_user.id and not current_user.is_superuser:
        raise ForbiddenException(detail="Not enough permissions to publish versions")

    version = await version_repo.get(version_id)
    if not version or version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

    manager = FeatureModelVersionManager(
        session=version_repo.session,
        feature_model=model,
        user=current_user,
    )
    return await manager.publish_version(version=version, validate=True)


@router.patch(
    "/{model_id}/versions/{version_id}/archive",
    dependencies=[Depends(ModelDesignerUser)],
    response_model=FeatureModelVersionPublic,
)
async def archive_feature_model_version(
    *,
    model_id: uuid.UUID,
    version_id: uuid.UUID,
    feature_model_repo: AsyncFeatureModelRepoDep,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: ModelDesignerUser,
) -> FeatureModelVersionPublic:
    """Archivar una versión (cambia estado a ARCHIVED)."""
    model = await feature_model_repo.get(model_id)
    if not model:
        raise FeatureModelNotFoundException(model_id=str(model_id))

    if model.owner_id != current_user.id and not current_user.is_superuser:
        raise ForbiddenException(detail="Not enough permissions to archive versions")

    version = await version_repo.get(version_id)
    if not version or version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

    manager = FeatureModelVersionManager(
        session=version_repo.session,
        feature_model=model,
        user=current_user,
    )
    return await manager.archive_version(version=version)


@router.patch(
    "/{model_id}/versions/{version_id}/restore",
    dependencies=[Depends(ModelDesignerUser)],
    response_model=FeatureModelVersionPublic,
)
async def restore_feature_model_version(
    *,
    model_id: uuid.UUID,
    version_id: uuid.UUID,
    feature_model_repo: AsyncFeatureModelRepoDep,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: ModelDesignerUser,
) -> FeatureModelVersionPublic:
    """Restaurar una versión ARCHIVED a PUBLISHED."""
    model = await feature_model_repo.get(model_id)
    if not model:
        raise FeatureModelNotFoundException(model_id=str(model_id))

    if model.owner_id != current_user.id and not current_user.is_superuser:
        raise ForbiddenException(detail="Not enough permissions to restore versions")

    version = await version_repo.get(version_id)
    if not version or version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

    manager = FeatureModelVersionManager(
        session=version_repo.session,
        feature_model=model,
        user=current_user,
    )
    return await manager.restore_version(version=version)
