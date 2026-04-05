import uuid
from fastapi import APIRouter, Depends

from app.api.deps import AsyncResourceRepoDep, ModelDesignerUser, VerifiedUser
from app.models.resource import ResourceCreate, ResourcePublic, ResourceUpdate
from app.exceptions import (
    ResourceNotFoundException,
    ResourceAccessDeniedException,
    InvalidResourceOperationException,
)


router = APIRouter(prefix="/resources", tags=["resources"])


@router.get(
    "/", dependencies=[Depends(VerifiedUser)], response_model=list[ResourcePublic]
)
async def list_resources(
    *,
    resource_repo: AsyncResourceRepoDep,
    skip: int = 0,
    limit: int = 100,
) -> list[ResourcePublic]:
    """Listar recursos activos con paginación básica."""
    return await resource_repo.list(skip=skip, limit=limit)


@router.get(
    "/{resource_id}",
    dependencies=[Depends(VerifiedUser)],
    response_model=ResourcePublic,
)
async def read_resource(
    *,
    resource_id: uuid.UUID,
    resource_repo: AsyncResourceRepoDep,
) -> ResourcePublic:
    """Obtener un recurso por ID."""
    resource = await resource_repo.get(resource_id=resource_id)
    if not resource:
        raise ResourceNotFoundException(resource_id=str(resource_id))
    return resource


@router.post("/", response_model=ResourcePublic)
async def create_resource(
    *,
    resource_in: ResourceCreate,
    resource_repo: AsyncResourceRepoDep,
    current_user: ModelDesignerUser,
) -> ResourcePublic:
    """Crear un recurso. Si no se especifica owner_id, se usa el usuario actual."""
    payload = resource_in
    if payload.owner_id is None:
        payload = ResourceCreate(**resource_in.model_dump(), owner_id=current_user.id)

    return await resource_repo.create(data=payload)


@router.patch("/{resource_id}", response_model=ResourcePublic)
async def update_resource(
    *,
    resource_id: uuid.UUID,
    resource_in: ResourceUpdate,
    resource_repo: AsyncResourceRepoDep,
    current_user: ModelDesignerUser,
) -> ResourcePublic:
    """Actualizar un recurso existente."""
    resource = await resource_repo.get(resource_id=resource_id)
    if not resource:
        raise ResourceNotFoundException(resource_id=str(resource_id))

    if resource.owner_id and not current_user.is_superuser:
        if resource.owner_id != current_user.id:
            raise ResourceAccessDeniedException(resource_id=str(resource_id))

    if resource_in.owner_id and not current_user.is_superuser:
        raise InvalidResourceOperationException(
            reason="Only superusers can change owner_id"
        )

    return await resource_repo.update(resource=resource, data=resource_in)
