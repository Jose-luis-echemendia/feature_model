import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache

from app.api.deps import (
    AsyncDomainRepoDep,
    get_verified_user,
    get_admin_user,
    AsyncCurrentUser,
)
from app.models.common import Message
from app.models.domain import (
    DomainPublic,
    DomainListResponse,
    DomainCreate,
    DomainUpdate,
    DomainPublicWithFeatureModels,
)
from app.enums import UserRole

router = APIRouter(
    prefix="/domains",
    tags=["Domains"],
    responses={
        404: {"description": "Domain not found"},
        403: {"description": "Not enough permissions (Admin only)"},
        400: {"description": "Validation error or domain has dependencies"},
    },
)


# ======================================================================================
#       --- Endpoint para leer (listar) la información de los dominios. ---
# ======================================================================================


@router.get(
    "/",
    dependencies=[Depends(get_verified_user)],
    response_model=DomainListResponse,
)
@cache(expire=300)  # Cache por 5 minutos
async def read_domains(
    current_user: AsyncCurrentUser,
    domain_repo: AsyncDomainRepoDep,
    skip: int = 0,
    limit: int = 100,
) -> DomainListResponse:
    """
    Read domains (solo accesible para administradores).

    Args:
        current_user: Usuario autenticado actual
        domain_repo: Repositorio de dominios
        skip: Número de registros a saltar
        limit: Número máximo de registros a retornar

    Returns:
        DomainListResponse: Lista de dominios con conteo total

    Note:
        - Admins y Developers pueden ver todos los dominios (activos e inactivos)
        - Otros roles solo ven dominios activos (is_active = True)
    """
    # Determinar si se deben incluir dominios inactivos
    include_inactive = current_user.role in [UserRole.ADMIN, UserRole.DEVELOPER]

    domains = await domain_repo.get_all(
        skip=skip, limit=limit, include_inactive=include_inactive
    )
    count = await domain_repo.count(include_inactive=include_inactive)

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
@cache(expire=300)  # Cache por 5 minutos
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
    Permanently delete a domain.

    This endpoint performs a hard delete of a domain from the database.
    **Important:** Deletion is only allowed if the domain has NO associated
    feature models. If you want to preserve the domain but mark it as unused,
    use the deactivate endpoint instead.

    Permissions Required:
        - ADMIN: Only administrators can delete domains

    Validation Rules:
        - The domain must have no associated feature models
        - All feature models must be deleted before the domain can be deleted

    Args:
        domain_id: UUID of the domain to delete
        domain_repo: Domain repository dependency

    Returns:
        Message: Success confirmation message

    Raises:
        HTTPException 403: If user is not an administrator
        HTTPException 404: If domain doesn't exist
        HTTPException 400: If domain has associated feature models

    Warning:
        This operation is irreversible. Consider using deactivate instead
        if you want to preserve the domain for future reference.

    Example:
        DELETE /domains/123e4567-e89b-12d3-a456-426614174000/

    Response Example:
        {
            "message": "Domain deleted successfully"
        }
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
    "/search/",
    dependencies=[Depends(get_verified_user)],
    response_model=DomainListResponse,
)
@cache(expire=300)  # Cache por 5 minutos
async def search_domains(
    *,
    current_user: AsyncCurrentUser,
    domain_repo: AsyncDomainRepoDep,
    search_term: str,
    skip: int = 0,
    limit: int = 100,
) -> DomainListResponse:
    """
    Search domains by name or description.

    Only accessible to administrators.

    Args:
        current_user: Usuario autenticado actual
        domain_repo: Repositorio de dominios
        search_term: Term to search for
        skip: Pagination offset
        limit: Pagination limit

    Returns:
        DomainListResponse: Search results

    Note:
        - Admins y Developers pueden ver todos los dominios (activos e inactivos)
        - Otros roles solo ven dominios activos (is_active = True)
    """
    # Determinar si se deben incluir dominios inactivos
    include_inactive = current_user.role in [UserRole.ADMIN, UserRole.DEVELOPER]

    domains = await domain_repo.search(
        search_term, skip=skip, limit=limit, include_inactive=include_inactive
    )
    count = await domain_repo.count_search(
        search_term, include_inactive=include_inactive
    )

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
    response_model=DomainPublicWithFeatureModels,
)
@cache(expire=300)  # Cache por 5 minutos
async def read_domain_with_feature_models(
    *,
    domain_id: uuid.UUID,
    domain_repo: AsyncDomainRepoDep,
) -> DomainPublicWithFeatureModels:
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
    Activate a domain.

    This endpoint sets the `is_active` flag to `true`, making the domain
    active and visible to all users. All feature models within this domain
    will become accessible again.

    Permissions Required:
        - ADMIN: Only administrators can activate domains

    Args:
        domain_id: UUID of the domain to activate
        domain_repo: Domain repository dependency

    Returns:
        DomainPublic: Activated domain with is_active=true

    Raises:
        HTTPException 403: If user is not an administrator
        HTTPException 404: If domain doesn't exist

    Note:
        Activating a domain makes it visible to all users and allows
        creation of new feature models within this domain.

    Example:
        PATCH /domains/123e4567-e89b-12d3-a456-426614174000/activate/
    """
    domain = await domain_repo.get(domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    return await domain_repo.activate(domain)


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
    Deactivate a domain.

    This endpoint sets the `is_active` flag to `false`, making the domain
    inactive. Deactivated domains are hidden from regular users but preserved
    in the database. This is a soft-delete operation that allows reactivation.

    Permissions Required:
        - ADMIN: Only administrators can deactivate domains

    Args:
        domain_id: UUID of the domain to deactivate
        domain_repo: Domain repository dependency

    Returns:
        DomainPublic: Deactivated domain with is_active=false

    Raises:
        HTTPException 403: If user is not an administrator
        HTTPException 404: If domain doesn't exist

    Note:
        - Deactivated domains are only visible to ADMIN and DEVELOPER roles
        - Feature models within the domain remain accessible
        - The domain can be reactivated using the activate endpoint
        - This operation does not delete any associated feature models

    Warning:
        Deactivating a domain may affect active feature models and their
        associated workflows. Consider the impact before deactivating.

    Example:
        PATCH /domains/123e4567-e89b-12d3-a456-426614174000/deactivate/
    """
    domain = await domain_repo.get(domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    return await domain_repo.deactivate(domain)
