import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import AsyncDomainRepoDep, get_verified_user, get_admin_user
from app.models.common import Message
from app.models.domain import (
    DomainPublic,
    DomainListResponse,
    DomainCreate,
    DomainUpdate,
)

router = APIRouter(prefix="/domains", tags=["domains"])


# ======================================================================================
#       --- Endpoint para leer (listar) la información de los dominios. ---
# ======================================================================================


@router.get(
    "/",
    dependencies=[Depends(get_verified_user)],
    response_model=DomainListResponse,
)
async def read_domains(
    domain_repo: AsyncDomainRepoDep,
    skip: int = 0,
    limit: int = 100,
) -> DomainListResponse:
    """
    Read domains (solo accesible para administradores).

    Args:
        domain_repo: Repositorio de dominios
        skip: Número de registros a saltar
        limit: Número máximo de registros a retornar

    Returns:
        DomainListResponse: Lista de dominios con conteo total
    """
    domains = await domain_repo.get_all(skip=skip, limit=limit)
    count = await domain_repo.count()

    return DomainListResponse.create(
        data=domains,
        count=count,
        skip=skip,
        limit=limit,
    )


# ---------------------------------------------------------------------------
# Endpoint para obtener un dominio por ID (solo admin)
# ---------------------------------------------------------------------------
@router.get(
    "/{domain_id}/",
    dependencies=[Depends(get_verified_user)],
    response_model=DomainPublic,
)
async def read_domain(
    *,
    domain_id: uuid.UUID,
    domain_repo: AsyncDomainRepoDep,
) -> DomainPublic:
    """
    Get a specific domain by ID.

    Only accessible to administrators.

    Args:
        domain_id: Domain ID
        domain_repo: Repositorio de dominios

    Returns:
        DomainPublic: Domain data

    Raises:
        HTTPException: If domain not found
    """
    domain = await domain_repo.get(domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return DomainPublic.model_validate(domain)


# ---------------------------------------------------------------------------
# Endpoint para crear un nuevo dominio (solo admin)
# ---------------------------------------------------------------------------
@router.post("/", dependencies=[Depends(get_admin_user)], response_model=DomainPublic)
async def create_domain(
    *,
    domain_repo: AsyncDomainRepoDep,
    domain_in: DomainCreate,
) -> DomainPublic:
    """
    Create new domain.

    Only administrators can create new domains.

    Args:
        domain_repo: Repositorio de dominios
        domain_in: Domain creation data

    Returns:
        DomainPublic: Created domain

    Raises:
        HTTPException: If domain with same name already exists
    """
    try:
        domain = await domain_repo.create(domain_in)
        return DomainPublic.model_validate(domain)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# Endpoint para actualizar un dominio (solo admin)
# ---------------------------------------------------------------------------


@router.patch(
    "/{domain_id}/", dependencies=[Depends(get_admin_user)], response_model=DomainPublic
)
async def update_domain(
    *,
    domain_id: uuid.UUID,
    domain_repo: AsyncDomainRepoDep,
    domain_in: DomainUpdate,
) -> DomainPublic:
    """
    Update a domain.

    Only administrators can update domains.

    Args:
        domain_id: Domain ID to update
        domain_repo: Repositorio de dominios
        domain_in: Domain update data

    Returns:
        DomainPublic: Updated domain

    Raises:
        HTTPException: If domain not found or validation error
    """
    # Primero verificar que el dominio existe
    db_domain = await domain_repo.get(domain_id)
    if not db_domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    try:
        updated_domain = await domain_repo.update(db_domain, domain_in)
        return DomainPublic.model_validate(updated_domain)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# Endpoint para eliminar un dominio (solo admin)
# ---------------------------------------------------------------------------
@router.delete(
    "/{domain_id}/", dependencies=[Depends(get_admin_user)], response_model=Message
)
async def delete_domain(
    *,
    domain_id: uuid.UUID,
    domain_repo: AsyncDomainRepoDep,
) -> Message:
    """
    Delete a domain.

    Only administrators can delete domains.

    Args:
        domain_id: Domain ID to delete
        domain_repo: Repositorio de dominios

    Returns:
        Message: Success message

    Raises:
        HTTPException: If domain not found
    """
    domain = await domain_repo.get(domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    # Verificar si el dominio tiene feature models asociados
    if hasattr(domain, "feature_models") and domain.feature_models:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete domain with associated feature models. Delete the feature models first.",
        )

    await domain_repo.delete(domain)
    return Message(message="Domain deleted successfully")


# ---------------------------------------------------------------------------
# Endpoint para buscar dominios por nombre (solo admin)
# ---------------------------------------------------------------------------
@router.get(
    "/search/{search_term}/",
    dependencies=[Depends(get_admin_user)],
    response_model=DomainListResponse,
)
async def search_domains(
    *,
    domain_repo: AsyncDomainRepoDep,
    search_term: str,
    skip: int = 0,
    limit: int = 100,
) -> DomainListResponse:
    """
    Search domains by name or description.

    Only accessible to administrators.

    Args:
        domain_repo: Repositorio de dominios
        search_term: Term to search for
        skip: Pagination offset
        limit: Pagination limit

    Returns:
        DomainListResponse: Search results
    """
    domains = await domain_repo.search(search_term, skip=skip, limit=limit)
    count = await domain_repo.count_search(search_term)

    return DomainListResponse.create(
        data=domains,
        count=count,
        skip=skip,
        limit=limit,
    )


# ---------------------------------------------------------------------------
# Endpoint para obtener dominio con sus feature models (solo admin)
# ---------------------------------------------------------------------------
@router.get(
    "/{domain_id}/with-feature-models/",
    dependencies=[Depends(get_admin_user)],
    response_model=DomainPublic,
)
async def read_domain_with_feature_models(
    *,
    domain_id: uuid.UUID,
    domain_repo: AsyncDomainRepoDep,
) -> DomainPublic:
    """
    Get a domain with its associated feature models.

    Only accessible to administrators.

    Args:
        domain_id: Domain ID
        domain_repo: Repositorio de dominios

    Returns:
        DomainPublic: Domain with feature models

    Raises:
        HTTPException: If domain not found
    """
    domain = await domain_repo.get_with_feature_models(domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return domain


# ======================================================================================
#       --- Endpoint para activar un dominio. ---
# ======================================================================================


@router.patch(
    "/{domain_id}/activate/",
    dependencies=[Depends(get_admin_user)],
    response_model=DomainPublic,
)
async def activate_domain(
    *,
    domain_id: uuid.UUID,
    domain_repo: AsyncDomainRepoDep,
) -> DomainPublic:
    """
    Activar un dominio (solo accesible para administradores).

    Args:
        domain_id: ID del dominio a activar
        domain_repo: Repositorio de dominios

    Returns:
        DomainPublic: Dominio activado

    Raises:
        HTTPException: Si el dominio no existe
    """
    domain = await domain_repo.get(domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    # Activar el dominio
    activated_domain = await domain_repo.activate(domain)
    return activated_domain


# ======================================================================================
#       --- Endpoint para desactivar un dominio. ---
# ======================================================================================


@router.patch(
    "/{domain_id}/deactivate/",
    dependencies=[Depends(get_admin_user)],
    response_model=DomainPublic,
)
async def deactivate_domain(
    *,
    domain_id: uuid.UUID,
    domain_repo: AsyncDomainRepoDep,
) -> DomainPublic:
    """
    Desactivar un dominio (solo accesible para administradores).

    Args:
        domain_id: ID del dominio a desactivar
        domain_repo: Repositorio de dominios

    Returns:
        DomainPublic: Dominio desactivado

    Raises:
        HTTPException: Si el dominio no existe
    """
    domain = await domain_repo.get(domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    # Desactivar el dominio
    deactivated_domain = await domain_repo.deactivate(domain)
    return deactivated_domain
