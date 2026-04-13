import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.api.deps import (
    AsyncConstraintRepoDep,
    AsyncFeatureModelVersionRepoDep,
    ModelDesignerUser,
)
from app.models.common import Message
from app.models.constraint import (
    Constraint,
    ConstraintCreate,
    ConstraintPublic,
    ConstraintUpdate,
    ConstraintReplace,
)
from app.exceptions import (
    ConstraintNotFoundException,
    ConstraintAccessDeniedException,
    InvalidConstraintOperationException,
)

router = APIRouter(prefix="/constraints", tags=["constraints"])


@router.get("/", response_model=list[ConstraintPublic])
async def list_constraints(
    *,
    constraint_repo: AsyncConstraintRepoDep,
    feature_model_version_id: Optional[uuid.UUID] = None,
    include_inactive: bool = False,
    skip: int = 0,
    limit: int = 100,
) -> list[ConstraintPublic]:
    """
    Listar constraints con filtros opcionales.

    Filtros soportados:
    - feature_model_version_id: limitar a una versión
    - include_inactive: incluir soft-deleted
    - skip/limit: paginación
    """
    stmt = select(Constraint)
    if not include_inactive:
        stmt = stmt.where(Constraint.is_active == True)
    if feature_model_version_id:
        stmt = stmt.where(
            Constraint.feature_model_version_id == feature_model_version_id
        )
    stmt = stmt.offset(skip).limit(limit)
    result = await constraint_repo.session.execute(stmt)
    return result.scalars().all()


@router.get("/{constraint_id}", response_model=ConstraintPublic)
async def read_constraint(
    *,
    constraint_id: uuid.UUID,
    constraint_repo: AsyncConstraintRepoDep,
) -> ConstraintPublic:
    """Obtener una constraint por ID."""
    constraint = await constraint_repo.get(constraint_id=constraint_id)
    if not constraint:
        raise ConstraintNotFoundException(constraint_id=str(constraint_id))
    return constraint


