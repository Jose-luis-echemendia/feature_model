import asyncio
import uuid
from unittest.mock import AsyncMock, Mock

from app.repositories.feature import FeatureRepository


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
    repo = FeatureRepository(session)

    found = run_async(repo.get(uuid.uuid4()))
    assert found is expected


def test_exists_returns_boolean() -> None:
    session = _build_session()
    repo = FeatureRepository(session)
    repo.get = AsyncMock(side_effect=[object(), None])  # type: ignore[method-assign]

    assert run_async(repo.exists(uuid.uuid4())) is True
    assert run_async(repo.exists(uuid.uuid4())) is False


def test_activate_and_deactivate_toggle_flag() -> None:
    session = _build_session()
    repo = FeatureRepository(session)
    feature = Mock(is_active=False)

    activated = run_async(repo.activate(feature))
    assert activated is feature
    assert feature.is_active is True

    deactivated = run_async(repo.deactivate(feature))
    assert deactivated is feature
    assert feature.is_active is False
