import asyncio
import uuid

from app.api.deps import SessionLocal
from app.core.security import get_password_hash
from app.enums import ModelStatus, UserRole
from app.models.configuration import (
    Configuration,
    ConfigurationCreate,
    ConfigurationUpdate,
)
from app.models.domain import Domain
from app.models.feature_model import FeatureModel
from app.models.feature_model_version import FeatureModelVersion
from app.models.user import User
from app.repositories.configuration import ConfigurationRepository


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


async def _cleanup(session, configuration_id, version_id, model_id, domain_id, user_id):
    configuration = await session.get(Configuration, configuration_id)
    if configuration:
        await session.delete(configuration)
        await session.commit()

    version = await session.get(FeatureModelVersion, version_id)
    if version:
        await session.delete(version)
        await session.commit()

    model = await session.get(FeatureModel, model_id)
    if model:
        await session.delete(model)
        await session.commit()

    domain = await session.get(Domain, domain_id)
    if domain:
        await session.delete(domain)
        await session.commit()

    user = await session.get(User, user_id)
    if user:
        await session.delete(user)
        await session.commit()


def test_configuration_repository_crud() -> None:
    async def _test() -> None:
        async with SessionLocal() as session:
            repo = ConfigurationRepository(session)

            user = await _create_user(session, f"owner-{uuid.uuid4()}@example.com")
            domain = Domain(name=f"domain-{uuid.uuid4()}", description="repo test")
            session.add(domain)
            await session.commit()
            await session.refresh(domain)

            model = FeatureModel(
                name=f"model-{uuid.uuid4()}",
                description="initial",
                domain_id=domain.id,
                owner_id=user.id,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)

            version = FeatureModelVersion(
                feature_model_id=model.id,
                version_number=1,
                status=ModelStatus.DRAFT,
            )
            session.add(version)
            await session.commit()
            await session.refresh(version)

            created = await repo.create(
                ConfigurationCreate(
                    name=f"config-{uuid.uuid4()}",
                    description="test config",
                    feature_model_version_id=version.id,
                    feature_ids=[],
                )
            )
            assert created.id

            fetched = await repo.get(created.id)
            assert fetched
            assert fetched.id == created.id

            updated = await repo.update(
                fetched, ConfigurationUpdate(name="updated-name")
            )
            assert updated.name == "updated-name"

            count = await repo.count()
            assert count >= 1

            await repo.delete(updated)

            await _cleanup(
                session,
                configuration_id=created.id,
                version_id=version.id,
                model_id=model.id,
                domain_id=domain.id,
                user_id=user.id,
            )

    run_async(_test())
