import secrets
import warnings
from typing import Annotated, Any
from functools import lru_cache

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
    field_validator,
    SecretStr,
    Field,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self
from pathlib import Path

from app.enums import Environment


# ── Directorio raíz del proyecto ──────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parents[2]  # cv-generator/
TEMPLATES_DIR = ROOT_DIR / "app" / "templates"


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        env_ignore_empty=True,
    )

    # ── Entorno ───────────────────────────────────────────────────────────────
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False

    # ── Aplicación ────────────────────────────────────────────────────────────
    APP_NAME: str = "Feature Models API"
    DOMAIN: str = "http://127.0.0.1:8000"
    APP_VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    FRONTEND_HOST: str = "http://localhost:5173"

    # 60 minutes * 24 hours * 8 days = 8 days

    # ── Seguridad ─────────────────────────────────────────────────────────────
    SECRET_KEY: SecretStr = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # 60 minutes * 24 hours * 30 days = 30 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
    )
    LOG_JSON: bool = Field(
        default=False,
        description="True = structlog en formato JSON (producción). False = consola legible.",
    )

    # ── Sentry Settings (Optional) ─────────────────────────────────────────────
    SENTRY_ENVIRONMENT: str | None = None
    SENTRY_DSN: HttpUrl | None = None

    # ── Base de datos (PostgreSQL async) ──────────────────────────────────────
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    # Pool de conexiones SQLAlchemy
    DB_POOL_SIZE: int = Field(default=10, ge=1, le=50)
    DB_MAX_OVERFLOW: int = Field(default=20, ge=0, le=100)
    DB_POOL_TIMEOUT: int = Field(default=30, ge=5)  # segundos
    DB_POOL_RECYCLE: int = Field(
        default=1800, ge=60
    )  # 30 min — evita conexiones muertas
    DB_ECHO: bool = False

    # --- S3/MinIO Settings ---
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_FM: str
    MINIO_BUCKET_ASSETS: str
    MINIO_USE_SSL: bool = True
    # TTL del presigned URL de descarga (segundos)
    MINIO_PRESIGN_TTL: int = Field(
        default=3600,
        ge=60,
        le=604800,
        description="Validez del link de descarga. Máx 7 días.",
    )
    MINIO_PUBLIC_DOMAIN: str | None = None

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: SecretStr | None = None
    REDIS_DB_BROKER: int = Field(
        default=0, description="Base de datos Redis para Celery broker"
    )
    REDIS_DB_BACKEND: int = Field(
        default=1, description="Base de datos Redis para Celery result backend"
    )
    REDIS_DB_CACHE: int = Field(
        default=2, description="Base de datos Redis para caché de la app"
    )

    # TTL de caché
    CACHE_TTL_SHORT: int = 60  # 1 min  — datos muy volátiles
    CACHE_TTL_DEFAULT: int = 300  # 5 min  — listados, etc.
    CACHE_TTL_LONG: int = 3600  # 1 hora — plantillas, config estática

    @property
    def REDIS_URL_BROKER(self) -> str:
        """URL Redis para el broker de Celery."""
        return self._build_redis_url(self.REDIS_DB_BROKER)

    @property
    def REDIS_URL_BACKEND(self) -> str:
        """URL Redis para el result backend de Celery."""
        return self._build_redis_url(self.REDIS_DB_BACKEND)

    @property
    def REDIS_URL_CACHE(self) -> str:
        """URL Redis para caché de la aplicación."""
        return self._build_redis_url(self.REDIS_DB_CACHE)

    def _build_redis_url(self, db: int) -> str:
        password = self.REDIS_PASSWORD
        auth = f":{password.get_secret_value()}@" if password else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{db}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    # ── Celery ────────────────────────────────────────────────────────────────
    CELERY_TASK_SOFT_TIME_LIMIT: int = 120  # segundos — warning antes de matar
    CELERY_TASK_TIME_LIMIT: int = 180  # segundos — kill hard
    CELERY_MAX_RETRIES: int = 3
    CELERY_RETRY_BACKOFF: int = 60  # segundos entre reintentos

    # ── Email (SMTP) ───────────────────────────────────────────────────────────
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: EmailStr | None = None
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEST_USER: EmailStr = "test@example.com"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    # --- FIRST USER ---
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    # ─────────────────────────────────────────────────────────────────────────
    # Validadores
    # ─────────────────────────────────────────────────────────────────────────

    # ─────────────────────────────────────────────────────────────────────────
    # Validadores
    # ─────────────────────────────────────────────────────────────────────────

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        raw = v.get_secret_value() if hasattr(v, "get_secret_value") else str(v)
        if len(raw) < 32:
            raise ValueError(
                "SECRET_KEY debe tener al menos 32 caracteres. "
                'Genera uno con: python -c "import secrets; print(secrets.token_hex(32))"'
            )
        return v

    @field_validator(
        "SENTRY_ENVIRONMENT",
        "SENTRY_DSN",
        "SMTP_HOST",
        "SMTP_USER",
        "SMTP_PASSWORD",
        "EMAILS_FROM_EMAIL",
        "EMAILS_FROM_NAME",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, v: Any) -> Any:
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @field_validator("SMTP_TLS", mode="before")
    @classmethod
    def default_smtp_tls_if_empty(cls, v: Any) -> Any:
        if isinstance(v, str) and v.strip() == "":
            return True
        return v

    @field_validator("SMTP_SSL", mode="before")
    @classmethod
    def default_smtp_ssl_if_empty(cls, v: Any) -> Any:
        if isinstance(v, str) and v.strip() == "":
            return False
        return v

    @field_validator("SMTP_PORT", mode="before")
    @classmethod
    def default_smtp_port_if_empty(cls, v: Any) -> Any:
        if isinstance(v, str) and v.strip() == "":
            return 587
        return v

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Comprobaciones extra que solo aplican en producción."""
        if self.ENVIRONMENT == Environment.PRODUCTION:
            if not self.BACKEND_CORS_ORIGINS:
                raise ValueError(
                    "BACKEND_CORS_ORIGINS no puede estar vacío en producción."
                )
            if self.DEBUG:
                raise ValueError("DEBUG no puede ser True en producción.")
            # if not self.MINIO_USE_SSL:
            #     raise ValueError(
            #         "MINIO_USE_SSL debe ser True en producción (requiere HTTPS)."
            #     )
            if not self.LOG_JSON:
                raise ValueError(
                    "LOG_JSON debe ser True en producción para logging estructurado."
                )
        return self

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.APP_NAME
        return self

    # ─────────────────────────────────────────────────────────────────────────
    # Validadores para los secretos
    # ─────────────────────────────────────────────────────────────────────────

    def _check_default_secret(
        self, var_name: str, value: SecretStr | str | None
    ) -> None:
        raw_value = value.get_secret_value() if isinstance(value, SecretStr) else value
        normalized = raw_value.strip() if isinstance(raw_value, str) else raw_value

        if normalized in ("", None):
            raise ValueError(f"{var_name} debe ser configurado.")

        insecure_defaults = {
            "changethis",
            "postgres",
            "password",
            "admin",
            "minioadmin",
            "minioadminsecret",
        }

        if (
            isinstance(normalized, str)
            and normalized.lower() in insecure_defaults
            and not self.is_development
        ):
            raise ValueError(
                f"{var_name} no puede usar un valor por defecto/inseguro. "
                "Debes cambiarlo en las variables de entorno."
            )

        if self.is_development:
            warnings.warn(
                f"{var_name} está configurado. Recuerda usar valores robustos para despliegues.",
                stacklevel=1,
            )
        return

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )
        self._check_default_secret("MINIO_ACCESS_KEY", self.MINIO_ACCESS_KEY)
        self._check_default_secret("MINIO_SECRET_KEY", self.MINIO_SECRET_KEY)

        if self.REDIS_PASSWORD is not None:
            self._check_default_secret("REDIS_PASSWORD", self.REDIS_PASSWORD)

        if self.SMTP_PASSWORD is not None:
            self._check_default_secret("SMTP_PASSWORD", self.SMTP_PASSWORD)

        return self

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION


# ── Singleton ─────────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Instancia única de Settings — se cachea tras la primera llamada.
    Usa lru_cache para evitar releer el .env en cada import.

    En tests puedes invalidar la caché con:
        get_settings.cache_clear()
    """
    return Settings()  # type: ignore[call-arg]


settings: Settings = get_settings()
