import uuid

from fastapi import APIRouter, Depends, HTTPException

from app import crud
from app.models.common import Message
from app.api.deps import SessionDep, get_current_user, AdminUser
from app.models.domain import (
    DomainPublic,
    DomainListResponse,
    DomainCreate,
    DomainUpdate,
)

router = APIRouter(prefix="/domains", tags=["domains"])


# ---------------------------------------------------------------------------
# Endpoint para leer (listar) la información de los dominios. (accesible para todos los roles)
# ---------------------------------------------------------------------------


@router.get(
    "/",
    dependencies=[Depends(get_current_user)],
    response_model=DomainListResponse,
)
def read_domains(
    session: SessionDep, skip: int = 0, limit: int = 100
) -> DomainListResponse:
    """Retrieve domains

    Args:
        session (SessionDep): _description_
        skip (int, optional): _description_. Defaults to 0.
        limit (int, optional): _description_. Defaults to 100.

    Returns:
        DomainListResponse: _description_
    """

    domains = crud.get_domains(session=session, skip=skip, limit=limit)
    count = crud.get_domains_count(session=session)

    return DomainListResponse(data=domains, count=count)


# ---------------------------------------------------------------------------
# Endpoint para obtener un dominio por ID (accesible para varios roles)
# ---------------------------------------------------------------------------
@router.get("/{domain_id}/", response_model=DomainPublic)
def read_domain(*, domain_id: uuid.UUID, session: SessionDep) -> DomainPublic:
    """
    Get a specific domain by ID.

    Accessible to authenticated users with appropriate roles.

    Args:
        domain_id: Domain ID
        session: Database session

    Returns:
        DomainPublic: Domain data

    Raises:
        HTTPException: If domain not found
    """
    domain = crud.get_domain(session=session, domain_id=domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return DomainPublic.model_validate(domain)


# ---------------------------------------------------------------------------
# Endpoint para crear un nuevo dominio (solo admin)
# ---------------------------------------------------------------------------
@router.post("/", dependencies=[Depends(AdminUser)], response_model=DomainPublic)
def create_domain(
    *,
    session: SessionDep,
    domain_in: DomainCreate,
) -> DomainPublic:
    """
    Create new domain.

    Only administrators can create new domains.

    Args:
        session: Database session
        domain_in: Domain creation data
        admin: Authenticated admin user

    Returns:
        DomainPublic: Created domain

    Raises:
        HTTPException: If domain with same name already exists
    """
    try:
        domain = crud.create_domain(session=session, domain_create=domain_in)
        return DomainPublic.model_validate(domain)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# Endpoint para actualizar un dominio (solo admin)
# ---------------------------------------------------------------------------


@router.patch("/{domain_id}/", response_model=DomainPublic)
def update_domain(
    *,
    domain_id: uuid.UUID,
    session: SessionDep,
    domain_in: DomainUpdate,
    admin: AdminUser,  # ← Solo admin puede actualizar
) -> DomainPublic:
    """
    Update a domain.

    Only administrators can update domains.

    Args:
        domain_id: Domain ID to update
        session: Database session
        domain_in: Domain update data
        admin: Authenticated admin user

    Returns:
        DomainPublic: Updated domain

    Raises:
        HTTPException: If domain not found or validation error
    """
    # Primero verificar que el dominio existe
    db_domain = crud.get_domain(session=session, domain_id=domain_id)
    if not db_domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    try:
        updated_domain = crud.update_domain(
            session=session, db_domain=db_domain, domain_in=domain_in
        )
        return DomainPublic.model_validate(updated_domain)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# Endpoint para eliminar un dominio (solo admin)
# ---------------------------------------------------------------------------
@router.delete(
    "/{domain_id}/", dependencies=[Depends(AdminUser)], response_model=Message
)
def delete_domain(
    *,
    domain_id: uuid.UUID,
    session: SessionDep,
) -> Message:
    """
    Delete a domain.

    Only administrators can delete domains.

    Args:
        domain_id: Domain ID to delete
        session: Database session
        admin: Authenticated admin user

    Returns:
        Message: Success message

    Raises:
        HTTPException: If domain not found
    """
    domain = crud.get_domain(session=session, domain_id=domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    # Verificar si el dominio tiene feature models asociados
    if hasattr(domain, "feature_models") and domain.feature_models:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete domain with associated feature models. Delete the feature models first.",
        )

    crud.delete_domain(session=session, db_domain=domain)
    return Message(message="Domain deleted successfully")


# ---------------------------------------------------------------------------
# Endpoint para buscar dominios por nombre (accesible para varios roles)
# ---------------------------------------------------------------------------
@router.get("/search/{search_term}/", response_model=DomainListResponse)
def search_domains(
    *, session: SessionDep, search_term: str, skip: int = 0, limit: int = 100
) -> DomainListResponse:
    """
    Search domains by name or description.

    Accessible to authenticated users with appropriate roles.

    Args:
        session: Database session
        search_term: Term to search for
        skip: Pagination offset
        limit: Pagination limit

    Returns:
        DomainListResponse: Search results
    """
    domains = crud.search_domains(
        session=session, search_term=search_term, skip=skip, limit=limit
    )
    count = len(domains)

    return DomainListResponse(data=domains, count=count)


# ---------------------------------------------------------------------------
# Endpoint para obtener dominio con sus feature models (accesible para varios roles)
# ---------------------------------------------------------------------------
@router.get("/{domain_id}/with-feature-models/", response_model=DomainPublic)
def read_domain_with_feature_models(
    *, domain_id: uuid.UUID, session: SessionDep
) -> DomainPublic:
    """
    Get a domain with its associated feature models.

    Accessible to authenticated users with appropriate roles.

    Args:
        domain_id: Domain ID
        session: Database session

    Returns:
        DomainPublic: Domain with feature models

    Raises:
        HTTPException: If domain not found
    """
    domain = crud.get_domain_with_feature_models(session=session, domain_id=domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return domain
