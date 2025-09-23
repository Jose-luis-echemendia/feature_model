from fastapi import APIRouter, Depends, HTTPException

from app import crud
from app.api.deps import SessionDep, get_current_user
from app.models.domain import Domain, DomainPublic, DomainsPublic

router = APIRouter(prefix="/domains", tags=["domains"])


# ---------------------------------------------------------------------------
# Endpoint para leer la información de los dominios.
# ---------------------------------------------------------------------------


@router.get(
    "/",
    dependencies=[Depends(get_current_user)],
    response_model=DomainsPublic,
)
def read_domains(session: SessionDep, skip: int = 0, limit: int = 100) -> DomainsPublic:
    """Retrieve domains

    Args:
        session (SessionDep): _description_
        skip (int, optional): _description_. Defaults to 0.
        limit (int, optional): _description_. Defaults to 100.

    Returns:
        DomainsPublic: _description_
    """

    domains = crud.get_domain(session=session, skip=skip, limit=limit)
    count = crud.get_domains_count(session=session)

    return DomainsPublic(data=domains, count=count)
