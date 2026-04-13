import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_cache.decorator import cache
from pydantic import BaseModel
from sqlmodel import select

from app.api.deps import (
    AsyncFeatureRepoDep,
    AsyncFeatureModelRepoDep,
    AsyncCurrentUser,
    AsyncFeatureRelationRepoDep,
    AsyncTagRepoDep,
    VerifiedUser,
)
from app.models import (
    FeatureCreate,
    FeaturePublic,
    FeatureUpdate,
    FeaturePublicWithChildren,
    FeatureRelationPublic,
    Message,
)
from app.models.tag import TagPublic
from app.enums import FeatureType
from app.models.feature_relation import FeatureRelation
from app.exceptions import (
    FeatureNotFoundException,
    FeatureAccessDeniedException,
    TagNotFoundException,
)


router = APIRouter(prefix="/features", tags=["features"])


class FeatureMove(BaseModel):
    parent_id: Optional[uuid.UUID] = None


class FeatureReplace(BaseModel):
    name: str
    type: FeatureType
    parent_id: Optional[uuid.UUID] = None
    group_id: Optional[uuid.UUID] = None


@router.get(
    "/",
    dependencies=[Depends(VerifiedUser)],
    response_model=list[FeaturePublicWithChildren],
)
@cache(expire=300)  # Cache por 5 minutos
async def read_features_by_model(
    *,
    feature_repo: AsyncFeatureRepoDep,
    feature_model_version_id: Optional[uuid.UUID] = None,
    name: Optional[str] = None,
    feature_type: Optional[FeatureType] = None,
    parent_id: Optional[uuid.UUID] = None,
    group_id: Optional[uuid.UUID] = None,
    include_inactive: bool = False,
    skip: int = 0,
    limit: int = 100,
) -> list[FeaturePublicWithChildren]:
    """
    Retrieve features with optional filters.

    Modos de uso:
    - Con feature_model_version_id: devuelve el árbol de la versión (root nodes).
    - Sin feature_model_version_id: devuelve lista plana con filtros avanzados.

    Filtros soportados:
    - name: búsqueda parcial por nombre
    - feature_type: mandatory u optional
    - parent_id: filtra por parent específico
    - group_id: filtra por grupo
    - include_inactive: incluye soft-deleted
    - skip/limit: paginación
    """
    if feature_model_version_id:
        root_features = await feature_repo.get_as_tree(
            feature_model_version_id=feature_model_version_id,
            skip=skip,
            limit=limit,
        )
        return root_features

    features = await feature_repo.get_filtered(
        feature_model_version_id=None,
        name=name,
        feature_type=feature_type.value if feature_type else None,
        parent_id=parent_id,
        group_id=group_id,
        include_inactive=include_inactive,
        skip=skip,
        limit=limit,
    )
    return [FeaturePublicWithChildren.model_validate(f) for f in features]


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
        raise FeatureAccessDeniedException()

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
    "/{feature_id}", dependencies=[Depends(VerifiedUser)], response_model=FeaturePublic
)
@cache(expire=300)  # Cache por 5 minutos
async def read_feature(
    *, feature_id: uuid.UUID, feature_repo: AsyncFeatureRepoDep
) -> FeaturePublic:
    """
    Get a specific feature by ID.
    """
    feature = await feature_repo.get(feature_id)
    if not feature:
        raise FeatureNotFoundException(feature_id=str(feature_id))
    return feature


@router.get(
    "/{feature_id}/children",
    dependencies=[Depends(VerifiedUser)],
    response_model=FeaturePublicWithChildren,
)
@cache(expire=300)
async def read_feature_children(
    *,
    feature_id: uuid.UUID,
    feature_repo: AsyncFeatureRepoDep,
) -> FeaturePublicWithChildren:
    """
    Obtiene el subárbol de una feature específica.

    Retorna el nodo con todos sus hijos recursivos.
    """
    feature = await feature_repo.get(feature_id)
    if not feature:
        raise FeatureNotFoundException(feature_id=str(feature_id))

    tree = await feature_repo.get_as_tree(
        feature_model_version_id=feature.feature_model_version_id
    )

    def find_node(
        nodes: list[FeaturePublicWithChildren],
    ) -> Optional[FeaturePublicWithChildren]:
        for node in nodes:
            if node.id == feature_id:
                return node
            found = find_node(node.children)
            if found:
                return found
        return None

    subtree = find_node(tree)
    if not subtree:
        raise FeatureNotFoundException(feature_id=str(feature_id))
    return subtree


