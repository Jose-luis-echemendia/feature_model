"""
Inicialización del submódulo utils.

Incluye utilidades generales y funciones de ayuda para la aplicación backend.
"""

from importlib import import_module

from .cache import invalidate_cache_pattern
from .config import normalize_minio_endpoint, parse_cors, resolve_minio_connection
from .generators import custom_generate_unique_id

_EMAIL_EXPORTS = {
    "send_email",
    "generate_test_email",
    "render_email_template",
    "generate_password_reset_token",
    "generate_reset_password_email",
    "generate_new_account_email",
    "verify_password_reset_token",
    "EmailData",
}


def __getattr__(name: str):
    if name in _EMAIL_EXPORTS:
        module = import_module("app.utils.email")
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "custom_generate_unique_id",
    "invalidate_cache_pattern",
    "normalize_minio_endpoint",
    "parse_cors",
    "resolve_minio_connection",
    *sorted(_EMAIL_EXPORTS),
]
