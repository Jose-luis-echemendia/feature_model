import asyncio
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.api.deps import (
    get_current_active_superuser,
    get_current_user,
    get_optional_user,
    role_required,
)
from app.enums import UserRole


def _run(coro):
    return asyncio.run(coro)


def test_get_current_user_without_token_raises_401() -> None:
    user_repo = AsyncMock()
    with pytest.raises(HTTPException) as exc:
        _run(get_current_user(user_repo=user_repo, token=""))
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_get_current_user_with_expired_token_raises_401() -> None:
    user_repo = AsyncMock()
    with patch("app.api.deps.jwt.decode", side_effect=ExpiredSignatureError()):
        with pytest.raises(HTTPException) as exc:
            _run(get_current_user(user_repo=user_repo, token="expired"))

    assert exc.value.status_code == 401
    assert exc.value.detail == "Token expired"


def test_get_current_user_with_invalid_token_raises_401() -> None:
    user_repo = AsyncMock()
    with patch("app.api.deps.jwt.decode", side_effect=InvalidTokenError()):
        with pytest.raises(HTTPException) as exc:
            _run(get_current_user(user_repo=user_repo, token="invalid"))

    assert exc.value.status_code == 401
    assert exc.value.detail == "Could not validate credentials"


def test_get_current_user_when_user_not_found_raises_401() -> None:
    user_id = uuid.uuid4()
    user_repo = AsyncMock()
    user_repo.get = AsyncMock(return_value=None)

    with patch("app.api.deps.jwt.decode", return_value={"sub": str(user_id)}):
        with pytest.raises(HTTPException) as exc:
            _run(get_current_user(user_repo=user_repo, token="ok"))

    assert exc.value.status_code == 401
    assert exc.value.detail == "User not found"


def test_get_current_user_when_user_inactive_raises_403() -> None:
    user_id = uuid.uuid4()
    inactive_user = SimpleNamespace(is_active=False)
    user_repo = AsyncMock()
    user_repo.get = AsyncMock(return_value=inactive_user)

    with patch("app.api.deps.jwt.decode", return_value={"sub": str(user_id)}):
        with pytest.raises(HTTPException) as exc:
            _run(get_current_user(user_repo=user_repo, token="ok"))

    assert exc.value.status_code == 403
    assert exc.value.detail == "Inactive user"


def test_get_current_user_returns_user_when_token_and_user_valid() -> None:
    user_id = uuid.uuid4()
    active_user = SimpleNamespace(is_active=True, role=UserRole.ADMIN)
    user_repo = AsyncMock()
    user_repo.get = AsyncMock(return_value=active_user)

    with patch("app.api.deps.jwt.decode", return_value={"sub": str(user_id)}):
        result = _run(get_current_user(user_repo=user_repo, token="ok"))

    assert result is active_user


def test_get_optional_user_without_token_returns_none() -> None:
    user_repo = AsyncMock()
    assert _run(get_optional_user(user_repo=user_repo, token=None)) is None


def test_get_optional_user_returns_none_when_auth_fails() -> None:
    user_repo = AsyncMock()
    with patch(
        "app.api.deps.get_current_user",
        new=AsyncMock(side_effect=HTTPException(status_code=401, detail="fail")),
    ):
        assert _run(get_optional_user(user_repo=user_repo, token="bad")) is None


def test_get_current_active_superuser_rejects_non_superuser() -> None:
    with pytest.raises(HTTPException) as exc:
        _run(
            get_current_active_superuser(
                current_user=SimpleNamespace(is_superuser=False)
            )
        )

    assert exc.value.status_code == 403


def test_role_required_allows_expected_role() -> None:
    dependency = role_required([UserRole.ADMIN, UserRole.DEVELOPER])
    current_user = SimpleNamespace(role=UserRole.ADMIN)

    result = _run(dependency(current_user))
    assert result is current_user


def test_role_required_rejects_unexpected_role() -> None:
    dependency = role_required([UserRole.ADMIN, UserRole.DEVELOPER])
    current_user = SimpleNamespace(role=UserRole.VIEWER)

    with pytest.raises(HTTPException) as exc:
        _run(dependency(current_user))

    assert exc.value.status_code == 403
    assert "Allowed roles" in str(exc.value.detail)
