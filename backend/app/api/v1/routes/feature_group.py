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
from app.exceptions import (
    FeatureGroupNotFoundException,
    FeatureGroupAccessDeniedException,
    InvalidFeatureGroupException,
)

router = APIRouter(prefix="/feature-groups", tags=["feature-groups"])


@router.get(
    "/",
    response_model=list[FeatureGroupPublic],
    summary="Listar feature groups",
    description="""Devuelve una lista de feature groups con filtros opcionales.

    Use cases: navegación de grupos, listados de administración y filtros por tipo.
    Permissions required: authenticated.
    Filtros: feature_model_version_id, parent_feature_id, group_type, include_inactive, skip/limit.
    """,
    responses={
        200: {
            "description": "Lista de feature groups",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "1111...",
                            "group_type": "or",
                            "parent_feature_id": "2222...",
                        }
                    ]
                }
            },
        },
        400: {"description": "Parámetros inválidos"},
        403: {"description": "Acceso denegado"},
    },
)
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


@router.get(
    "/{group_id}",
    response_model=FeatureGroupPublic,
    summary="Obtener feature group por ID",
    description="""Recupera un feature group específico por su identificador.

    Use cases: mostrar detalle en UI, validar estado antes de editar.
    Permissions required: authenticated.
    """,
    responses={
        200: {
            "description": "Feature group encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "id": "1111...",
                        "group_type": "or",
                        "parent_feature_id": "2222...",
                    }
                }
            },
        },
        404: {"description": "Feature group no encontrado"},
        403: {"description": "Acceso denegado"},
    },
)
async def read_feature_group(
    *,
    group_id: uuid.UUID,
    feature_group_repo: AsyncFeatureGroupRepoDep,
) -> FeatureGroupPublic:
    """Obtener un grupo por ID."""
    group = await feature_group_repo.get(group_id=group_id)
    if not group:
        raise FeatureGroupNotFoundException(group_id=str(group_id))
    return group