@router.get(
    "/{feature_id}/relations",
    dependencies=[Depends(VerifiedUser)],
    response_model=list[FeatureRelationPublic],
)
@cache(expire=300)
async def read_feature_relations(
    *,
    feature_id: uuid.UUID,
    feature_relation_repo: AsyncFeatureRelationRepoDep,
) -> list[FeatureRelationPublic]:
    """
    Obtiene relaciones cross-tree donde la feature participa.

    Incluye relaciones donde la feature es source o target.
    """
    stmt = select(FeatureRelation).where(
        FeatureRelation.is_active == True,
        (FeatureRelation.source_feature_id == feature_id)
        | (FeatureRelation.target_feature_id == feature_id),
    )
    result = await feature_relation_repo.session.execute(stmt)
    return result.scalars().all()


@router.get(
    "/{feature_id}/tags",
    dependencies=[Depends(VerifiedUser)],
    response_model=list[TagPublic],
)
async def list_feature_tags(
    *,
    feature_id: uuid.UUID,
    feature_repo: AsyncFeatureRepoDep,
) -> list[TagPublic]:
    """Listar tags asociadas a una feature."""
    feature = await feature_repo.get(feature_id)
    if not feature:
        raise FeatureNotFoundException(feature_id=str(feature_id))

    await feature_repo.session.refresh(feature, ["tags"])
    return feature.tags


@router.post(
    "/{feature_id}/tags/{tag_id}",
    response_model=Message,
)
async def add_tag_to_feature(
    *,
    feature_id: uuid.UUID,
    tag_id: uuid.UUID,
    feature_repo: AsyncFeatureRepoDep,
    tag_repo: AsyncTagRepoDep,
    current_user: AsyncCurrentUser,
) -> Message:
    """Asociar una tag a una feature."""
    from app.enums import UserRole

    if current_user.role not in [
        UserRole.MODEL_DESIGNER,
        UserRole.ADMIN,
        UserRole.DEVELOPER,
    ]:
        raise FeatureAccessDeniedException()

    feature = await feature_repo.get(feature_id)
    if not feature:
        raise FeatureNotFoundException(feature_id=str(feature_id))

    tag = await tag_repo.get(tag_id)
    if not tag:
        raise TagNotFoundException(tag_id=str(tag_id))

    await feature_repo.session.refresh(feature, ["tags"])
    if tag not in feature.tags:
        feature.tags.append(tag)
        feature_repo.session.add(feature)
        await feature_repo.session.commit()

    return Message(message="Tag associated with feature")


@router.delete(
    "/{feature_id}/tags/{tag_id}",
    response_model=Message,
)
async def remove_tag_from_feature(
    *,
    feature_id: uuid.UUID,
    tag_id: uuid.UUID,
    feature_repo: AsyncFeatureRepoDep,
    tag_repo: AsyncTagRepoDep,
    current_user: AsyncCurrentUser,
) -> Message:
    """Desasociar una tag de una feature."""
    from app.enums import UserRole

    if current_user.role not in [
        UserRole.MODEL_DESIGNER,
        UserRole.ADMIN,
        UserRole.DEVELOPER,
    ]:
        raise FeatureAccessDeniedException()

    feature = await feature_repo.get(feature_id)
    if not feature:
        raise FeatureNotFoundException(feature_id=str(feature_id))

    tag = await tag_repo.get(tag_id)
    if not tag:
        raise TagNotFoundException(tag_id=str(tag_id))

    await feature_repo.session.refresh(feature, ["tags"])
    if tag in feature.tags:
        feature.tags.remove(tag)
        feature_repo.session.add(feature)
        await feature_repo.session.commit()

    return Message(message="Tag removed from feature")


@router.patch("/{feature_id}", response_model=FeaturePublic)
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
        raise FeatureAccessDeniedException(feature_id=str(feature_id))

    db_feature = await feature_repo.get(feature_id)
    if not db_feature:
        raise FeatureNotFoundException(feature_id=str(feature_id))

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


