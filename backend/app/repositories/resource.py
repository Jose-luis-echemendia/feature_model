import uuid
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.resource import Resource, ResourceCreate, ResourceUpdate


class ResourceRepository:
    """Repositorio asíncrono para Resources."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, resource_id: uuid.UUID) -> Resource | None:
        stmt = select(Resource).where(
            Resource.id == resource_id, Resource.is_active == True
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> list[Resource]:
        stmt = (
            select(Resource).where(Resource.is_active == True).offset(skip).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, data: ResourceCreate) -> Resource:
        resource = Resource.model_validate(data)
        self.session.add(resource)
        await self.session.commit()
        await self.session.refresh(resource)
        return resource

    async def update(self, resource: Resource, data: ResourceUpdate) -> Resource:
        update_data = data.model_dump(exclude_unset=True)
        resource.sqlmodel_update(update_data)
        self.session.add(resource)
        await self.session.commit()
        await self.session.refresh(resource)
        return resource
