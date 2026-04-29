import asyncio
import uuid
from unittest.mock import AsyncMock, Mock, patch

from app.repositories.tag import TagRepository


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
    repo = TagRepository(session)

    found = run_async(repo.get(uuid.uuid4()))

    assert found is expected


def test_get_by_name_returns_scalar_one_or_none() -> None:
    session = _build_session()
    expected = object()
    result = Mock()
    result.scalar_one_or_none.return_value = expected
    session.execute.return_value = result
    repo = TagRepository(session)

    found = run_async(repo.get_by_name("backend"))

    assert found is expected


def test_list_returns_scalars_all() -> None:
    session = _build_session()
    expected = [object(), object()]
    scalars_obj = Mock()
    scalars_obj.all.return_value = expected
    result = Mock()
    result.scalars.return_value = scalars_obj
    session.execute.return_value = result
    repo = TagRepository(session)

    items = run_async(repo.list(skip=10, limit=5))

    assert items == expected


def test_create_validates_and_persists_tag() -> None:
    session = _build_session()
    repo = TagRepository(session)
    data = object()
    fake_tag = object()

    with patch("app.repositories.tag.Tag.model_validate", return_value=fake_tag):
        created = run_async(repo.create(data))

    assert created is fake_tag
    session.add.assert_called_once_with(fake_tag)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(fake_tag)
