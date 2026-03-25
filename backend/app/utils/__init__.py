"""
Inicialización del submódulo utils.

Incluye utilidades generales y funciones de ayuda para la aplicación backend.
"""

from .generators import custom_generate_unique_id
from .email import (
    send_email,
    generate_test_email,
    render_email_template,
)
from .cache import invalidate_cache_pattern
