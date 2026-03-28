import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.api.deps import (
    AsyncFeatureRepoDep,
    AsyncFeatureGroupRepoDep,
    AsyncFeatureModelVersionRepoDep,
    ModelDesignerUser,
)
from app.models.common import Message
from app.models.feature_group import (
    FeatureGroup,
    FeatureGroupCreate,
    FeatureGroupPublic,
    FeatureGroupUpdate,
    FeatureGroupReplace,
)
from app.enums import FeatureGroupType

router = APIRouter(prefix="/feature-groups", tags=["feature-groups"])


@router.get("/", response_model=list[FeatureGroupPublic])
async def list_feature_groups(
    *,
    feature_group_repo: AsyncFeatureGroupRepoDep,
    feature_model_version_id: Optional[uuid.UUID] = None,
    parent_feature_id: Optional[uuid.UUID] = None,
    group_type: Optional[FeatureGroupType] = None,
    include_inactive: bool = False,
    skip: int = 0,
    limit: int = 100,
) -> list[FeatureGroupPublic]:
    """
    Listar grupos con filtros opcionales.

    Filtros soportados:
    - feature_model_version_id: limitar a una versión
    - parent_feature_id: filtrar por feature padre
    - group_type: alternative u or
    - include_inactive: incluir soft-deleted
    - skip/limit: paginación
    """
    stmt = select(FeatureGroup)
    if not include_inactive:
        stmt = stmt.where(FeatureGroup.is_active == True)
    if feature_model_version_id:
        stmt = stmt.where(
            FeatureGroup.feature_model_version_id == feature_model_version_id
        )
    if parent_feature_id:
        stmt = stmt.where(FeatureGroup.parent_feature_id == parent_feature_id)
    if group_type:
        stmt = stmt.where(FeatureGroup.group_type == group_type)

    stmt = stmt.offset(skip).limit(limit)
    result = await feature_group_repo.session.execute(stmt)
    return result.scalars().all()


@router.get("/{group_id}", response_model=FeatureGroupPublic)
async def read_feature_group(
    *,
    group_id: uuid.UUID,
    feature_group_repo: AsyncFeatureGroupRepoDep,
) -> FeatureGroupPublic:
    """Obtener un grupo por ID."""
    group = await feature_group_repo.get(group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Feature group not found.")
    return group


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


@router.patch("/{group_id}", response_model=FeatureGroupPublic)
async def update_feature_group(
    *,
    group_id: uuid.UUID,
    group_in: FeatureGroupUpdate,
    current_user: ModelDesignerUser,
    feature_group_repo: AsyncFeatureGroupRepoDep,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
) -> FeatureGroupPublic:
    """
    Actualizar parcialmente un grupo (copy-on-write).

    Crea una nueva versión del modelo con el grupo actualizado.
    """
    db_group = await feature_group_repo.get(group_id=group_id)
    if not db_group:
        raise HTTPException(status_code=404, detail="Feature group not found.")

    await feature_group_repo.session.refresh(db_group, ["feature_model_version"])
    await feature_group_repo.session.refresh(
        db_group.feature_model_version, ["feature_model"]
    )

    if (
        db_group.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    try:
        return await feature_group_repo.update(
            db_group=db_group,
            data=group_in,
            user=current_user,
            feature_model_version_repo=feature_model_version_repo,
        )
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{group_id}", response_model=FeatureGroupPublic)
async def replace_feature_group(
    *,
    group_id: uuid.UUID,
    group_in: FeatureGroupReplace,
    current_user: ModelDesignerUser,
    feature_group_repo: AsyncFeatureGroupRepoDep,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
) -> FeatureGroupPublic:
    """
    Reemplazar completamente un grupo (copy-on-write).

    Requiere todos los campos principales del grupo.
    """
    db_group = await feature_group_repo.get(group_id=group_id)
    if not db_group:
        raise HTTPException(status_code=404, detail="Feature group not found.")

    await feature_group_repo.session.refresh(db_group, ["feature_model_version"])
    await feature_group_repo.session.refresh(
        db_group.feature_model_version, ["feature_model"]
    )

    if (
        db_group.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    try:
        update_data = FeatureGroupUpdate(
            group_type=group_in.group_type,
            parent_feature_id=group_in.parent_feature_id,
            min_cardinality=group_in.min_cardinality,
            max_cardinality=group_in.max_cardinality,
        )
        return await feature_group_repo.update(
            db_group=db_group,
            data=update_data,
            user=current_user,
            feature_model_version_repo=feature_model_version_repo,
        )
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{group_id}", response_model=Message)
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
