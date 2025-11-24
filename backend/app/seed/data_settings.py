"""
Datos de configuración del sistema (App Settings)
"""

# Estructura: (key, value, description)
settings_data = [
    ("MAINTENANCE_MODE", True, "Dice si el sistema está en modo mantenimiento"),
    ("GENERATE_PDF", False, "Dice si el sistema permite la generación de PDF"),
    ("DOWNLOAD_PDF", False, "Dice si el sistema permite la descarga de PDF"),
    ("CHECK_TASK", False, "Dice si el sistema permite la consulta de tareas de celery"),
]
