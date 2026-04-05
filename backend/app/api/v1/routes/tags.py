import uuid
from fastapi import APIRouter, Depends

from app.api.deps import AsyncTagRepoDep, ModelDesignerUser, VerifiedUser
from app.models.tag import TagCreate, TagPublic
from app.exceptions import TagNotFoundException, TagAlreadyExistsException


router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", dependencies=[Depends(VerifiedUser)], response_model=list[TagPublic])
async def list_tags(
    *,
    tag_repo: AsyncTagRepoDep,
    skip: int = 0,
    limit: int = 100,
) -> list[TagPublic]:
    """Listar tags activas con paginación básica."""
    return await tag_repo.list(skip=skip, limit=limit)


@router.get("/{tag_id}", dependencies=[Depends(VerifiedUser)], response_model=TagPublic)
async def read_tag(*, tag_id: uuid.UUID, tag_repo: AsyncTagRepoDep) -> TagPublic:
    """Obtener una tag por ID."""
    tag = await tag_repo.get(tag_id=tag_id)
    if not tag:
        raise TagNotFoundException(tag_id=str(tag_id))
    return tag


@router.post("/", response_model=TagPublic)
async def create_tag(
    *,
    tag_in: TagCreate,
    tag_repo: AsyncTagRepoDep,
    current_user: ModelDesignerUser,
) -> TagPublic:
    """Crear una nueva tag (nombre único)."""
    existing = await tag_repo.get_by_name(tag_in.name)
    if existing:
        raise TagAlreadyExistsException(tag_name=tag_in.name)

    return await tag_repo.create(data=tag_in)
