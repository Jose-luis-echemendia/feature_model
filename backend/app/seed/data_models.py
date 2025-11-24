"""
Datos de dominios, tags, recursos y feature models
Solo para desarrollo/testing - Enfocados en el sector educativo
"""

# ============================================================================
# DOMINIOS EDUCATIVOS
# ============================================================================
domains_data = [
    {
        "name": "Ingeniería Informática",
        "description": "Programas y planes de estudio para carreras de ingeniería en ciencias informáticas",
    },
    {
        "name": "Ciencias Básicas",
        "description": "Cursos de matemáticas, física y química para programas de ingeniería",
    },
    {
        "name": "Formación General",
        "description": "Cursos de humanidades, idiomas y formación integral",
    },
    {
        "name": "Desarrollo de Software",
        "description": "Programas especializados en ingeniería de software y desarrollo de aplicaciones",
    },
    {
        "name": "Ciencia de Datos",
        "description": "Planes de estudio para ciencia de datos, inteligencia artificial y machine learning",
    },
    {
        "name": "Seguridad Informática",
        "description": "Programas de ciberseguridad y seguridad de la información",
    },
]

# ============================================================================
# TAGS PEDAGÓGICOS
# ============================================================================
tags_data = [
    {
        "name": "fundamentos",
        "description": "Cursos fundamentales y de introducción",
    },
    {
        "name": "avanzado",
        "description": "Contenido de nivel avanzado",
    },
    {
        "name": "práctico",
        "description": "Enfoque práctico con laboratorios y proyectos",
    },
    {
        "name": "teórico",
        "description": "Contenido teórico y conceptual",
    },
    {
        "name": "obligatorio",
        "description": "Asignatura obligatoria del plan de estudios",
    },
    {
        "name": "electivo",
        "description": "Asignatura electiva u optativa",
    },
    {
        "name": "proyecto",
        "description": "Curso basado en proyectos",
    },
    {
        "name": "certificacion",
        "description": "Preparación para certificaciones profesionales",
    },
    {
        "name": "investigacion",
        "description": "Componente de investigación",
    },
    {
        "name": "practica_profesional",
        "description": "Prácticas profesionales o pasantías",
    },
]

# ============================================================================
# RECURSOS EDUCATIVOS
# ============================================================================
from app.enums import ResourceType, ResourceStatus, LicenseType

resources_data = [
    {
        "title": "Introducción a Feature Models en Educación",
        "type": ResourceType.VIDEO,
        "description": "Video tutorial sobre cómo modelar planes de estudio usando feature models",
        "language": "es",
        "duration_minutes": 20,
        "status": ResourceStatus.PUBLISHED,
        "license": LicenseType.CREATIVE_COMMONS_BY,
        "content_url_or_data": {"url": "https://example.com/videos/intro-fm-educacion"},
    },
    {
        "title": "Guía de Diseño Curricular con Feature Models",
        "type": ResourceType.PDF,
        "description": "Documento completo sobre metodología de diseño curricular usando modelos de características",
        "language": "es",
        "status": ResourceStatus.PUBLISHED,
        "license": LicenseType.CREATIVE_COMMONS_BY_SA,
        "content_url_or_data": {
            "url": "https://example.com/docs/guia-diseno-curricular.pdf"
        },
    },
    {
        "title": "Programación Orientada a Objetos - Conceptos Fundamentales",
        "type": ResourceType.VIDEO,
        "description": "Serie de videos sobre POO con ejemplos en Python y Java",
        "language": "es",
        "duration_minutes": 45,
        "status": ResourceStatus.PUBLISHED,
        "license": LicenseType.CREATIVE_COMMONS_BY,
        "content_url_or_data": {"url": "https://example.com/videos/poo-fundamentos"},
    },
    {
        "title": "Estructuras de Datos - Material de Estudio",
        "type": ResourceType.PDF,
        "description": "Guía completa de estructuras de datos con ejercicios",
        "language": "es",
        "status": ResourceStatus.PUBLISHED,
        "license": LicenseType.INTERNAL_USE,
        "content_url_or_data": {
            "url": "https://example.com/docs/estructuras-datos.pdf"
        },
    },
    {
        "title": "Quiz de Validación Curricular",
        "type": ResourceType.QUIZ,
        "description": "Evaluación sobre reglas y restricciones en diseño curricular",
        "language": "es",
        "duration_minutes": 15,
        "status": ResourceStatus.PUBLISHED,
        "license": LicenseType.INTERNAL_USE,
        "content_url_or_data": {
            "questions": [
                {
                    "question": "¿Qué es un requisito previo (prerequisito) en un plan de estudios?",
                    "options": [
                        "Una asignatura que debe cursarse antes que otra",
                        "Una asignatura opcional",
                        "Un crédito adicional",
                        "Un recurso de aprendizaje",
                    ],
                    "correct": 0,
                }
            ]
        },
    },
    {
        "title": "Base de Datos - Laboratorios Prácticos",
        "type": ResourceType.OTHER,
        "description": "Conjunto de laboratorios prácticos para curso de bases de datos",
        "language": "es",
        "status": ResourceStatus.PUBLISHED,
        "license": LicenseType.INTERNAL_USE,
        "content_url_or_data": {"url": "https://example.com/labs/bases-datos"},
    },
]

