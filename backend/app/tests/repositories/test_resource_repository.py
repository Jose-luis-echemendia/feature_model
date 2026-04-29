import asyncio
import uuid
from unittest.mock import AsyncMock, Mock, patch

from app.repositories.resource import ResourceRepository


def run_async(coro):
    return asyncio.run(coro)


def _build_session() -> Mock:
    session = Mock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = Mock()
    return session


def test_get_returns_scalar_one_or_none() -> None:
    session = _build_session()
    expected = object()
    result = Mock()
    result.scalar_one_or_none.return_value = expected
    session.execute.return_value = result
    repo = ResourceRepository(session)

    found = run_async(repo.get(uuid.uuid4()))

    assert found is expected


def test_list_returns_scalars_all() -> None:
    session = _build_session()
    expected = [object(), object()]
    scalars_obj = Mock()
    scalars_obj.all.return_value = expected
    result = Mock()
    result.scalars.return_value = scalars_obj
    session.execute.return_value = result
    repo = ResourceRepository(session)

    items = run_async(repo.list(skip=1, limit=2))

    assert items == expected


def test_create_validates_and_persists_resource() -> None:
    session = _build_session()
    repo = ResourceRepository(session)
    data = object()
    fake_resource = object()

    with patch(
        "app.repositories.resource.Resource.model_validate",
        return_value=fake_resource,
    ):
        created = run_async(repo.create(data))

    assert created is fake_resource
    session.add.assert_called_once_with(fake_resource)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(fake_resource)


def test_update_applies_model_dump_and_persists() -> None:
    session = _build_session()
    repo = ResourceRepository(session)
    resource = Mock()
    update_data = Mock()
    update_data.model_dump.return_value = {"title": "Updated", "language": "en"}

    updated = run_async(repo.update(resource, update_data))

    assert updated is resource
    update_data.model_dump.assert_called_once_with(exclude_unset=True)
    resource.sqlmodel_update.assert_called_once_with(
        {"title": "Updated", "language": "en"}
    )
    session.add.assert_called_once_with(resource)
