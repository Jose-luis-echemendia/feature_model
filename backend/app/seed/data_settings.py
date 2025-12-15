"""
Datos de configuración del sistema (App Settings)
"""

# Estructura: (key, value, description)
settings_data = [
    ("MAINTENANCE_MODE", False, "Indica si el sistema está en modo mantenimiento"),
    (
        "GENERATE_PDF",
        True,
        "Permite la generación de PDF de planes de estudio y configuraciones",
    ),
    ("DOWNLOAD_PDF", True, "Permite la descarga de PDF de itinerarios curriculares"),
    (
        "CHECK_TASK",
        True,
        "Permite la consulta de tareas de procesamiento en segundo plano",
    ),
    (
        "ENABLE_CURRICULUM_VALIDATION",
        True,
        "Activa la validación automática de coherencia curricular",
    ),
    (
        "MAX_CURRICULUM_VERSIONS",
        10,
        "Número máximo de versiones de planes de estudio a mantener",
    ),
    (
        "ENABLE_COLLABORATIVE_DESIGN",
        True,
        "Permite el diseño colaborativo de modelos curriculares",
    ),
    ("AUTO_SAVE_INTERVAL", 300, "Intervalo de auto-guardado en segundos (5 minutos)"),
    (
        "ENABLE_LEARNING_ANALYTICS",
        True,
        "Activa el módulo de analíticas de aprendizaje",
    ),
    (
        "DEFAULT_CREDIT_HOURS",
        120,
        "Créditos académicos por defecto para un programa completo",
    ),
    (
        "ALLOWS_USER_REGISTRATION",
        False,
        "Indica si el sistema permite el registro de nuevos usuarios"
    )
]
