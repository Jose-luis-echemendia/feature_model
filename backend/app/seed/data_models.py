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

# Modelo 3: Maestría en Ciencia de Datos
maestria_ciencia_datos_model = {
    "name": "Maestría en Ciencia de Datos e Inteligencia Artificial",
    "description": "Programa de posgrado avanzado en ciencia de datos, machine learning e inteligencia artificial (2 años, 90 créditos)",
    "domain_name": "Ciencia de Datos",
    "version": {
        "version_number": 1,
        "status": ModelStatus.PUBLISHED,
        "features": [
            {
                "name": "Maestría en Ciencia de Datos",
                "type": FeatureType.MANDATORY,
                "properties": {
                    "description": "Programa completo de maestría",
                    "creditos_totales": 90,
                    "duracion_años": 2,
                    "nivel": "posgrado",
                    "modalidad": "presencial",
                },
                "children": [
                    # NIVEL 2: Núcleo Fundamental
                    {
                        "name": "Núcleo Fundamental",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Asignaturas fundamentales obligatorias",
                            "creditos": 36,
                            "semestres": "1-2",
                        },
                        "children": [
                            # NIVEL 3: Asignaturas del núcleo
                            {
                                "name": "Matemáticas Avanzadas",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "creditos": 12,
                                    "semestre": 1,
                                    "horas_totales": 160,
                                },
                                "children": [
                                    # NIVEL 4: Módulos de matemáticas
                                    {
                                        "name": "Álgebra Lineal Computacional",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "creditos": 4,
                                            "horas": 48,
                                            "temas": [
                                                "Matrices",
                                                "Eigenvalores",
                                                "SVD",
                                                "PCA",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Cálculo Multivariable",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "creditos": 4,
                                            "horas": 48,
                                            "prerequisitos": [
                                                "Álgebra Lineal Computacional"
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Optimización Matemática",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "creditos": 4,
                                            "horas": 64,
                                            "temas": [
                                                "Gradiente Descendente",
                                                "Optimización Convexa",
                                            ],
                                        },
                                    },
                                ],
                            },
                            {
                                "name": "Estadística y Probabilidad",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "creditos": 12,
                                    "semestre": 1,
                                    "horas_totales": 160,
                                },
                                "children": [
                                    # NIVEL 4: Módulos de estadística
                                    {
                                        "name": "Probabilidad Avanzada",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "creditos": 4,
                                            "horas": 48,
                                            "temas": [
                                                "Distribuciones",
                                                "Teorema Central Límite",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Inferencia Estadística",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "creditos": 4,
                                            "horas": 48,
                                            "prerequisitos": ["Probabilidad Avanzada"],
                                        },
                                    },
                                    {
                                        "name": "Análisis Bayesiano",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "creditos": 4,
                                            "horas": 64,
                                            "temas": ["Prior", "Posterior", "MCMC"],
                                        },
                                    },
                                ],
                            },
                            {
                                "name": "Programación para Ciencia de Datos",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "creditos": 12,
                                    "semestre": 1,
                                    "horas_totales": 180,
                                },
                                "children": [
                                    # NIVEL 4: Herramientas de programación
                                    {
                                        "name": "Python Científico",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "creditos": 4,
                                            "horas": 60,
                                            "tecnologias": [
                                                "NumPy",
                                                "Pandas",
                                                "Matplotlib",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Entorno R",
                                        "type": FeatureType.OPTIONAL,
                                        "properties": {
                                            "creditos": 4,
                                            "horas": 60,
                                            "tecnologias": [
                                                "dplyr",
                                                "ggplot2",
                                                "tidyverse",
                                            ],
                                            "nota": "Alternativa a Python para análisis estadístico",
                                        },
                                    },
                                    {
                                        "name": "SQL y Bases de Datos",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "creditos": 4,
                                            "horas": 60,
                                            "temas": [
                                                "Consultas avanzadas",
                                                "Optimización",
                                                "NoSQL",
                                            ],
                                        },
                                    },
                                ],
                            },
                        ],
                    },
                    # NIVEL 2: Área de Machine Learning
                    {
                        "name": "Machine Learning",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Módulo completo de aprendizaje automático",
                            "creditos": 24,
                            "semestres": "2-3",
                        },
                        "children": [
                            # NIVEL 3: Aprendizaje Supervisado
                            {
                                "name": "Aprendizaje Supervisado",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "creditos": 8,
                                    "semestre": 2,
                                    "horas": 120,
                                },
                                "children": [
                                    # NIVEL 4: Técnicas específicas
                                    {
                                        "name": "Regresión Avanzada",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "creditos": 2,
                                            "temas": [
                                                "Lineal",
                                                "Logística",
                                                "Ridge",
                                                "Lasso",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Árboles de Decisión y Ensambles",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "creditos": 3,
                                            "temas": [
                                                "Random Forest",
                                                "XGBoost",
                                                "LightGBM",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Support Vector Machines",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "creditos": 3,
                                            "temas": [
                                                "Kernels",
                                                "Hiperplanos",
                                                "SVM multiclase",
                                            ],
                                        },
                                    },
                                ],
                            },
                            # NIVEL 3: Aprendizaje No Supervisado
                            {
                                "name": "Aprendizaje No Supervisado",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "creditos": 8,
                                    "semestre": 2,
                                    "horas": 120,
                                },
                                "children": [
                                    # NIVEL 4: Técnicas de clustering
                                    {
                                        "name": "Clustering",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "creditos": 4,
                                            "temas": [
                                                "K-Means",
                                                "DBSCAN",
                                                "Hierarchical",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Reducción de Dimensionalidad",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "creditos": 4,
                                            "temas": [
                                                "PCA",
                                                "t-SNE",
                                                "UMAP",
                                                "Autoencoders",
                                            ],
                                            "prerequisitos": [
                                                "Álgebra Lineal Computacional"
                                            ],
                                        },
                                    },
                                ],
                            },
                            # NIVEL 3: Deep Learning
                            {
                                "name": "Deep Learning",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "creditos": 8,
                                    "semestre": 3,
                                    "horas": 140,
                                },
                                "children": [
                                    # NIVEL 4: Arquitecturas de redes neuronales
                                    {
                                        "name": "Redes Neuronales Fundamentales",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "creditos": 2,
                                            "temas": [
                                                "Perceptrón",
                                                "Backpropagation",
                                                "MLP",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Especialización en Arquitecturas",
                                        "type": FeatureType.XOR_GROUP,
                                        "properties": {
                                            "description": "Elegir una especialización profunda",
                                            "creditos": 6,
                                        },
                                        "children": [
                                            {
                                                "name": "Visión por Computadora (CNN)",
                                                "type": FeatureType.ALTERNATIVE,
                                                "properties": {
                                                    "creditos": 6,
                                                    "temas": [
                                                        "ResNet",
                                                        "YOLO",
                                                        "Segmentación",
                                                        "GANs",
                                                    ],
                                                    "frameworks": [
                                                        "PyTorch",
                                                        "TensorFlow",
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "Procesamiento de Lenguaje Natural (NLP)",
                                                "type": FeatureType.ALTERNATIVE,
                                                "properties": {
                                                    "creditos": 6,
                                                    "temas": [
                                                        "Transformers",
                                                        "BERT",
                                                        "GPT",
                                                        "Attention",
                                                    ],
                                                    "frameworks": [
                                                        "Hugging Face",
                                                        "spaCy",
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "Series Temporales (RNN/LSTM)",
                                                "type": FeatureType.ALTERNATIVE,
                                                "properties": {
                                                    "creditos": 6,
                                                    "temas": [
                                                        "RNN",
                                                        "LSTM",
                                                        "GRU",
                                                        "Forecasting",
                                                    ],
                                                    "aplicaciones": [
                                                        "Finanzas",
                                                        "Clima",
                                                        "IoT",
                                                    ],
                                                },
                                            },
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                    # NIVEL 2: Big Data e Infraestructura
                    {
                        "name": "Big Data e Infraestructura",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Procesamiento de grandes volúmenes de datos",
                            "creditos": 12,
                            "semestre": 3,
                        },
                        "children": [
                            # NIVEL 3: Tecnologías Big Data
                            {
                                "name": "Tecnologías Distribuidas",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "creditos": 6,
                                    "horas": 90,
                                },
                                "children": [
                                    # NIVEL 4: Herramientas específicas
                                    {
                                        "name": "Apache Spark",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "creditos": 3,
                                            "temas": [
                                                "RDD",
                                                "DataFrames",
                                                "MLlib",
                                                "Streaming",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Hadoop Ecosystem",
                                        "type": FeatureType.OPTIONAL,
                                        "properties": {
                                            "creditos": 3,
                                            "temas": [
                                                "HDFS",
                                                "MapReduce",
                                                "Hive",
                                                "Pig",
                                            ],
                                        },
                                    },
                                ],
                            },
                            {
                                "name": "Cloud Computing para ML",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "creditos": 6,
                                    "horas": 90,
                                },
                                "children": [
                                    # NIVEL 4: Plataformas cloud (OR group - elegir al menos una)
                                    {
                                        "name": "Plataformas Cloud",
                                        "type": FeatureType.OR_GROUP,
                                        "properties": {
                                            "description": "Elegir al menos una plataforma cloud",
                                            "minimo_selecciones": 1,
                                        },
                                        "children": [
                                            {
                                                "name": "AWS SageMaker",
                                                "type": FeatureType.OPTIONAL,
                                                "properties": {
                                                    "creditos": 2,
                                                    "servicios": [
                                                        "S3",
                                                        "EC2",
                                                        "Lambda",
                                                        "SageMaker",
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "Google Cloud AI",
                                                "type": FeatureType.OPTIONAL,
                                                "properties": {
                                                    "creditos": 2,
                                                    "servicios": [
                                                        "Vertex AI",
                                                        "BigQuery",
                                                        "Cloud Functions",
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "Azure Machine Learning",
                                                "type": FeatureType.OPTIONAL,
                                                "properties": {
                                                    "creditos": 2,
                                                    "servicios": [
                                                        "Azure ML",
                                                        "Databricks",
                                                        "Cognitive Services",
                                                    ],
                                                },
                                            },
                                        ],
                                    },
                                    {
                                        "name": "MLOps y Deployment",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "creditos": 4,
                                            "temas": [
                                                "Docker",
                                                "Kubernetes",
                                                "CI/CD",
                                                "Monitoring",
                                            ],
                                        },
                                    },
                                ],
                            },
                        ],
                    },
                    # NIVEL 2: Asignaturas Complementarias (OR group)
                    {
                        "name": "Asignaturas Complementarias",
                        "type": FeatureType.OR_GROUP,
                        "properties": {
                            "description": "Elegir al menos 2 asignaturas complementarias",
                            "creditos_minimos": 8,
                            "creditos_por_asignatura": 4,
                            "minimo_selecciones": 2,
                        },
                        "children": [
                            # NIVEL 3: Opciones complementarias
                            {
                                "name": "Ética en IA",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "creditos": 4,
                                    "semestre": 3,
                                    "temas": [
                                        "Bias",
                                        "Fairness",
                                        "Privacy",
                                        "Transparency",
                                    ],
                                },
                            },
                            {
                                "name": "Visualización de Datos Avanzada",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "creditos": 4,
                                    "semestre": 3,
                                    "herramientas": [
                                        "D3.js",
                                        "Tableau",
                                        "Power BI",
                                        "Plotly",
                                    ],
                                },
                            },
                            {
                                "name": "Aprendizaje por Refuerzo",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "creditos": 4,
                                    "semestre": 3,
                                    "temas": [
                                        "Q-Learning",
                                        "Policy Gradients",
                                        "Actor-Critic",
                                    ],
                                    "prerequisitos": ["Deep Learning"],
                                },
                            },
                            {
                                "name": "Graph Neural Networks",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "creditos": 4,
                                    "semestre": 3,
                                    "temas": [
                                        "GCN",
                                        "GraphSAGE",
                                        "GAT",
                                        "Knowledge Graphs",
                                    ],
                                    "prerequisitos": ["Deep Learning"],
                                },
                            },
                            {
                                "name": "Análisis de Datos Biomédicos",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "creditos": 4,
                                    "semestre": 3,
                                    "aplicaciones": [
                                        "Genómica",
                                        "Diagnóstico",
                                        "Drug Discovery",
                                    ],
                                },
                            },
                        ],
                    },
                    # NIVEL 2: Proyecto de Investigación
                    {
                        "name": "Trabajo de Fin de Maestría",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Proyecto de investigación o aplicación práctica",
                            "creditos": 10,
                            "semestre": 4,
                            "duracion_meses": 6,
                        },
                        "children": [
                            # NIVEL 3: Componentes del proyecto
                            {
                                "name": "Propuesta de Investigación",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "peso": "20%",
                                    "entregable": "Documento de propuesta",
                                },
                            },
                            {
                                "name": "Desarrollo e Implementación",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "peso": "50%",
                                    "entregable": "Código y modelos",
                                },
                            },
                            {
                                "name": "Documentación y Defensa",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "peso": "30%",
                                    "entregable": "Tesis y presentación",
                                },
                            },
                        ],
                    },
                ],
            }
        ],
        # Relaciones entre features (constraints)
        "feature_relations": [
            {
                "source": "Deep Learning",
                "target": "Python Científico",
                "type": "requires",
                "description": "Deep Learning requiere dominio de Python Científico",
            },
            {
                "source": "Visión por Computadora (CNN)",
                "target": "Álgebra Lineal Computacional",
                "type": "requires",
                "description": "CNN requiere conocimientos avanzados de álgebra lineal",
            },
            {
                "source": "Procesamiento de Lenguaje Natural (NLP)",
                "target": "Probabilidad Avanzada",
                "type": "requires",
                "description": "NLP requiere fundamentos sólidos en probabilidad",
            },
            {
                "source": "Apache Spark",
                "target": "Python Científico",
                "type": "requires",
                "description": "Spark requiere conocimientos de Python",
            },
            {
                "source": "Entorno R",
                "target": "Python Científico",
                "type": "excludes",
                "description": "Si se elige R, no se puede cursar Python (son alternativos)",
            },
            {
                "source": "Aprendizaje por Refuerzo",
                "target": "Redes Neuronales Fundamentales",
                "type": "requires",
                "description": "RL requiere fundamentos de redes neuronales",
            },
            {
                "source": "Graph Neural Networks",
                "target": "Deep Learning",
                "type": "requires",
                "description": "GNN requiere conocimientos de Deep Learning",
            },
        ],
    },
}

