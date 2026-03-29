import asyncio
import uuid

from app.api.deps import SessionLocal
from app.core.security import get_password_hash
from app.enums import ModelStatus, UserRole
from app.models.domain import DomainCreate
from app.models.feature_model import FeatureModelCreate
from app.models.feature_model_version import FeatureModelVersion
from app.models.user import User
from app.repositories.domain import DomainRepository
from app.repositories.feature_model import FeatureModelRepository
from app.repositories.feature_model_version import FeatureModelVersionRepository


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


def test_feature_model_version_repository_basic() -> None:
    async def _test() -> None:
        async with SessionLocal() as session:
            domain_repo = DomainRepository(session)
            feature_model_repo = FeatureModelRepository(session)
            version_repo = FeatureModelVersionRepository(session)

            user = await _create_user(session, f"owner-{uuid.uuid4()}@example.com")
            domain = await domain_repo.create(
                DomainCreate(name=f"domain-{uuid.uuid4()}", description="repo test")
            )

            model = await feature_model_repo.create(
                data=FeatureModelCreate(
                    name=f"model-{uuid.uuid4()}",
                    description="initial",
                    domain_id=domain.id,
                ),
                owner_id=user.id,
            )

            version_1 = FeatureModelVersion(
                feature_model_id=model.id,
                version_number=1,
                status=ModelStatus.DRAFT,
            )
            version_2 = FeatureModelVersion(
                feature_model_id=model.id,
                version_number=2,
                status=ModelStatus.PUBLISHED,
            )
            session.add(version_1)
            session.add(version_2)
            await session.commit()

            latest = await version_repo.get_latest_version_number(model.id)
            assert latest == 2

            stats = await version_repo.get_statistics(version_2.id)
            assert stats
            assert stats["total_features"] == 0
            assert stats["total_groups"] == 0

            await feature_model_repo.delete(model)
            await domain_repo.delete(domain)
            await _delete_user(session, user.id)

    run_async(_test())