# ============================================================================
# FEATURE MODELS - PLANES DE ESTUDIO
# ============================================================================
from app.enums import FeatureType, ModelStatus

# Modelo 1: Carrera de Ingeniería Informática
ingenieria_informatica_model = {
    "name": "Ingeniería en Ciencias Informáticas",
    "description": "Plan de estudios completo para la carrera de Ingeniería en Ciencias Informáticas (5 años)",
    "domain_name": "Ingeniería Informática",
    "version": {
        "version_number": 1,
        "status": ModelStatus.PUBLISHED,
        "features": [
            {
                "name": "Plan de Estudios ICI",
                "type": FeatureType.MANDATORY,
                "properties": {
                    "description": "Plan de estudios de Ingeniería en Ciencias Informáticas",
                    "creditos_totales": 240,
                    "duracion_años": 5,
                },
                "children": [
                    {
                        "name": "Ciclo Básico",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Formación básica en ciencias",
                            "creditos": 60,
                            "semestres": "1-2",
                        },
                        "children": [
                            {
                                "name": "Matemática I",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "creditos": 6,
                                    "semestre": 1,
                                    "horas_teoricas": 48,
                                    "horas_practicas": 32,
                                },
                            },
                            {
                                "name": "Matemática II",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "creditos": 6,
                                    "semestre": 2,
                                    "prerequisitos": ["Matemática I"],
                                },
                            },
                            {
                                "name": "Fundamentos de Programación",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "creditos": 8,
                                    "semestre": 1,
                                    "horas_practicas": 64,
                                },
                            },
                            {
                                "name": "Estructuras de Datos",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "creditos": 6,
                                    "semestre": 2,
                                    "prerequisitos": ["Fundamentos de Programación"],
                                },
                            },
                        ],
                    },
                    {
                        "name": "Ciclo Profesional",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Formación profesional específica",
                            "creditos": 120,
                            "semestres": "3-8",
                        },
                        "children": [
                            {
                                "name": "Ingeniería de Software",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "creditos": 8,
                                    "semestre": 3,
                                },
                            },
                            {
                                "name": "Bases de Datos",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "creditos": 6,
                                    "semestre": 4,
                                },
                            },
                            {
                                "name": "Redes de Computadoras",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "creditos": 6,
                                    "semestre": 5,
                                },
                            },
                            {
                                "name": "Especialización",
                                "type": FeatureType.XOR_GROUP,
                                "properties": {
                                    "description": "Elegir una especialización",
                                    "creditos": 30,
                                },
                                "children": [
                                    {
                                        "name": "Desarrollo de Software",
                                        "type": FeatureType.ALTERNATIVE,
                                        "properties": {
                                            "creditos": 30,
                                            "asignaturas": [
                                                "Arquitectura de Software",
                                                "DevOps y CI/CD",
                                                "Microservicios",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Ciencia de Datos",
                                        "type": FeatureType.ALTERNATIVE,
                                        "properties": {
                                            "creditos": 30,
                                            "asignaturas": [
                                                "Machine Learning",
                                                "Big Data",
                                                "Visualización de Datos",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Seguridad Informática",
                                        "type": FeatureType.ALTERNATIVE,
                                        "properties": {
                                            "creditos": 30,
                                            "asignaturas": [
                                                "Criptografía",
                                                "Hacking Ético",
                                                "Seguridad en Redes",
                                            ],
                                        },
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        "name": "Asignaturas Electivas",
                        "type": FeatureType.OR_GROUP,
                        "properties": {
                            "description": "Elegir al menos 3 electivas",
                            "creditos_minimos": 18,
                            "creditos_por_asignatura": 6,
                        },
                        "children": [
                            {
                                "name": "Desarrollo Móvil",
                                "type": FeatureType.OPTIONAL,
                                "properties": {"creditos": 6},
                            },
                            {
                                "name": "Computación en la Nube",
                                "type": FeatureType.OPTIONAL,
                                "properties": {"creditos": 6},
                            },
                            {
                                "name": "Internet de las Cosas",
                                "type": FeatureType.OPTIONAL,
                                "properties": {"creditos": 6},
                            },
                            {
                                "name": "Blockchain",
                                "type": FeatureType.OPTIONAL,
                                "properties": {"creditos": 6},
                            },
                            {
                                "name": "Realidad Virtual y Aumentada",
                                "type": FeatureType.OPTIONAL,
                                "properties": {"creditos": 6},
                            },
                        ],
                    },
                    {
                        "name": "Práctica Profesional",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "creditos": 12,
                            "semestre": 9,
                            "duracion_semanas": 16,
                        },
                    },
                    {
                        "name": "Trabajo de Diploma",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "creditos": 30,
                            "semestre": 10,
                        },
                    },
                ],
            }
        ],
    },
}

