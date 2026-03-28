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

router = APIRouter(prefix="/feature-relations", tags=["feature-relations"])


@router.get("/", response_model=list[FeatureRelationPublic])
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
    """Listar relaciones con filtros opcionales."""
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


@router.get("/{relation_id}", response_model=FeatureRelationPublic)
async def read_feature_relation(
    *,
    relation_id: uuid.UUID,
    feature_relation_repo: AsyncFeatureRelationRepoDep,
) -> FeatureRelationPublic:
    """Obtener una relación por ID."""
    relation = await feature_relation_repo.get(relation_id=relation_id)
    if not relation:
        raise HTTPException(status_code=404, detail="Feature relation not found.")
    return relation


@router.post(
    "/", response_model=FeatureRelationPublic, status_code=status.HTTP_201_CREATED
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
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    try:
        relation = await feature_relation_repo.create(
            data=relation_in,
            user=current_user,
            feature_repo=feature_repo,
            feature_model_version_repo=feature_model_version_repo,
        )
        return relation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{relation_id}", response_model=FeatureRelationPublic)
async def update_feature_relation(
    *,
    relation_id: uuid.UUID,
    relation_in: FeatureRelationUpdate,
    current_user: ModelDesignerUser,
    feature_relation_repo: AsyncFeatureRelationRepoDep,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
) -> FeatureRelationPublic:
    """Actualizar parcialmente una relación (copy-on-write)."""
    db_relation = await feature_relation_repo.get(relation_id=relation_id)
    if not db_relation:
        raise HTTPException(status_code=404, detail="Feature relation not found.")

    await feature_relation_repo.session.refresh(db_relation, ["feature_model_version"])
    await feature_relation_repo.session.refresh(
        db_relation.feature_model_version, ["feature_model"]
    )

    if (
        db_relation.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    try:
        return await feature_relation_repo.update(
            db_relation=db_relation,
            data=relation_in,
            user=current_user,
            feature_model_version_repo=feature_model_version_repo,
        )
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{relation_id}", response_model=FeatureRelationPublic)
async def replace_feature_relation(
    *,
    relation_id: uuid.UUID,
    relation_in: FeatureRelationReplace,
    current_user: ModelDesignerUser,
    feature_relation_repo: AsyncFeatureRelationRepoDep,
    feature_model_version_repo: AsyncFeatureModelVersionRepoDep,
) -> FeatureRelationPublic:
    """Reemplazar completamente una relación (copy-on-write)."""
    db_relation = await feature_relation_repo.get(relation_id=relation_id)
    if not db_relation:
        raise HTTPException(status_code=404, detail="Feature relation not found.")

    await feature_relation_repo.session.refresh(db_relation, ["feature_model_version"])
    await feature_relation_repo.session.refresh(
        db_relation.feature_model_version, ["feature_model"]
    )

    if (
        db_relation.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions.")

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
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{relation_id}", response_model=Message)
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
        raise HTTPException(status_code=404, detail="Feature relation not found.")

    # Cargar las relaciones necesarias para la verificación de permisos
    await feature_relation_repo.session.refresh(db_relation, ["feature_model_version"])
    await feature_relation_repo.session.refresh(
        db_relation.feature_model_version, ["feature_model"]
    )

    if (
        db_relation.feature_model_version.feature_model.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    await feature_relation_repo.delete(
        db_relation=db_relation,
        user=current_user,
        feature_model_version_repo=feature_model_version_repo,
    )
    return Message(
        message="Feature relation deleted in new model version created successfully."
    )
