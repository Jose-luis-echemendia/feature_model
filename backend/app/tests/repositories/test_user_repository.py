import asyncio
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.repositories import user as user_module
from app.repositories.user import UserRepository


def run_async(coro):
    return asyncio.run(coro)


def _build_session() -> Mock:
    session = Mock()
    session.add = Mock()
    session.get = AsyncMock()
    session.exec = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    return session


def test_create_persists_user_with_hashed_password() -> None:
    session = _build_session()
    repo = UserRepository(session)
    repo.get_by_email = AsyncMock(return_value=None)  # type: ignore[method-assign]
    repo.prepare_password = Mock(return_value="hashed-pw")  # type: ignore[method-assign]
    data = SimpleNamespace(email="user@example.com", password="plain-pw")

    created = run_async(repo.create(data))

    assert created.email == "user@example.com"
    assert created.hashed_password == "hashed-pw"
    repo.get_by_email.assert_awaited_once_with("user@example.com")
    repo.prepare_password.assert_called_once_with("plain-pw")
    session.add.assert_called_once_with(created)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(created)


def test_create_raises_when_email_exists() -> None:
    session = _build_session()
    repo = UserRepository(session)
    repo.get_by_email = AsyncMock(return_value=object())  # type: ignore[method-assign]
    data = SimpleNamespace(email="user@example.com", password="plain-pw")

    with pytest.raises(ValueError):
        run_async(repo.create(data))

    repo.get_by_email.assert_awaited_once_with("user@example.com")
    session.add.assert_not_called()


def test_update_without_password_uses_model_dump_data() -> None:
    session = _build_session()
    repo = UserRepository(session)
    db_user = Mock()
    data = Mock()
    data.model_dump.return_value = {"email": "updated@example.com"}

    updated = run_async(repo.update(db_user, data))

    assert updated is db_user
    data.model_dump.assert_called_once_with(exclude_unset=True)
    db_user.sqlmodel_update.assert_called_once_with({"email": "updated@example.com"})
    session.add.assert_called_once_with(db_user)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(db_user)


def test_update_with_password_hashes_new_password() -> None:
    session = _build_session()
    repo = UserRepository(session)
    db_user = Mock()
    data = Mock()
    data.model_dump.return_value = {
        "email": "updated@example.com",
        "password": "new-password",
    }
    repo.prepare_password = Mock(return_value="hashed-new-password")  # type: ignore[method-assign]

    updated = run_async(repo.update(db_user, data))

    assert updated is db_user
    repo.prepare_password.assert_called_once_with("new-password")
    db_user.sqlmodel_update.assert_called_once_with(
        {"email": "updated@example.com", "hashed_password": "hashed-new-password"}
    )


def test_delete_removes_and_commits() -> None:
    session = _build_session()
    repo = UserRepository(session)
    db_user = object()

    deleted = run_async(repo.delete(db_user))

    assert deleted is db_user
    session.delete.assert_awaited_once_with(db_user)
    session.commit.assert_awaited_once()


def test_authenticate_returns_none_when_user_not_found() -> None:
    session = _build_session()
    repo = UserRepository(session)
    repo.get_by_email = AsyncMock(return_value=None)  # type: ignore[method-assign]

    authenticated = run_async(repo.authenticate("user@example.com", "plain-pw"))

    assert authenticated is None


def test_authenticate_returns_none_when_password_is_invalid() -> None:
    session = _build_session()
    repo = UserRepository(session)
    db_user = SimpleNamespace(hashed_password="stored-hash")
    repo.get_by_email = AsyncMock(return_value=db_user)  # type: ignore[method-assign]

    with patch(
        "app.repositories.user.anyio.to_thread.run_sync",
        new=AsyncMock(return_value=False),
    ):
        authenticated = run_async(repo.authenticate("user@example.com", "wrong-pw"))

    assert authenticated is None


def test_authenticate_returns_user_when_password_is_valid() -> None:
    session = _build_session()
    repo = UserRepository(session)
    db_user = SimpleNamespace(hashed_password="stored-hash")
    repo.get_by_email = AsyncMock(return_value=db_user)  # type: ignore[method-assign]

    with patch(
        "app.repositories.user.anyio.to_thread.run_sync",
        new=AsyncMock(return_value=True),
    ):
        authenticated = run_async(repo.authenticate("user@example.com", "correct-pw"))

    assert authenticated is db_user


def test_change_password_raises_when_current_password_is_invalid() -> None:
    session = _build_session()
    repo = UserRepository(session)
    db_user = SimpleNamespace(hashed_password="stored-hash")

    with patch(
        "app.repositories.user.anyio.to_thread.run_sync",
        new=AsyncMock(return_value=False),
    ):
        with pytest.raises(ValueError, match="contraseña actual"):
            run_async(repo.change_password(db_user, "wrong-pw", "new-pw"))


def test_change_password_updates_hash_and_commits() -> None:
    session = _build_session()
    repo = UserRepository(session)
    db_user = SimpleNamespace(hashed_password="stored-hash")

    with patch(
        "app.repositories.user.anyio.to_thread.run_sync",
        new=AsyncMock(side_effect=[True, "new-hash"]),
    ):
        updated = run_async(repo.change_password(db_user, "current-pw", "new-pw"))

    assert updated is db_user
    assert db_user.hashed_password == "new-hash"
    session.add.assert_called_once_with(db_user)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(db_user)


def test_exists_returns_boolean_based_on_get() -> None:
    session = _build_session()
    repo = UserRepository(session)
    session.get.side_effect = [object(), None]

    assert run_async(repo.exists(uuid.uuid4())) is True
    assert run_async(repo.exists(uuid.uuid4())) is False


def test_count_returns_scalar_one() -> None:
    session = _build_session()
    repo = UserRepository(session)
    result = Mock()
    result.scalar_one.return_value = 12
    session.execute.return_value = result

    total = run_async(repo.count())

    assert total == 12
    session.execute.assert_awaited_once()


def test_search_returns_scalars_all() -> None:
    session = _build_session()
    repo = UserRepository(session)
    expected = [object(), object()]
    scalars_obj = Mock()
    scalars_obj.all.return_value = expected
    result = Mock()
    result.scalars.return_value = scalars_obj
    session.execute.return_value = result

    found = run_async(repo.search("example", skip=5, limit=10))

    assert found == expected


def test_count_search_returns_scalar_one() -> None:
    session = _build_session()
    repo = UserRepository(session)
    result = Mock()
    result.scalar_one.return_value = 3
    session.execute.return_value = result

    total = run_async(repo.count_search("example"))

    assert total == 3
