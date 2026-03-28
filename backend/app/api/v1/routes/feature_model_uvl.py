"""
Endpoints para gestionar representación UVL de Feature Models.
Permite trabajar en paralelo modelo visual + texto UVL.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.api.deps import (
    AsyncCurrentUser,
    AsyncFeatureModelVersionRepoDep,
    get_verified_user,
)
from app.exceptions import FeatureModelVersionNotFoundException, ForbiddenException
from app.models import FeatureModelVersionUVLPublic, FeatureModelVersionUVLUpdate
from app.services.feature_model import FeatureModelExportService

router = APIRouter(
    prefix="/feature-models",
    tags=["Feature Models - UVL"],
    dependencies=[Depends(get_verified_user)],
)


def _validate_uvl_content(uvl_content: str) -> str:
    """Validaciones mínimas de UVL para evitar guardar payloads vacíos."""
    normalized = uvl_content.strip()
    if not normalized:
        raise ValueError("UVL content cannot be empty")

    if "features" not in normalized:
        raise ValueError("UVL content must include a 'features' section")

    return normalized


@router.get(
    "/{model_id}/versions/{version_id}/uvl",
    response_model=FeatureModelVersionUVLPublic,
    summary="Get effective UVL for a feature model version",
)
async def get_feature_model_version_uvl(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: uuid.UUID = Path(..., description="Version UUID"),
    version_repo: AsyncFeatureModelVersionRepoDep,
) -> FeatureModelVersionUVLPublic:
    """Obtiene el UVL efectivo (guardado o generado desde estructura)."""
    version = await version_repo.get_version_with_full_structure(version_id)

    if not version or version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

    if version.uvl_content and version.uvl_content.strip():
        return FeatureModelVersionUVLPublic(
            version_id=version.id,
            feature_model_id=version.feature_model_id,
            uvl_content=version.uvl_content,
            source="stored",
        )

    generated_uvl = FeatureModelExportService(version).export_to_uvl()
    return FeatureModelVersionUVLPublic(
        version_id=version.id,
        feature_model_id=version.feature_model_id,
        uvl_content=generated_uvl,
        source="generated",
    )


@router.put(
    "/{model_id}/versions/{version_id}/uvl",
    response_model=FeatureModelVersionUVLPublic,
    status_code=status.HTTP_200_OK,
    summary="Save UVL for a feature model version",
)
async def save_feature_model_version_uvl(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: uuid.UUID = Path(..., description="Version UUID"),
    data: FeatureModelVersionUVLUpdate,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> FeatureModelVersionUVLPublic:
    """Guarda UVL textual para edición paralela durante el modelado visual."""
    version = await version_repo.get_version_with_full_structure(version_id)

    if not version or version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

    # Solo owner del modelo o superuser pueden persistir cambios de UVL
    if (
        version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise ForbiddenException(detail="Not enough permissions to update UVL")

    try:
        normalized_uvl = _validate_uvl_content(data.uvl_content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    version.uvl_content = normalized_uvl
    version_repo.session.add(version)
    await version_repo.session.commit()
    await version_repo.session.refresh(version)

    return FeatureModelVersionUVLPublic(
        version_id=version.id,
        feature_model_id=version.feature_model_id,
        uvl_content=version.uvl_content,
        source="stored",
    )


@router.post(
    "/{model_id}/versions/{version_id}/uvl/sync-from-structure",
    response_model=FeatureModelVersionUVLPublic,
    status_code=status.HTTP_200_OK,
    summary="Sync UVL from current visual structure",
)
async def sync_feature_model_version_uvl_from_structure(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: uuid.UUID = Path(..., description="Version UUID"),
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> FeatureModelVersionUVLPublic:
    """Regenera UVL desde la estructura del modelo y lo persiste."""
    version = await version_repo.get_version_with_full_structure(version_id)

    if not version or version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

    if (
        version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise ForbiddenException(detail="Not enough permissions to sync UVL")

    version.uvl_content = FeatureModelExportService(version).export_to_uvl()
    version_repo.session.add(version)
    await version_repo.session.commit()
    await version_repo.session.refresh(version)

    return FeatureModelVersionUVLPublic(
        version_id=version.id,
        feature_model_id=version.feature_model_id,
        uvl_content=version.uvl_content,
        source="synced",
    )
