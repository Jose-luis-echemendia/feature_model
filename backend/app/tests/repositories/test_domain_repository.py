import asyncio
import uuid

from app.models.domain import DomainCreate, DomainUpdate
from app.repositories.domain import DomainRepository
from app.api.deps import SessionLocal


def run_async(coro):
    return asyncio.run(coro)


async def _create_domain(
    repo: DomainRepository, name: str, description: str | None = None
):
    data = DomainCreate(name=name, description=description)
    return await repo.create(data)


async def _delete_domain(repo: DomainRepository, domain_id: uuid.UUID):
    domain = await repo.get(domain_id)
    if domain:
        await repo.delete(domain)


def test_domain_repository_crud() -> None:
    async def _test() -> None:
        async with SessionLocal() as session:
            repo = DomainRepository(session)
            name = f"domain-{uuid.uuid4()}"
            description = "test domain"

            domain = await _create_domain(repo, name, description)
            assert domain.id
            assert domain.name == name
            assert domain.description == description

            fetched = await repo.get(domain.id)
            assert fetched
            assert fetched.id == domain.id

            by_name = await repo.get_by_name(name)
            assert by_name
            assert by_name.id == domain.id

            update = DomainUpdate(name=f"{name}-updated")
            updated = await repo.update(domain, update)
            assert updated.name.endswith("-updated")

            count = await repo.count()
            assert count >= 1

            results = await repo.search(search_term="domain-")
            assert any(r.id == domain.id for r in results)

            activated = await repo.activate(updated)
            assert activated.is_active is True

            deactivated = await repo.deactivate(activated)
            assert deactivated.is_active is False

            await _delete_domain(repo, domain.id)

    run_async(_test())
