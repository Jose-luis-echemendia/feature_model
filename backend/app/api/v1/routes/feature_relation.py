import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.api.deps import (
    AsyncFeatureRepoDep,
    AsyncFeatureRelationRepoDep,
    AsyncFeatureModelVersionRepoDep,
    ModelDesignerUser,
)
from app.models.common import Message
from app.models.feature_relation import (
    FeatureRelation,
    FeatureRelationCreate,
    FeatureRelationPublic,
    FeatureRelationUpdate,
    FeatureRelationReplace,
)
from app.enums import FeatureRelationType
from app.exceptions import (
    FeatureRelationNotFoundException,
    FeatureRelationAccessDeniedException,
    InvalidFeatureRelationException,
)

router = APIRouter(prefix="/feature-relations", tags=["feature-relations"])


@router.get(
    "/",
    response_model=list[FeatureRelationPublic],
    summary="Listar feature relations",
    description="""Devuelve una lista de relaciones con filtros opcionales.

    Use cases: navegación, auditoría de relaciones requires/excludes, listados de administración.
    Permissions required: authenticated.
    Filtros: feature_model_version_id, feature_id, relation_type, include_inactive, skip/limit.
    """,
    responses={
        200: {
            "description": "Lista de relaciones",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "1111...",
                            "type": "requires",
                            "source_feature_id": "2222...",
                            "target_feature_id": "3333...",
                        }
                    ]
                }
            },
        },
        400: {"description": "Parámetros inválidos"},
        403: {"description": "Acceso denegado"},
    },
)
async def list_feature_relations(
    *,
    feature_relation_repo: AsyncFeatureRelationRepoDep,
    feature_model_version_id: Optional[uuid.UUID] = None,
    feature_id: Optional[uuid.UUID] = None,
    relation_type: Optional[FeatureRelationType] = None,
    include_inactive: bool = False,
    skip: int = 0,
    limit: int = 100,
) -> list[FeatureRelationPublic]:
    """
    Listar relaciones con filtros opcionales.

    Filtros soportados:
    - feature_model_version_id: limitar a una versión
    - feature_id: filtra relaciones donde la feature es source o target
    - relation_type: requires o excludes
    - include_inactive: incluir soft-deleted
    - skip/limit: paginación
    """
    stmt = select(FeatureRelation)
    if not include_inactive:
        stmt = stmt.where(FeatureRelation.is_active == True)
    if feature_model_version_id:
        stmt = stmt.where(
            FeatureRelation.feature_model_version_id == feature_model_version_id
        )
    if feature_id:
        stmt = stmt.where(
            (FeatureRelation.source_feature_id == feature_id)
            | (FeatureRelation.target_feature_id == feature_id)
        )
    if relation_type:
        stmt = stmt.where(FeatureRelation.type == relation_type)

    stmt = stmt.offset(skip).limit(limit)
    result = await feature_relation_repo.session.execute(stmt)
    return result.scalars().all()


@router.get(
    "/{relation_id}",
    response_model=FeatureRelationPublic,
    summary="Obtener feature relation por ID",
    description="""Recupera una relación específica por su identificador.

    Use cases: mostrar detalle en UI, validar antes de editar.
    Permissions required: authenticated.
    """,
    responses={
        200: {
            "description": "Relación encontrada",
            "content": {
                "application/json": {
                    "example": {
                        "id": "1111...",
                        "type": "requires",
                        "source_feature_id": "2222...",
                        "target_feature_id": "3333...",
                    }
                }
            },
        },
        404: {"description": "Relación no encontrada"},
        403: {"description": "Acceso denegado"},
    },
)
async def read_feature_relation(
    *,
    relation_id: uuid.UUID,
    feature_relation_repo: AsyncFeatureRelationRepoDep,
) -> FeatureRelationPublic:
    """Obtener una relación por ID."""
    relation = await feature_relation_repo.get(relation_id=relation_id)
    if not relation:
        raise FeatureRelationNotFoundException(relation_id=str(relation_id))
    return relation


