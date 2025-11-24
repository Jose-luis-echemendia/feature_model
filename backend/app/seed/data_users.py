"""
Datos de usuarios del sistema
Incluye usuarios de producción y de desarrollo/testing
"""

from app.enums import UserRole

# ============================================================================
# USUARIOS DE PRODUCCIÓN (se crean siempre)
# ============================================================================
# Estructura: (email, role)
production_users = [
    ("echemendiajoseluis@gmail.com", UserRole.ADMIN),
    ("carlos.rodriguez@gmail.com", UserRole.MODEL_DESIGNER),
    ("laura.martinez@gmail.com", UserRole.MODEL_EDITOR),
    ("lianysm99@gmail.com", UserRole.CONFIGURATOR),
    ("yadira.rodriguez@gmail.com", UserRole.VIEWER),
    ("ernesto.lito@gmail.com", UserRole.REVIEWER),
]

# ============================================================================
# USUARIOS DE DESARROLLO/TESTING (solo en entorno local/development)
# ============================================================================
# Estructura: (email, password, role, is_superuser)
development_users = [
    ("admin@example.com", "admin123", UserRole.ADMIN, True),
    ("designer@example.com", "designer123", UserRole.MODEL_DESIGNER, False),
    ("editor@example.com", "editor123", UserRole.MODEL_EDITOR, False),
    ("configurator@example.com", "config123", UserRole.CONFIGURATOR, False),
    ("viewer@example.com", "viewer123", UserRole.VIEWER, False),
    ("reviewer@example.com", "reviewer123", UserRole.REVIEWER, False),
]