@router.post("/", response_model=ConstraintPublic, status_code=status.HTTP_201_CREATED)
async def create_constraint(
    *,
    constraint_in: ConstraintCreate,
    current_user: ModelDesignerUser,
    constraint_repo: AsyncConstraintRepoDep,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
):
    """
    Create a new complex constraint. This will trigger the creation of a new model version.
    """
    # Permisos: Verificamos que el usuario es dueño del modelo.
    version = await feature_model_version_repo.get(
        version_id=constraint_in.feature_model_version_id
    )
    if not version:
        raise HTTPException(status_code=404, detail="Feature Model Version not found.")

    # Cargar las relaciones necesarias para la verificación de permisos
    await feature_model_version_repo.session.refresh(version, ["feature_model"])

    if (
        version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise ConstraintAccessDeniedException(
            constraint_id=str(constraint_in.feature_model_version_id)
        )

    try:
        constraint = await constraint_repo.create(
            data=constraint_in,
            user=current_user,
            feature_model_version_repo=feature_model_version_repo,
        )
        return constraint
    except (ValueError, RuntimeError) as e:
        raise InvalidConstraintOperationException(reason=str(e))


@router.patch("/{constraint_id}", response_model=ConstraintPublic)
async def update_constraint(
    *,
    constraint_id: uuid.UUID,
    constraint_in: ConstraintUpdate,
    current_user: ModelDesignerUser,
    constraint_repo: AsyncConstraintRepoDep,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
) -> ConstraintPublic:
    """
    Actualizar parcialmente una constraint (copy-on-write).

    Crea una nueva versión del modelo con la constraint actualizada.
    """
    db_constraint = await constraint_repo.get(constraint_id=constraint_id)
    if not db_constraint:
        raise ConstraintNotFoundException(constraint_id=str(constraint_id))

    await constraint_repo.session.refresh(db_constraint, ["feature_model_version"])
    await constraint_repo.session.refresh(
        db_constraint.feature_model_version, ["feature_model"]
    )

    if (
        db_constraint.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise ConstraintAccessDeniedException(constraint_id=str(constraint_id))

    try:
        return await constraint_repo.update(
            db_constraint=db_constraint,
            data=constraint_in,
            user=current_user,
            feature_model_version_repo=feature_model_version_repo,
        )
    except (ValueError, RuntimeError) as e:
        raise InvalidConstraintOperationException(reason=str(e))


@router.put("/{constraint_id}", response_model=ConstraintPublic)
async def replace_constraint(
    *,
    constraint_id: uuid.UUID,
    constraint_in: ConstraintReplace,
    current_user: ModelDesignerUser,
    constraint_repo: AsyncConstraintRepoDep,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
) -> ConstraintPublic:
    """
    Reemplazar completamente una constraint (copy-on-write).

    Requiere todos los campos principales de la constraint.
    """
    db_constraint = await constraint_repo.get(constraint_id=constraint_id)
    if not db_constraint:
        raise ConstraintNotFoundException(constraint_id=str(constraint_id))

    await constraint_repo.session.refresh(db_constraint, ["feature_model_version"])
    await constraint_repo.session.refresh(
        db_constraint.feature_model_version, ["feature_model"]
    )

    if (
        db_constraint.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise ConstraintAccessDeniedException(constraint_id=str(constraint_id))

    try:
        update_data = ConstraintUpdate(
            description=constraint_in.description,
            expr_text=constraint_in.expr_text,
        )
        return await constraint_repo.update(
            db_constraint=db_constraint,
            data=update_data,
            user=current_user,
            feature_model_version_repo=feature_model_version_repo,
        )
    except (ValueError, RuntimeError) as e:
        raise InvalidConstraintOperationException(reason=str(e))


@router.delete("/{constraint_id}", response_model=Message)
async def delete_constraint(
    *,
    constraint_id: uuid.UUID,
    current_user: ModelDesignerUser,
    constraint_repo: AsyncConstraintRepoDep,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
):
    """
    Delete a complex constraint. This will trigger the creation of a new model version.
    """
    db_constraint = await constraint_repo.get(constraint_id=constraint_id)
    if not db_constraint:
        raise ConstraintNotFoundException(constraint_id=str(constraint_id))

    # Cargar las relaciones necesarias para la verificación de permisos
    await constraint_repo.session.refresh(db_constraint, ["feature_model_version"])
    await constraint_repo.session.refresh(
        db_constraint.feature_model_version, ["feature_model"]
    )

    if (
        db_constraint.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise ConstraintAccessDeniedException(constraint_id=str(constraint_id))

    await constraint_repo.delete(
        db_constraint=db_constraint,
        user=current_user,
        feature_model_version_repo=feature_model_version_repo,
    )
    return Message(
        message="Constraint deleted in new model version created successfully."
    )


@router.patch("/{constraint_id}/activate", response_model=ConstraintPublic)
async def activate_constraint(
    *,
    constraint_id: uuid.UUID,
    current_user: ModelDesignerUser,
    constraint_repo: AsyncConstraintRepoDep,
) -> ConstraintPublic:
    """
    Activar una constraint (is_active=true).
    """
    db_constraint = await constraint_repo.get(constraint_id=constraint_id)
    if not db_constraint:
        raise ConstraintNotFoundException(constraint_id=str(constraint_id))

    await constraint_repo.session.refresh(db_constraint, ["feature_model_version"])
    await constraint_repo.session.refresh(
        db_constraint.feature_model_version, ["feature_model"]
    )

    if (
        db_constraint.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise ConstraintAccessDeniedException(constraint_id=str(constraint_id))

    if db_constraint.is_active:
        raise HTTPException(status_code=400, detail="Constraint is already active")

    return await constraint_repo.activate(db_constraint)


@router.patch("/{constraint_id}/deactivate", response_model=ConstraintPublic)
async def deactivate_constraint(
    *,
    constraint_id: uuid.UUID,
    current_user: ModelDesignerUser,
    constraint_repo: AsyncConstraintRepoDep,
) -> ConstraintPublic:
    """
    Desactivar una constraint (is_active=false).
    """
    db_constraint = await constraint_repo.get(constraint_id=constraint_id)
    if not db_constraint:
        raise ConstraintNotFoundException(constraint_id=str(constraint_id))

    await constraint_repo.session.refresh(db_constraint, ["feature_model_version"])
    await constraint_repo.session.refresh(
        db_constraint.feature_model_version, ["feature_model"]
    )

    if (
        db_constraint.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise ConstraintAccessDeniedException(constraint_id=str(constraint_id))

    if not db_constraint.is_active:
        raise HTTPException(status_code=400, detail="Constraint is already inactive")

    return await constraint_repo.deactivate(db_constraint)
