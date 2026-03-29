import asyncio
import uuid

from app.api.deps import SessionLocal
from app.core.security import get_password_hash
from app.enums import UserRole
from app.models.domain import DomainCreate
from app.models.feature_model import FeatureModelCreate, FeatureModelUpdate
from app.models.user import User
from app.repositories.domain import DomainRepository
from app.repositories.feature_model import FeatureModelRepository


def run_async(coro):
    return asyncio.run(coro)


async def _create_user(session, email: str) -> User:
    user = User(
        email=email,
        hashed_password=get_password_hash("test-password"),
        is_superuser=True,
        role=UserRole.ADMIN,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def _delete_user(session, user_id: uuid.UUID) -> None:
    user = await session.get(User, user_id)
    if user:
        await session.delete(user)
        await session.commit()


def test_feature_model_repository_crud() -> None:
    async def _test() -> None:
        async with SessionLocal() as session:
            domain_repo = DomainRepository(session)
            feature_model_repo = FeatureModelRepository(session)

            user = await _create_user(session, f"owner-{uuid.uuid4()}@example.com")
            domain = await domain_repo.create(
                DomainCreate(name=f"domain-{uuid.uuid4()}", description="repo test")
            )

            model = await feature_model_repo.create(
                FeatureModelCreate(
                    name=f"model-{uuid.uuid4()}",
                    description="initial",
                    domain_id=domain.id,
                ),
                owner_id=user.id,
            )
            assert model.id
            assert model.domain_id == domain.id
            assert model.owner_id == user.id

            fetched = await feature_model_repo.get(model.id)
            assert fetched
            assert fetched.id == model.id

            update = FeatureModelUpdate(name=f"{model.name}-updated")
            updated = await feature_model_repo.update(fetched, update)
            assert updated.name.endswith("-updated")

            count = await feature_model_repo.count()
            assert count >= 1

            by_domain = await feature_model_repo.get_by_domain(domain.id)
            assert any(m.id == model.id for m in by_domain)

            active = await feature_model_repo.activate(updated)
            assert active.is_active is True

            inactive = await feature_model_repo.deactivate(active)
            assert inactive.is_active is False

            can_delete, error_message = await feature_model_repo.can_be_deleted(
                model.id
            )
            assert can_delete is True
            assert error_message == ""

            await feature_model_repo.delete(inactive)
            await domain_repo.delete(domain)
            await _delete_user(session, user.id)

    run_async(_test())