@router.put("/{feature_id}", response_model=FeaturePublic)
async def replace_feature(
    *,
    feature_id: uuid.UUID,
    feature_repo: AsyncFeatureRepoDep,
    feature_in: FeatureReplace,
    current_user: AsyncCurrentUser,
) -> FeaturePublic:
    """
    Reemplaza completamente una feature (campos principales).

    Equivale a un update full: name, type, parent_id, group_id.
    """
    from app.enums import UserRole

    if current_user.role not in [
        UserRole.MODEL_DESIGNER,
        UserRole.ADMIN,
        UserRole.DEVELOPER,
    ]:
        raise FeatureAccessDeniedException(feature_id=str(feature_id))

    db_feature = await feature_repo.get(feature_id)
    if not db_feature:
        raise FeatureNotFoundException(feature_id=str(feature_id))

    if feature_in.parent_id:
        parent_feature = await feature_repo.get(feature_in.parent_id)
        if (
            not parent_feature
            or parent_feature.feature_model_version_id
            != db_feature.feature_model_version_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Parent feature not found or does not belong to the same model.",
            )

    update_data = FeatureUpdate(
        name=feature_in.name,
        type=feature_in.type,
        parent_id=feature_in.parent_id,
        group_id=feature_in.group_id,
    )

    try:
        new_feature = await feature_repo.update(
            db_feature=db_feature,
            data=update_data,
            user=current_user,
        )
        return new_feature
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{feature_id}/move", response_model=FeaturePublic)
async def move_feature(
    *,
    feature_id: uuid.UUID,
    payload: FeatureMove,
    feature_repo: AsyncFeatureRepoDep,
    current_user: AsyncCurrentUser,
) -> FeaturePublic:
    """
    Reparenting explícito de una feature.

    Cambia únicamente el parent_id.
    """
    from app.enums import UserRole

    if current_user.role not in [
        UserRole.MODEL_DESIGNER,
        UserRole.ADMIN,
        UserRole.DEVELOPER,
    ]:
        raise FeatureAccessDeniedException(feature_id=str(feature_id))

    db_feature = await feature_repo.get(feature_id)
    if not db_feature:
        raise FeatureNotFoundException(feature_id=str(feature_id))

    if payload.parent_id:
        parent_feature = await feature_repo.get(payload.parent_id)
        if (
            not parent_feature
            or parent_feature.feature_model_version_id
            != db_feature.feature_model_version_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Parent feature not found or does not belong to the same model.",
            )

    try:
        new_feature = await feature_repo.update(
            db_feature=db_feature,
            data=FeatureUpdate(parent_id=payload.parent_id),
            user=current_user,
        )
        return new_feature
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{feature_id}/activate", response_model=FeaturePublic)
async def activate_feature(
    *,
    feature_id: uuid.UUID,
    feature_repo: AsyncFeatureRepoDep,
    current_user: AsyncCurrentUser,
) -> FeaturePublic:
    """
    Activar una feature (is_active=true).
    """
    from app.enums import UserRole

    if current_user.role not in [
        UserRole.MODEL_DESIGNER,
        UserRole.ADMIN,
        UserRole.DEVELOPER,
    ]:
        raise FeatureAccessDeniedException(feature_id=str(feature_id))

    db_feature = await feature_repo.get_any(feature_id)
    if not db_feature:
        raise FeatureNotFoundException(feature_id=str(feature_id))

    if db_feature.is_active:
        raise HTTPException(status_code=400, detail="Feature is already active")

    return await feature_repo.activate(db_feature)


@router.patch("/{feature_id}/deactivate", response_model=FeaturePublic)
async def deactivate_feature(
    *,
    feature_id: uuid.UUID,
    feature_repo: AsyncFeatureRepoDep,
    current_user: AsyncCurrentUser,
) -> FeaturePublic:
    """
    Desactivar una feature (is_active=false).
    """
    from app.enums import UserRole

    if current_user.role not in [
        UserRole.MODEL_DESIGNER,
        UserRole.ADMIN,
        UserRole.DEVELOPER,
    ]:
        raise FeatureAccessDeniedException(feature_id=str(feature_id))

    db_feature = await feature_repo.get_any(feature_id)
    if not db_feature:
        raise FeatureNotFoundException(feature_id=str(feature_id))

    if not db_feature.is_active:
        raise HTTPException(status_code=400, detail="Feature is already inactive")

    return await feature_repo.deactivate(db_feature)


@router.delete("/{feature_id}", response_model=Message)
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
        raise FeatureAccessDeniedException(feature_id=str(feature_id))

    db_feature = await feature_repo.get(feature_id)
    if not db_feature:
        raise FeatureNotFoundException(feature_id=str(feature_id))

    await feature_repo.delete(db_feature=db_feature, user=current_user)
    return Message(message="Feature deleted in new model version created successfully.")