@router.post(
    "/",
    response_model=FeatureRelationPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear feature relation",
    description="""Crea una relación y genera una nueva versión del modelo (copy-on-write).

    Use cases: añadir restricciones requires/excludes entre features.
    Permissions required: authenticated (owner or model designer).
    Note: La operación dispara nueva versión del modelo.
    """,
    responses={
        201: {
            "description": "Relación creada en nueva versión",
            "content": {
                "application/json": {
                    "example": {
                        "id": "1111...",
                        "type": "requires",
                        "source_feature_id": "2222...",
                        "target_feature_id": "3333...",
                    }
                }
            },
        },
        400: {"description": "Solicitud inválida o relación inconsistente"},
        404: {"description": "Source feature no encontrada"},
        403: {"description": "Acceso denegado"},
    },
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
        raise FeatureRelationAccessDeniedException()

    try:
        relation = await feature_relation_repo.create(
            data=relation_in,
            user=current_user,
            feature_repo=feature_repo,
            feature_model_version_repo=feature_model_version_repo,
        )
        return relation
    except ValueError as e:
        raise InvalidFeatureRelationException(reason=str(e))


@router.patch(
    "/{relation_id}",
    response_model=FeatureRelationPublic,
    summary="Actualizar feature relation (parcial)",
    description="""Actualiza parcialmente una relación y crea una nueva versión del modelo (copy-on-write).

    Use cases: cambiar tipo o endpoints de la relación.
    Permissions required: authenticated (owner or model designer).
    Behavior: copy-on-write; la relación original permanece en la versión anterior.
    """,
    responses={
        200: {
            "description": "Relación actualizada en nueva versión",
            "content": {
                "application/json": {
                    "example": {
                        "id": "1111...",
                        "type": "excludes",
                        "source_feature_id": "2222...",
                        "target_feature_id": "3333...",
                    }
                }
            },
        },
        400: {"description": "Datos inválidos o conflicto de relación"},
        404: {"description": "Relación no encontrada"},
        403: {"description": "Acceso denegado"},
    },
)
async def update_feature_relation(
    *,
    relation_id: uuid.UUID,
    relation_in: FeatureRelationUpdate,
    current_user: ModelDesignerUser,
    feature_relation_repo: AsyncFeatureRelationRepoDep,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
) -> FeatureRelationPublic:
    """
    Actualizar parcialmente una relación (copy-on-write).

    Crea una nueva versión del modelo con la relación actualizada.
    """
    db_relation = await feature_relation_repo.get(relation_id=relation_id)
    if not db_relation:
        raise FeatureRelationNotFoundException(relation_id=str(relation_id))

    await feature_relation_repo.session.refresh(db_relation, ["feature_model_version"])
    await feature_relation_repo.session.refresh(
        db_relation.feature_model_version, ["feature_model"]
    )

    if (
        db_relation.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise FeatureRelationAccessDeniedException(relation_id=str(relation_id))

    try:
        return await feature_relation_repo.update(
            db_relation=db_relation,
            data=relation_in,
            user=current_user,
            feature_model_version_repo=feature_model_version_repo,
        )
    except (ValueError, RuntimeError) as e:
        raise InvalidFeatureRelationException(reason=str(e))


@router.put(
    "/{relation_id}",
    response_model=FeatureRelationPublic,
    summary="Reemplazar feature relation (completo)",
    description="""Reemplaza completamente una relación y crea una nueva versión del modelo (copy-on-write).

    Use cases: reescritura completa de una relación.
    Permissions required: authenticated (owner or model designer).
    Behavior: requiere todos los campos principales.
    """,
    responses={
        200: {
            "description": "Relación reemplazada en nueva versión",
            "content": {
                "application/json": {
                    "example": {
                        "id": "1111...",
                        "type": "requires",
                        "source_feature_id": "2222...",
                        "target_feature_id": "3333...",
                    }
                }
            },
        },
        400: {"description": "Datos inválidos o conflicto de relación"},
        404: {"description": "Relación no encontrada"},
        403: {"description": "Acceso denegado"},
    },
)
async def replace_feature_relation(
    *,
    relation_id: uuid.UUID,
    relation_in: FeatureRelationReplace,
    current_user: ModelDesignerUser,
    feature_relation_repo: AsyncFeatureRelationRepoDep,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
) -> FeatureRelationPublic:
    """
    Reemplazar completamente una relación (copy-on-write).

    Requiere todos los campos principales de la relación.
    """
    db_relation = await feature_relation_repo.get(relation_id=relation_id)
    if not db_relation:
        raise FeatureRelationNotFoundException(relation_id=str(relation_id))

    await feature_relation_repo.session.refresh(db_relation, ["feature_model_version"])
    await feature_relation_repo.session.refresh(
        db_relation.feature_model_version, ["feature_model"]
    )

    if (
        db_relation.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise FeatureRelationAccessDeniedException(relation_id=str(relation_id))

    try:
        update_data = FeatureRelationUpdate(
            type=relation_in.type,
            source_feature_id=relation_in.source_feature_id,
            target_feature_id=relation_in.target_feature_id,
        )
        return await feature_relation_repo.update(
            db_relation=db_relation,
            data=update_data,
            user=current_user,
            feature_model_version_repo=feature_model_version_repo,
        )
    except (ValueError, RuntimeError) as e:
        raise InvalidFeatureRelationException(reason=str(e))


@router.delete(
    "/{relation_id}",
    response_model=Message,
    summary="Eliminar feature relation",
    description="""Elimina una relación y crea una nueva versión del modelo.

    Use cases: remover relaciones obsoletas.
    Permissions required: authenticated (owner or model designer).
    Note: La operación es atómica; crea una nueva versión sin la relación.
    """,
    responses={
        200: {
            "description": "Eliminación exitosa",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Feature relation deleted in new model version created successfully."
                    }
                }
            },
        },
        404: {"description": "Relación no encontrada"},
        403: {"description": "Acceso denegado"},
    },
)
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
        raise FeatureRelationNotFoundException(relation_id=str(relation_id))

    # Cargar las relaciones necesarias para la verificación de permisos
    await feature_relation_repo.session.refresh(db_relation, ["feature_model_version"])
    await feature_relation_repo.session.refresh(
        db_relation.feature_model_version, ["feature_model"]
    )

    if (
        db_relation.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise FeatureRelationAccessDeniedException(relation_id=str(relation_id))

    await feature_relation_repo.delete(
        db_relation=db_relation,
        user=current_user,
        feature_model_version_repo=feature_model_version_repo,
    )
    return Message(
        message="Feature relation deleted in new model version created successfully."
    )


@router.patch(
    "/{relation_id}/activate",
    response_model=FeatureRelationPublic,
    summary="Activar feature relation",
    description="""Marca una relación como activa (`is_active=true`).

    Use cases: reactivar relaciones desactivadas.
    Permissions required: authenticated (owner or model designer).
    """,
    responses={
        200: {
            "description": "Relación activada",
            "content": {
                "application/json": {"example": {"id": "1111...", "is_active": True}}
            },
        },
        400: {"description": "Ya está activa"},
        404: {"description": "Relación no encontrada"},
        403: {"description": "Acceso denegado"},
    },
)
async def activate_feature_relation(
    *,
    relation_id: uuid.UUID,
    current_user: ModelDesignerUser,
    feature_relation_repo: AsyncFeatureRelationRepoDep,
) -> FeatureRelationPublic:
    """
    Activar una relación (is_active=true).
    """
    db_relation = await feature_relation_repo.get(relation_id=relation_id)
    if not db_relation:
        raise FeatureRelationNotFoundException(relation_id=str(relation_id))

    await feature_relation_repo.session.refresh(db_relation, ["feature_model_version"])
    await feature_relation_repo.session.refresh(
        db_relation.feature_model_version, ["feature_model"]
    )

    if (
        db_relation.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise FeatureRelationAccessDeniedException(relation_id=str(relation_id))

    if db_relation.is_active:
        raise HTTPException(
            status_code=400, detail="Feature relation is already active"
        )

    return await feature_relation_repo.activate(db_relation)


@router.patch(
    "/{relation_id}/deactivate",
    response_model=FeatureRelationPublic,
    summary="Desactivar feature relation",
    description="""Marca una relación como inactiva (`is_active=false`).

    Use cases: deshabilitar una relación temporalmente sin eliminarla.
    Permissions required: authenticated (owner or model designer).
    """,
    responses={
        200: {
            "description": "Relación desactivada",
            "content": {
                "application/json": {"example": {"id": "1111...", "is_active": False}}
            },
        },
        400: {"description": "Ya está inactiva"},
        404: {"description": "Relación no encontrada"},
        403: {"description": "Acceso denegado"},
    },
)
async def deactivate_feature_relation(
    *,
    relation_id: uuid.UUID,
    current_user: ModelDesignerUser,
    feature_relation_repo: AsyncFeatureRelationRepoDep,
) -> FeatureRelationPublic:
    """
    Desactivar una relación (is_active=false).
    """
    db_relation = await feature_relation_repo.get(relation_id=relation_id)
    if not db_relation:
        raise FeatureRelationNotFoundException(relation_id=str(relation_id))

    await feature_relation_repo.session.refresh(db_relation, ["feature_model_version"])
    await feature_relation_repo.session.refresh(
        db_relation.feature_model_version, ["feature_model"]
    )

    if (
        db_relation.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise FeatureRelationAccessDeniedException(relation_id=str(relation_id))

    if not db_relation.is_active:
        raise HTTPException(
            status_code=400, detail="Feature relation is already inactive"
        )

    return await feature_relation_repo.deactivate(db_relation)
