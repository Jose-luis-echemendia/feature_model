import pytest

from app.core.config import Settings
from app.core.config_helpers import (
    normalize_minio_endpoint,
    parse_cors,
    resolve_minio_connection,
)
from app.enums import Environment


@pytest.fixture
def base_settings_kwargs() -> dict:
    return {
        "ENVIRONMENT": Environment.DEVELOPMENT,
        "SECRET_KEY": "x" * 64,
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": 5432,
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "StrongPostgresPassword123!",
        "POSTGRES_DB": "feature_model",
        "MINIO_ENDPOINT": "localhost:9000",
        "MINIO_ACCESS_KEY": "StrongMinioAccessKey123",
        "MINIO_SECRET_KEY": "StrongMinioSecretKey123",
        "MINIO_BUCKET_FM": "feature-model",
        "MINIO_BUCKET_ASSETS": "assets",
        "FIRST_SUPERUSER": "admin@example.com",
        "FIRST_SUPERUSER_PASSWORD": "StrongSuperUserPassword123!",
    }


def test_parse_cors_splits_comma_separated_string() -> None:
    result = parse_cors("http://a.com, http://b.com")
    assert result == ["http://a.com", "http://b.com"]


def test_parse_cors_accepts_json_like_string_unchanged() -> None:
    result = parse_cors('["http://a.com"]')
    assert result == '["http://a.com"]'


def test_parse_cors_rejects_invalid_type() -> None:
    with pytest.raises(ValueError):
        parse_cors(123)


def test_settings_computes_all_cors_origins(base_settings_kwargs: dict) -> None:
    settings = Settings(
        **base_settings_kwargs,
        BACKEND_CORS_ORIGINS=["http://api.local/", "http://admin.local"],
        FRONTEND_HOST="http://frontend.local",
    )

    assert settings.all_cors_origins == [
        "http://api.local",
        "http://admin.local",
        "http://frontend.local",
    ]


def test_settings_builds_redis_urls_with_password(base_settings_kwargs: dict) -> None:
    settings = Settings(
        **base_settings_kwargs,
        REDIS_HOST="redis.local",
        REDIS_PORT=6380,
        REDIS_PASSWORD="redisStrongPassword123",
        REDIS_DB_BROKER=10,
        REDIS_DB_BACKEND=11,
        REDIS_DB_CACHE=12,
    )

    assert (
        settings.REDIS_URL_BROKER
        == "redis://:redisStrongPassword123@redis.local:6380/10"
    )
    assert (
        settings.REDIS_URL_BACKEND
        == "redis://:redisStrongPassword123@redis.local:6380/11"
    )
    assert (
        settings.REDIS_URL_CACHE
        == "redis://:redisStrongPassword123@redis.local:6380/12"
    )


def test_normalize_minio_endpoint_strips_scheme_and_path() -> None:
    assert normalize_minio_endpoint("https://minio.example.com:9000/s3") == (
        "minio.example.com:9000"
    )
    assert normalize_minio_endpoint("minio.example.com:9000/s3") == (
        "minio.example.com:9000"
    )
    assert normalize_minio_endpoint("minio:9000") == "minio:9000"
    assert normalize_minio_endpoint("http://minio:9000/path") == "minio:9000"
    assert normalize_minio_endpoint("minio.local") == "minio.local"


def test_settings_exposes_normalized_minio_endpoint_host(
    base_settings_kwargs: dict,
) -> None:
    settings = Settings(
        **base_settings_kwargs,
        MINIO_ENDPOINT="https://minio.example.com:9000/s3",
    )

    assert settings.MINIO_ENDPOINT_HOST == "minio.example.com:9000"


def test_resolve_minio_connection_prefers_explicit_http_scheme() -> None:
    host, use_ssl = resolve_minio_connection("http://minio-service:9099", True)

    assert host == "minio-service:9099"
    assert use_ssl is False


def test_resolve_minio_connection_prefers_explicit_https_scheme() -> None:
    host, use_ssl = resolve_minio_connection("https://minio-service:9099", False)

    assert host == "minio-service:9099"
    assert use_ssl is True


def test_settings_production_requires_non_empty_cors(
    base_settings_kwargs: dict,
) -> None:
    with pytest.raises(ValueError, match="BACKEND_CORS_ORIGINS"):
        Settings(
            **base_settings_kwargs,
            ENVIRONMENT=Environment.PRODUCTION,
            LOG_JSON=True,
            BACKEND_CORS_ORIGINS=[],
        )


def test_settings_production_rejects_debug_true(base_settings_kwargs: dict) -> None:
    with pytest.raises(ValueError, match="DEBUG"):
        Settings(
            **base_settings_kwargs,
            ENVIRONMENT=Environment.PRODUCTION,
            LOG_JSON=True,
            DEBUG=True,
            BACKEND_CORS_ORIGINS=["http://allowed.local"],
        )


def test_settings_production_requires_json_logging(base_settings_kwargs: dict) -> None:
    with pytest.raises(ValueError, match="LOG_JSON"):
        Settings(
            **base_settings_kwargs,
            ENVIRONMENT=Environment.PRODUCTION,
            LOG_JSON=False,
            DEBUG=False,
            BACKEND_CORS_ORIGINS=["http://allowed.local"],
        )
