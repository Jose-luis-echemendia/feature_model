import asyncio
from datetime import timedelta

import jwt
import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.core.security import (
    REFRESH_TOKEN_TYPE,
    ALGORITHM,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    require_admin_key,
    require_api_key,
    verify_password,
)


def test_require_api_key_rejects_missing_key() -> None:
    with pytest.raises(HTTPException) as exc:
        asyncio.run(require_api_key(None))
    assert exc.value.status_code == 403


def test_require_api_key_accepts_valid_key() -> None:
    api_key = settings.SECRET_KEY.get_secret_value()
    result = asyncio.run(require_api_key(api_key))
    assert result == api_key


def test_require_admin_key_rejects_invalid_key() -> None:
    with pytest.raises(HTTPException) as exc:
        asyncio.run(require_admin_key("invalid-key"))
    assert exc.value.status_code == 403


def test_require_admin_key_accepts_valid_key() -> None:
    admin_key = settings.SECRET_KEY.get_secret_value()
    result = asyncio.run(require_admin_key(admin_key))
    assert result == admin_key


def test_create_access_token_includes_subject_and_role() -> None:
    token = create_access_token(
        subject="user-123",
        expires_delta=timedelta(minutes=10),
        role="admin",
    )

    payload = jwt.decode(
        token,
        settings.SECRET_KEY.get_secret_value(),
        algorithms=[ALGORITHM],
    )
    assert payload["sub"] == "user-123"
    assert payload["role"] == "admin"
    assert "exp" in payload


def test_create_refresh_token_contains_expected_claims() -> None:
    token = create_refresh_token(subject="user-123", expires_delta=timedelta(days=1))

    payload = jwt.decode(
        token,
        settings.SECRET_KEY.get_secret_value(),
        algorithms=[ALGORITHM],
    )
    assert payload["sub"] == "user-123"
    assert payload["type"] == REFRESH_TOKEN_TYPE
    assert payload["jti"]
    assert "exp" in payload


def test_password_hash_and_verify_roundtrip() -> None:
    plain = "StrongPassword123!"
    hashed = get_password_hash(plain)

    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("wrong-password", hashed) is False