# Modelo 4: Curso de Desarrollo Móvil Básico
curso_desarrollo_movil_model = {
    "name": "Desarrollo de Aplicaciones Móviles - Nivel Básico",
    "description": "Curso intensivo de desarrollo móvil multiplataforma (3 meses, 120 horas)",
    "domain_name": "Desarrollo de Software",
    "version": {
        "version_number": 1,
        "status": ModelStatus.PUBLISHED,
        "features": [
            {
                "name": "Curso Desarrollo Móvil",
                "type": FeatureType.MANDATORY,
                "properties": {
                    "description": "Programa completo de desarrollo móvil",
                    "duracion_meses": 3,
                    "horas_totales": 120,
                    "nivel": "básico",
                    "modalidad": "online",
                },
                "children": [
                    # NIVEL 2: Fundamentos de Desarrollo Móvil
                    {
                        "name": "Fundamentos de Desarrollo Móvil",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Conceptos básicos y arquitectura móvil",
                            "horas": 20,
                            "semanas": "1-2",
                        },
                        "children": [
                            # NIVEL 3: Temas fundamentales
                            {
                                "name": "Introducción a Plataformas Móviles",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 8,
                                    "temas": [
                                        "iOS vs Android",
                                        "Arquitectura",
                                        "Ecosistema",
                                    ],
                                },
                            },
                            {
                                "name": "UI/UX para Móviles",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 8,
                                    "temas": [
                                        "Material Design",
                                        "Human Interface Guidelines",
                                        "Responsive Design",
                                    ],
                                },
                            },
                            {
                                "name": "Ciclo de Vida de Apps",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 4,
                                    "temas": [
                                        "Estados",
                                        "Eventos",
                                        "Gestión de memoria",
                                    ],
                                },
                            },
                        ],
                    },
                    # NIVEL 2: Plataforma de Desarrollo (XOR - elegir una)
                    {
                        "name": "Plataforma de Desarrollo",
                        "type": FeatureType.XOR_GROUP,
                        "properties": {
                            "description": "Elegir una plataforma principal",
                            "horas": 60,
                            "semanas": "3-8",
                        },
                        "children": [
                            # NIVEL 3: Opción 1 - React Native
                            {
                                "name": "React Native (Multiplataforma)",
                                "type": FeatureType.ALTERNATIVE,
                                "properties": {
                                    "horas": 60,
                                    "lenguaje": "JavaScript/TypeScript",
                                    "plataformas": ["iOS", "Android"],
                                },
                                "children": [
                                    {
                                        "name": "React Fundamentals",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "horas": 12,
                                            "temas": [
                                                "Components",
                                                "Props",
                                                "State",
                                                "Hooks",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "React Native Core",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "horas": 20,
                                            "temas": [
                                                "View",
                                                "Text",
                                                "FlatList",
                                                "Navigation",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Native Modules",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "horas": 12,
                                            "temas": [
                                                "Camera",
                                                "Geolocation",
                                                "Push Notifications",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Estado Global",
                                        "type": FeatureType.OR_GROUP,
                                        "properties": {
                                            "description": "Elegir al menos una librería de estado",
                                        },
                                        "children": [
                                            {
                                                "name": "Redux",
                                                "type": FeatureType.OPTIONAL,
                                                "properties": {
                                                    "horas": 8,
                                                    "temas": [
                                                        "Store",
                                                        "Actions",
                                                        "Reducers",
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "Context API",
                                                "type": FeatureType.OPTIONAL,
                                                "properties": {
                                                    "horas": 8,
                                                    "temas": [
                                                        "Provider",
                                                        "Consumer",
                                                        "useContext",
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "MobX",
                                                "type": FeatureType.OPTIONAL,
                                                "properties": {
                                                    "horas": 8,
                                                    "temas": [
                                                        "Observables",
                                                        "Actions",
                                                        "Reactions",
                                                    ],
                                                },
                                            },
                                        ],
                                    },
                                    {
                                        "name": "Styling en React Native",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "horas": 8,
                                            "temas": [
                                                "StyleSheet",
                                                "Flexbox",
                                                "Styled Components",
                                            ],
                                        },
                                    },
                                ],
                            },
                            # NIVEL 3: Opción 2 - Flutter
                            {
                                "name": "Flutter (Multiplataforma)",
                                "type": FeatureType.ALTERNATIVE,
                                "properties": {
                                    "horas": 60,
                                    "lenguaje": "Dart",
                                    "plataformas": ["iOS", "Android", "Web"],
                                },
                                "children": [
                                    {
                                        "name": "Dart Fundamentals",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "horas": 12,
                                            "temas": [
                                                "Variables",
                                                "Functions",
                                                "Classes",
                                                "Async",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Flutter Widgets",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "horas": 20,
                                            "temas": [
                                                "StatelessWidget",
                                                "StatefulWidget",
                                                "Layout",
                                                "Material",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Navigation & Routing",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "horas": 8,
                                            "temas": [
                                                "Navigator",
                                                "Routes",
                                                "Named Routes",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "State Management Flutter",
                                        "type": FeatureType.OR_GROUP,
                                        "properties": {
                                            "description": "Elegir al menos una solución de estado",
                                        },
                                        "children": [
                                            {
                                                "name": "Provider",
                                                "type": FeatureType.OPTIONAL,
                                                "properties": {
                                                    "horas": 8,
                                                    "temas": [
                                                        "ChangeNotifier",
                                                        "Consumer",
                                                        "Selector",
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "Riverpod",
                                                "type": FeatureType.OPTIONAL,
                                                "properties": {
                                                    "horas": 8,
                                                    "temas": [
                                                        "Providers",
                                                        "StateNotifier",
                                                        "FutureProvider",
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "BLoC Pattern",
                                                "type": FeatureType.OPTIONAL,
                                                "properties": {
                                                    "horas": 8,
                                                    "temas": [
                                                        "Events",
                                                        "States",
                                                        "Streams",
                                                    ],
                                                },
                                            },
                                        ],
                                    },
                                    {
                                        "name": "Flutter Plugins",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "horas": 12,
                                            "temas": [
                                                "http",
                                                "shared_preferences",
                                                "image_picker",
                                            ],
                                        },
                                    },
                                ],
                            },
                            # NIVEL 3: Opción 3 - Android Nativo
                            {
                                "name": "Android Nativo (Kotlin)",
                                "type": FeatureType.ALTERNATIVE,
                                "properties": {
                                    "horas": 60,
                                    "lenguaje": "Kotlin",
                                    "plataformas": ["Android"],
                                },
                                "children": [
                                    {
                                        "name": "Kotlin Fundamentals",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "horas": 12,
                                            "temas": [
                                                "Variables",
                                                "Functions",
                                                "Classes",
                                                "Coroutines",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Android Components",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "horas": 20,
                                            "temas": [
                                                "Activities",
                                                "Fragments",
                                                "Services",
                                                "Receivers",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Jetpack Components",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "horas": 16,
                                            "temas": [
                                                "ViewModel",
                                                "LiveData",
                                                "Room",
                                                "Navigation",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "UI en Android",
                                        "type": FeatureType.XOR_GROUP,
                                        "properties": {
                                            "description": "Elegir tecnología de UI",
                                        },
                                        "children": [
                                            {
                                                "name": "XML Layouts",
                                                "type": FeatureType.ALTERNATIVE,
                                                "properties": {
                                                    "horas": 12,
                                                    "temas": [
                                                        "ConstraintLayout",
                                                        "RecyclerView",
                                                        "Material Components",
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "Jetpack Compose",
                                                "type": FeatureType.ALTERNATIVE,
                                                "properties": {
                                                    "horas": 12,
                                                    "temas": [
                                                        "Composables",
                                                        "State",
                                                        "Layouts",
                                                        "Material3",
                                                    ],
                                                },
                                            },
                                        ],
                                    },
                                ],
                            },
                            # NIVEL 3: Opción 4 - iOS Nativo
                            {
                                "name": "iOS Nativo (Swift)",
                                "type": FeatureType.ALTERNATIVE,
                                "properties": {
                                    "horas": 60,
                                    "lenguaje": "Swift",
                                    "plataformas": ["iOS", "iPadOS"],
                                },
                                "children": [
                                    {
                                        "name": "Swift Fundamentals",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "horas": 12,
                                            "temas": [
                                                "Variables",
                                                "Optionals",
                                                "Closures",
                                                "Protocols",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "UIKit Basics",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "horas": 20,
                                            "temas": [
                                                "UIViewController",
                                                "UITableView",
                                                "Auto Layout",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "SwiftUI",
                                        "type": FeatureType.OPTIONAL,
                                        "properties": {
                                            "horas": 16,
                                            "temas": [
                                                "Views",
                                                "State",
                                                "Bindings",
                                                "Navigation",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "iOS Frameworks",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "horas": 12,
                                            "temas": [
                                                "URLSession",
                                                "Core Data",
                                                "UserDefaults",
                                            ],
                                        },
                                    },
                                ],
                            },
                        ],
                    },
                    # NIVEL 2: Backend Integration
                    {
                        "name": "Integración con Backend",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Conexión con APIs y servicios",
                            "horas": 16,
                            "semanas": "9-10",
                        },
                        "children": [
                            # NIVEL 3: Temas de integración
                            {
                                "name": "Consumo de APIs REST",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 8,
                                    "temas": ["HTTP Methods", "JSON", "Authentication"],
                                },
                            },
                            {
                                "name": "Persistencia Local",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 6,
                                    "temas": ["SQLite", "SharedPreferences", "Cache"],
                                },
                            },
                            {
                                "name": "Firebase Integration",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "horas": 8,
                                    "servicios": [
                                        "Authentication",
                                        "Firestore",
                                        "Cloud Messaging",
                                    ],
                                },
                            },
                        ],
                    },
                    # NIVEL 2: Testing y Deployment
                    {
                        "name": "Testing y Publicación",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Pruebas y despliegue en tiendas",
                            "horas": 12,
                            "semanas": "11-12",
                        },
                        "children": [
                            # NIVEL 3: Componentes de testing
                            {
                                "name": "Testing Básico",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 6,
                                    "tipos": ["Unit Tests", "Widget Tests"],
                                },
                            },
                            {
                                "name": "Deployment",
                                "type": FeatureType.OR_GROUP,
                                "properties": {
                                    "description": "Publicar en al menos una tienda",
                                },
                                "children": [
                                    {
                                        "name": "Google Play Store",
                                        "type": FeatureType.OPTIONAL,
                                        "properties": {
                                            "horas": 4,
                                            "temas": [
                                                "App Bundle",
                                                "Signing",
                                                "Store Listing",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Apple App Store",
                                        "type": FeatureType.OPTIONAL,
                                        "properties": {
                                            "horas": 4,
                                            "temas": [
                                                "App Store Connect",
                                                "TestFlight",
                                                "Review Process",
                                            ],
                                        },
                                    },
                                ],
                            },
                            {
                                "name": "Optimización de Rendimiento",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "horas": 4,
                                    "temas": [
                                        "Memory Leaks",
                                        "Battery Usage",
                                        "Network Optimization",
                                    ],
                                },
                            },
                        ],
                    },
                    # NIVEL 2: Proyecto Final
                    {
                        "name": "Proyecto Final",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Aplicación móvil completa",
                            "horas": 12,
                            "semanas": "12",
                        },
                        "children": [
                            # NIVEL 3: Componentes del proyecto
                            {
                                "name": "Diseño de la App",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 2,
                                    "entregable": "Mockups y wireframes",
                                },
                            },
                            {
                                "name": "Implementación",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 8,
                                    "entregable": "Código fuente y app funcional",
                                },
                            },
                            {
                                "name": "Presentación",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 2,
                                    "entregable": "Demo y documentación",
                                },
                            },
                        ],
                    },
                ],
            }
        ],
        # Relaciones entre features
        "feature_relations": [
            # React Native requiere fundamentos
            {
                "source": "React Native Core",
                "target": "React Fundamentals",
                "type": "requires",
                "description": "React Native Core requiere conocimientos de React",
            },
            {
                "source": "Native Modules",
                "target": "React Native Core",
                "type": "requires",
                "description": "Módulos nativos requieren dominio del core de React Native",
            },
            # Flutter requiere fundamentos
            {
                "source": "Flutter Widgets",
                "target": "Dart Fundamentals",
                "type": "requires",
                "description": "Widgets de Flutter requieren conocimientos de Dart",
            },
            {
                "source": "State Management Flutter",
                "target": "Flutter Widgets",
                "type": "requires",
                "description": "Gestión de estado requiere comprensión de widgets",
            },
            # Android requiere fundamentos
            {
                "source": "Android Components",
                "target": "Kotlin Fundamentals",
                "type": "requires",
                "description": "Componentes de Android requieren conocimientos de Kotlin",
            },
            {
                "source": "Jetpack Components",
                "target": "Android Components",
                "type": "requires",
                "description": "Jetpack requiere comprensión de componentes básicos",
            },
            {
                "source": "Jetpack Compose",
                "target": "Kotlin Fundamentals",
                "type": "requires",
                "description": "Compose requiere conocimientos avanzados de Kotlin",
            },
            # iOS requiere fundamentos
            {
                "source": "UIKit Basics",
                "target": "Swift Fundamentals",
                "type": "requires",
                "description": "UIKit requiere conocimientos de Swift",
            },
            {
                "source": "SwiftUI",
                "target": "Swift Fundamentals",
                "type": "requires",
                "description": "SwiftUI requiere dominio de Swift",
            },
            # Exclusiones entre tecnologías
            {
                "source": "XML Layouts",
                "target": "Jetpack Compose",
                "type": "excludes",
                "description": "XML Layouts y Compose son tecnologías alternativas",
            },
            # Integraciones requieren fundamentos de plataforma
            {
                "source": "Consumo de APIs REST",
                "target": "Fundamentos de Desarrollo Móvil",
                "type": "requires",
                "description": "APIs REST requieren comprensión de fundamentos móviles",
            },
            {
                "source": "Testing Básico",
                "target": "Plataforma de Desarrollo",
                "type": "requires",
                "description": "Testing requiere haber elegido una plataforma",
            },
            {
                "source": "Proyecto Final",
                "target": "Integración con Backend",
                "type": "requires",
                "description": "Proyecto final requiere conocimientos de integración",
            },
        ],
    },
}

# Lista de todos los modelos
feature_models_data = [
    ingenieria_informatica_model,
    curso_fullstack_model,
    maestria_ciencia_datos_model,
    curso_desarrollo_movil_model,
]
