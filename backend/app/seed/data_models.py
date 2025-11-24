"""
Datos de dominios, tags, recursos y feature models
Solo para desarrollo/testing
"""

# ============================================================================
# DOMINIOS
# ============================================================================
domains_data = [
    {
        "name": "E-Commerce",
        "description": "Dominio para sistemas de comercio electrónico",
    },
    {
        "name": "Healthcare",
        "description": "Dominio para aplicaciones de salud y medicina",
    },
    {
        "name": "Education",
        "description": "Dominio para plataformas educativas y e-learning",
    },
    {
        "name": "IoT",
        "description": "Dominio para Internet de las Cosas y dispositivos conectados",
    },
    {
        "name": "Finance",
        "description": "Dominio para aplicaciones financieras y bancarias",
    },
]

# ============================================================================
# TAGS
# ============================================================================
tags_data = [
    {
        "name": "performance",
        "description": "Características relacionadas con rendimiento",
    },
    {"name": "security", "description": "Características de seguridad"},
    {"name": "ui", "description": "Interfaz de usuario"},
    {"name": "api", "description": "Integración con APIs"},
    {"name": "mobile", "description": "Funcionalidad móvil"},
    {"name": "analytics", "description": "Análisis y métricas"},
    {"name": "payment", "description": "Procesamiento de pagos"},
    {"name": "authentication", "description": "Autenticación y autorización"},
    {"name": "database", "description": "Gestión de base de datos"},
    {"name": "cloud", "description": "Servicios en la nube"},
]

# ============================================================================
# RECURSOS EDUCATIVOS
# ============================================================================
from app.enums import ResourceType, ResourceStatus, LicenseType

resources_data = [
    {
        "title": "Introducción a Feature Models",
        "type": ResourceType.VIDEO,
        "description": "Video tutorial sobre conceptos básicos de feature modeling",
        "language": "es",
        "duration_minutes": 15,
        "status": ResourceStatus.PUBLISHED,
        "license": LicenseType.CREATIVE_COMMONS_BY,
        "content_url_or_data": {"url": "https://example.com/videos/intro-fm"},
    },
    {
        "title": "Guía de Configuración",
        "type": ResourceType.PDF,
        "description": "Documento PDF con guía completa de configuración",
        "language": "es",
        "status": ResourceStatus.PUBLISHED,
        "license": LicenseType.CREATIVE_COMMONS_BY_SA,
        "content_url_or_data": {"url": "https://example.com/docs/config-guide.pdf"},
    },
    {
        "title": "Quiz de Feature Modeling",
        "type": ResourceType.QUIZ,
        "description": "Evaluación de conocimientos básicos",
        "language": "es",
        "duration_minutes": 10,
        "status": ResourceStatus.PUBLISHED,
        "license": LicenseType.INTERNAL_USE,
        "content_url_or_data": {
            "questions": [
                {
                    "question": "¿Qué es un feature model?",
                    "options": [
                        "Una representación jerárquica de características",
                        "Un modelo de datos",
                        "Un patrón de diseño",
                        "Ninguna de las anteriores",
                    ],
                    "correct": 0,
                }
            ]
        },
    },
    {
        "title": "Tutorial Avanzado de Feature Models",
        "type": ResourceType.VIDEO,
        "description": "Conceptos avanzados y mejores prácticas",
        "language": "en",
        "duration_minutes": 30,
        "status": ResourceStatus.PUBLISHED,
        "license": LicenseType.CREATIVE_COMMONS_BY,
        "content_url_or_data": {"url": "https://example.com/videos/advanced-fm"},
    },
]

# ============================================================================
# FEATURE MODELS
# ============================================================================
from app.enums import FeatureType, ModelStatus

# Modelo E-Commerce
ecommerce_model = {
    "name": "E-Commerce Platform",
    "description": "Modelo de características para una plataforma de comercio electrónico completa",
    "domain_name": "E-Commerce",  # Referencia al dominio
    "version": {
        "version_number": 1,
        "status": ModelStatus.PUBLISHED,
        "features": [
            {
                "name": "E-Commerce System",
                "type": FeatureType.MANDATORY,
                "properties": {
                    "description": "Sistema completo de comercio electrónico"
                },
                "children": [
                    {
                        "name": "Product Catalog",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Catálogo de productos con búsqueda y filtros"
                        },
                    },
                    {
                        "name": "Shopping Cart",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Carrito de compras con gestión de items"
                        },
                    },
                    {
                        "name": "Payment Processing",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Procesamiento de pagos con múltiples métodos"
                        },
                    },
                    {
                        "name": "User Management",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Gestión de usuarios y autenticación"
                        },
                    },
                    {
                        "name": "Wishlist",
                        "type": FeatureType.OPTIONAL,
                        "properties": {
                            "description": "Lista de deseos para productos favoritos"
                        },
                    },
                    {
                        "name": "Product Reviews",
                        "type": FeatureType.OPTIONAL,
                        "properties": {
                            "description": "Sistema de reseñas y calificaciones"
                        },
                    },
                    {
                        "name": "Recommendations",
                        "type": FeatureType.OPTIONAL,
                        "properties": {
                            "description": "Motor de recomendaciones personalizadas"
                        },
                    },
                ],
            }
        ],
    },
}

# Modelo Healthcare
healthcare_model = {
    "name": "Healthcare Management System",
    "description": "Sistema de gestión hospitalaria y atención médica",
    "domain_name": "Healthcare",
    "version": {
        "version_number": 1,
        "status": ModelStatus.PUBLISHED,
        "features": [
            {
                "name": "Healthcare System",
                "type": FeatureType.MANDATORY,
                "properties": {"description": "Sistema completo de gestión médica"},
                "children": [
                    {
                        "name": "Patient Management",
                        "type": FeatureType.MANDATORY,
                        "properties": {"description": "Gestión de pacientes"},
                    },
                    {
                        "name": "Appointment Scheduling",
                        "type": FeatureType.MANDATORY,
                        "properties": {"description": "Programación de citas"},
                    },
                    {
                        "name": "Medical Records",
                        "type": FeatureType.MANDATORY,
                        "properties": {"description": "Historial médico electrónico"},
                    },
                    {
                        "name": "Telemedicine",
                        "type": FeatureType.OPTIONAL,
                        "properties": {"description": "Consultas médicas remotas"},
                    },
                ],
            }
        ],
    },
}

# Lista de todos los modelos
feature_models_data = [
    ecommerce_model,
    healthcare_model,
]