# Modelo 2: Curso de Desarrollo Web Full Stack
curso_fullstack_model = {
    "name": "Desarrollo Web Full Stack",
    "description": "Curso intensivo de desarrollo web frontend y backend",
    "domain_name": "Desarrollo de Software",
    "version": {
        "version_number": 1,
        "status": ModelStatus.PUBLISHED,
        "features": [
            {
                "name": "Curso Full Stack",
                "type": FeatureType.MANDATORY,
                "properties": {
                    "description": "Programa completo de desarrollo web",
                    "duracion_meses": 6,
                    "modalidad": "híbrido",
                },
                "children": [
                    {
                        "name": "Frontend Development",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "descripcion": "Desarrollo de interfaces de usuario",
                            "horas": 120,
                        },
                        "children": [
                            {
                                "name": "HTML/CSS Fundamentals",
                                "type": FeatureType.MANDATORY,
                                "properties": {"horas": 20},
                            },
                            {
                                "name": "JavaScript",
                                "type": FeatureType.MANDATORY,
                                "properties": {"horas": 40},
                            },
                            {
                                "name": "Framework Frontend",
                                "type": FeatureType.XOR_GROUP,
                                "properties": {
                                    "descripcion": "Elegir un framework",
                                },
                                "children": [
                                    {
                                        "name": "React",
                                        "type": FeatureType.ALTERNATIVE,
                                        "properties": {"horas": 60},
                                    },
                                    {
                                        "name": "Vue.js",
                                        "type": FeatureType.ALTERNATIVE,
                                        "properties": {"horas": 60},
                                    },
                                    {
                                        "name": "Angular",
                                        "type": FeatureType.ALTERNATIVE,
                                        "properties": {"horas": 60},
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        "name": "Backend Development",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "descripcion": "Desarrollo de APIs y lógica de negocio",
                            "horas": 100,
                        },
                        "children": [
                            {
                                "name": "Node.js y Express",
                                "type": FeatureType.MANDATORY,
                                "properties": {"horas": 40},
                            },
                            {
                                "name": "Bases de Datos",
                                "type": FeatureType.MANDATORY,
                                "properties": {"horas": 30},
                            },
                            {
                                "name": "RESTful APIs",
                                "type": FeatureType.MANDATORY,
                                "properties": {"horas": 30},
                            },
                        ],
                    },
                    {
                        "name": "Módulos Opcionales",
                        "type": FeatureType.OR_GROUP,
                        "properties": {
                            "descripcion": "Elegir al menos uno",
                        },
                        "children": [
                            {
                                "name": "DevOps Básico",
                                "type": FeatureType.OPTIONAL,
                                "properties": {"horas": 20},
                            },
                            {
                                "name": "Testing Avanzado",
                                "type": FeatureType.OPTIONAL,
                                "properties": {"horas": 20},
                            },
                            {
                                "name": "Seguridad Web",
                                "type": FeatureType.OPTIONAL,
                                "properties": {"horas": 20},
                            },
                        ],
                    },
                    {
                        "name": "Proyecto Final",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "descripcion": "Proyecto integrador full stack",
                            "horas": 80,
                        },
                    },
                ],
            }
        ],
    },
}

# Lista de todos los modelos
feature_models_data = [
    ingenieria_informatica_model,
    curso_fullstack_model,
]
