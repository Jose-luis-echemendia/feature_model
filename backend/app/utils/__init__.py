"""
Inicialización del submódulo utils.

Incluye utilidades generales y funciones de ayuda para la aplicación backend.
"""

from .generators import custom_generate_unique_id
from .email import (
    send_email,
    generate_test_email,
    render_email_template,
    generate_password_reset_token,
    generate_reset_password_email,
    verify_password_reset_token
)
from .cache import invalidate_cache_pattern