@router.post(
    "/",
    response_model=FeatureGroupPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear feature group",
    description="""Crea un feature group y genera una nueva versión del modelo (copy-on-write).

    Use cases: definir grupos or/alternative dentro del árbol de features.
    Permissions required: authenticated (owner or model designer).
    Note: La operación dispara nueva versión del modelo.
    """,
    responses={
        201: {
            "description": "Feature group creado en nueva versión",
            "content": {
                "application/json": {
                    "example": {
                        "id": "1111...",
                        "group_type": "or",
                        "parent_feature_id": "2222...",
                    }
                }
            },
        },
        400: {"description": "Solicitud inválida o grupo inconsistente"},
        404: {"description": "Parent feature no encontrada"},
        403: {"description": "Acceso denegado"},
    },
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
        raise FeatureGroupAccessDeniedException(
            group_id=str(group_in.parent_feature_id)
        )

    try:
        group = await feature_group_repo.create(
            data=group_in,
            user=current_user,
            feature_repo=feature_repo,
            feature_model_version_repo=feature_model_version_repo,
        )
        return group
    except (ValueError, RuntimeError) as e:
        raise InvalidFeatureGroupException(reason=str(e))


@router.patch(
    "/{group_id}",
    response_model=FeatureGroupPublic,
    summary="Actualizar feature group (parcial)",
    description="""Actualiza parcialmente un feature group y crea una nueva versión del modelo (copy-on-write).

    Use cases: cambiar cardinalidad o parent feature.
    Permissions required: authenticated (owner or model designer).
    Behavior: copy-on-write; el grupo original permanece en la versión anterior.
    """,
    responses={
        200: {
            "description": "Feature group actualizado en nueva versión",
            "content": {
                "application/json": {
                    "example": {
                        "id": "1111...",
                        "group_type": "alt",
                        "min_cardinality": 1,
                        "max_cardinality": 1,
                    }
                }
            },
        },
        400: {"description": "Datos inválidos o conflicto de grupo"},
        404: {"description": "Feature group no encontrado"},
        403: {"description": "Acceso denegado"},
    },
)
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
        raise FeatureGroupNotFoundException(group_id=str(group_id))

    await feature_group_repo.session.refresh(db_group, ["feature_model_version"])
    await feature_group_repo.session.refresh(
        db_group.feature_model_version, ["feature_model"]
    )

    if (
        db_group.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise FeatureGroupAccessDeniedException(group_id=str(group_id))

    try:
        return await feature_group_repo.update(
            db_group=db_group,
            data=group_in,
            user=current_user,
            feature_model_version_repo=feature_model_version_repo,
        )
    except (ValueError, RuntimeError) as e:
        raise InvalidFeatureGroupException(reason=str(e))


@router.put(
    "/{group_id}",
    response_model=FeatureGroupPublic,
    summary="Reemplazar feature group (completo)",
    description="""Reemplaza completamente un feature group y crea una nueva versión del modelo (copy-on-write).

    Use cases: reescritura completa de la estructura del grupo.
    Permissions required: authenticated (owner or model designer).
    Behavior: requiere todos los campos principales.
    """,
    responses={
        200: {
            "description": "Feature group reemplazado en nueva versión",
            "content": {
                "application/json": {
                    "example": {
                        "id": "1111...",
                        "group_type": "or",
                        "min_cardinality": 1,
                        "max_cardinality": 3,
                    }
                }
            },
        },
        400: {"description": "Datos inválidos o conflicto de grupo"},
        404: {"description": "Feature group no encontrado"},
        403: {"description": "Acceso denegado"},
    },
)
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
        raise FeatureGroupNotFoundException(group_id=str(group_id))

    await feature_group_repo.session.refresh(db_group, ["feature_model_version"])
    await feature_group_repo.session.refresh(
        db_group.feature_model_version, ["feature_model"]
    )

    if (
        db_group.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise FeatureGroupAccessDeniedException(group_id=str(group_id))

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
        raise InvalidFeatureGroupException(reason=str(e))


@router.delete(
    "/{group_id}",
    response_model=Message,
    summary="Eliminar feature group",
    description="""Elimina un feature group y crea una nueva versión del modelo.

    Use cases: remover grupos obsoletos.
    Permissions required: authenticated (owner or model designer).
    Note: La operación es atómica; crea una nueva versión sin el grupo.
    """,
    responses={
        200: {
            "description": "Eliminación exitosa",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Feature group deleted in new model version created successfully."
                    }
                }
            },
        },
        404: {"description": "Feature group no encontrado"},
        403: {"description": "Acceso denegado"},
    },
)
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
        raise FeatureGroupNotFoundException(group_id=str(group_id))

    # Cargar las relaciones necesarias para la verificación de permisos
    await feature_group_repo.session.refresh(db_group, ["feature_model_version"])
    await feature_group_repo.session.refresh(
        db_group.feature_model_version, ["feature_model"]
    )

    if (
        db_group.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise FeatureGroupAccessDeniedException(group_id=str(group_id))

    await feature_group_repo.delete(
        db_group=db_group,
        user=current_user,
        feature_model_version_repo=feature_model_version_repo,
    )
    return Message(
        message="Feature group deleted in new model version created successfully."
    )


@router.patch(
    "/{group_id}/activate",
    response_model=FeatureGroupPublic,
    summary="Activar feature group",
    description="""Marca un feature group como activo (`is_active=true`).

    Use cases: reactivar grupos desactivados.
    Permissions required: authenticated (owner or model designer).
    """,
    responses={
        200: {
            "description": "Feature group activado",
            "content": {
                "application/json": {"example": {"id": "1111...", "is_active": True}}
            },
        },
        400: {"description": "Ya está activo"},
        404: {"description": "Feature group no encontrado"},
        403: {"description": "Acceso denegado"},
    },
)
async def activate_feature_group(
    *,
    group_id: uuid.UUID,
    current_user: ModelDesignerUser,
    feature_group_repo: AsyncFeatureGroupRepoDep,
) -> FeatureGroupPublic:
    """
    Activar un grupo de features (is_active=true).
    """
    db_group = await feature_group_repo.get(group_id=group_id)
    if not db_group:
        raise FeatureGroupNotFoundException(group_id=str(group_id))

    await feature_group_repo.session.refresh(db_group, ["feature_model_version"])
    await feature_group_repo.session.refresh(
        db_group.feature_model_version, ["feature_model"]
    )

    if (
        db_group.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise FeatureGroupAccessDeniedException(group_id=str(group_id))

    if db_group.is_active:
        raise HTTPException(status_code=400, detail="Feature group is already active")

    return await feature_group_repo.activate(db_group)


@router.patch(
    "/{group_id}/deactivate",
    response_model=FeatureGroupPublic,
    summary="Desactivar feature group",
    description="""Marca un feature group como inactivo (`is_active=false`).

    Use cases: deshabilitar un grupo temporalmente sin eliminarlo.
    Permissions required: authenticated (owner or model designer).
    """,
    responses={
        200: {
            "description": "Feature group desactivado",
            "content": {
                "application/json": {"example": {"id": "1111...", "is_active": False}}
            },
        },
        400: {"description": "Ya está inactivo"},
        404: {"description": "Feature group no encontrado"},
        403: {"description": "Acceso denegado"},
    },
)
async def deactivate_feature_group(
    *,
    group_id: uuid.UUID,
    current_user: ModelDesignerUser,
    feature_group_repo: AsyncFeatureGroupRepoDep,
) -> FeatureGroupPublic:
    """
    Desactivar un grupo de features (is_active=false).
    """
    db_group = await feature_group_repo.get(group_id=group_id)
    if not db_group:
        raise FeatureGroupNotFoundException(group_id=str(group_id))

    await feature_group_repo.session.refresh(db_group, ["feature_model_version"])
    await feature_group_repo.session.refresh(
        db_group.feature_model_version, ["feature_model"]
    )

    if (
        db_group.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise FeatureGroupAccessDeniedException(group_id=str(group_id))

    if not db_group.is_active:
        raise HTTPException(status_code=400, detail="Feature group is already inactive")

    return await feature_group_repo.deactivate(db_group)
