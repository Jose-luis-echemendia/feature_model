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
from pydantic import BaseModel
from app.services.feature_model import (
    FeatureModelExportService,
    FeatureModelUVLImporter,
)

router = APIRouter(
    prefix="/feature-models",
    tags=["Feature Models - UVL"],
    dependencies=[Depends(get_verified_user)],
)


class FeatureModelUVLDiff(BaseModel):
    features_added: list[str]
    features_removed: list[str]
    relations_added: list[tuple[str, str, str]]
    relations_removed: list[tuple[str, str, str]]
    constraints_added: list[str]
    constraints_removed: list[str]


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


@router.post(
    "/{model_id}/versions/{version_id}/uvl/apply-to-structure",
    response_model=FeatureModelVersionUVLPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Apply UVL to create a new model structure",
)
async def apply_feature_model_uvl_to_structure(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: uuid.UUID = Path(..., description="Source Version UUID"),
    data: FeatureModelVersionUVLUpdate,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> FeatureModelVersionUVLPublic:
    """Aplicar UVL para crear una nueva versión estructurada del modelo."""
    version = await version_repo.get_version_with_full_structure(version_id)

    if not version or version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

    if (
        version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise ForbiddenException(detail="Not enough permissions to apply UVL")

    importer = FeatureModelUVLImporter(
        session=version_repo.session,
        feature_model=version.feature_model,
        user=current_user,
    )
    new_version = await importer.apply_uvl(data.uvl_content)

    return FeatureModelVersionUVLPublic(
        version_id=new_version.id,
        feature_model_id=new_version.feature_model_id,
        uvl_content=new_version.uvl_content or "",
        source="applied",
    )


@router.post(
    "/{model_id}/versions/{version_id}/uvl/diff",
    response_model=FeatureModelUVLDiff,
    status_code=status.HTTP_200_OK,
    summary="Diff UVL against current structure",
)
async def diff_feature_model_uvl(
    *,
    model_id: uuid.UUID = Path(..., description="Feature Model UUID"),
    version_id: uuid.UUID = Path(..., description="Source Version UUID"),
    data: FeatureModelVersionUVLUpdate,
    version_repo: AsyncFeatureModelVersionRepoDep,
    current_user: AsyncCurrentUser,
) -> FeatureModelUVLDiff:
    """
    Compara UVL vs estructura de la versión actual y devuelve diferencias.

    Útil para previsualizar cambios antes de aplicar UVL.
    """
    version = await version_repo.get_version_with_full_structure(version_id)

    if not version or version.feature_model_id != model_id:
        raise FeatureModelVersionNotFoundException(version_id=str(version_id))

    if (
        version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise ForbiddenException(detail="Not enough permissions to diff UVL")

    importer = FeatureModelUVLImporter(
        session=version_repo.session,
        feature_model=version.feature_model,
        user=current_user,
    )
    diff = importer.diff_uvl(data.uvl_content, version)
    return FeatureModelUVLDiff(**diff)
