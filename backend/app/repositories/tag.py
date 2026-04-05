import uuid
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.tag import Tag, TagCreate


class TagRepository:
    """Repositorio asíncrono para Tags."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, tag_id: uuid.UUID) -> Tag | None:
        stmt = select(Tag).where(Tag.id == tag_id, Tag.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Tag | None:
        stmt = select(Tag).where(Tag.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> list[Tag]:
        stmt = select(Tag).where(Tag.is_active == True).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, data: TagCreate) -> Tag:
        tag = Tag.model_validate(data)
        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag)
        return tag
