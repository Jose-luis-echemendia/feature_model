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
    ("yadira.rodriguez@uci.cu", UserRole.MODEL_DESIGNER),
    ("liany.sobrino@uci.cu", UserRole.MODEL_DESIGNER),
    ("ernesto.valdes@estudiantes.uci.cu", UserRole.MODEL_EDITOR),
    ("coord.academica@uci.cu", UserRole.CONFIGURATOR),
    ("jefe.departamento@uci.cu", UserRole.REVIEWER),
]

# ============================================================================
# USUARIOS DE DESARROLLO/TESTING (solo en entorno local/development)
# ============================================================================
# Estructura: (email, password, role, is_superuser)
development_users = [
    ("admin@example.com", "admin123", UserRole.ADMIN, True),
    ("diseñador.curricular@example.com", "designer123", UserRole.MODEL_DESIGNER, False),
    ("coordinador.academico@example.com", "editor123", UserRole.MODEL_EDITOR, False),
    ("jefe.carrera@example.com", "config123", UserRole.CONFIGURATOR, False),
    ("profesor@example.com", "viewer123", UserRole.VIEWER, False),
    ("evaluador.curricular@example.com", "reviewer123", UserRole.REVIEWER, False),
]
