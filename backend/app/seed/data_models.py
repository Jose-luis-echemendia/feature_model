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

# Modelo 5: Asignatura Gestión de Proyectos Informáticos (GPI)
asignatura_gpi_model = {
    "name": "Gestión de Proyectos Informáticos (GPI)",
    "description": "Asignatura completa sobre metodologías, técnicas y herramientas para la gestión exitosa de proyectos de software (1 semestre, 6 créditos)",
    "domain_name": "Ingeniería Informática",
    "version": {
        "version_number": 1,
        "status": ModelStatus.PUBLISHED,
        "features": [
            {
                "name": "GPI - Gestión de Proyectos Informáticos",
                "type": FeatureType.MANDATORY,
                "properties": {
                    "description": "Asignatura de gestión de proyectos de software",
                    "creditos": 6,
                    "semestre": 6,
                    "horas_totales": 96,
                    "horas_teoricas": 48,
                    "horas_practicas": 48,
                    "nivel": "pregrado",
                    "area": "ingeniería de software",
                },
                "children": [
                    # NIVEL 1: Módulos principales de la asignatura
                    {
                        "name": "Fundamentos de Gestión de Proyectos",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Conceptos básicos y marcos de referencia",
                            "creditos": 1.5,
                            "horas": 24,
                        },
                        "children": [
                            # NIVEL 2: Temas de fundamentos
                            {
                                "name": "Introducción a Proyectos",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 6,
                                    "temas": [
                                        "Definición de proyecto",
                                        "Ciclo de vida del proyecto",
                                        "Stakeholders",
                                    ],
                                },
                            },
                            {
                                "name": "Marcos de Referencia",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 8,
                                    "temas": [
                                        "PMI y PMBOK",
                                        "PRINCE2",
                                        "ISO 21500",
                                    ],
                                },
                            },
                            {
                                "name": "Roles del Proyecto",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 6,
                                    "temas": [
                                        "Project Manager",
                                        "Sponsor",
                                        "Equipo de proyecto",
                                        "Stakeholders",
                                    ],
                                },
                            },
                            {
                                "name": "Comparativa de Enfoques",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 4,
                                    "temas": [
                                        "Waterfall vs Ágil",
                                        "Cuándo usar cada enfoque",
                                        "Híbridos",
                                    ],
                                },
                            },
                        ],
                    },
                    {
                        "name": "Planificación y Estimación",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Técnicas de planificación y estimación de proyectos",
                            "creditos": 1.5,
                            "horas": 24,
                        },
                        "children": [
                            # NIVEL 2: Técnicas de planificación
                            {
                                "name": "Descomposición del Trabajo",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 8,
                                    "temas": [
                                        "WBS (Work Breakdown Structure)",
                                        "Paquetes de trabajo",
                                        "Diccionario WBS",
                                    ],
                                },
                            },
                            {
                                "name": "Técnicas de Estimación",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 8,
                                    "descripcion": "Métodos para estimar esfuerzo, costo y tiempo",
                                },
                                "children": [
                                    # NIVEL 3: Categorías de técnicas de estimación
                                    {
                                        "name": "Estimación Algorítmica",
                                        "type": FeatureType.OR_GROUP,
                                        "properties": {
                                            "description": "Elegir al menos un método algorítmico",
                                            "minimo_selecciones": 1,
                                        },
                                        "children": [
                                            {
                                                "name": "COCOMO II",
                                                "type": FeatureType.OPTIONAL,
                                                "properties": {
                                                    "niveles": [
                                                        "Básico",
                                                        "Intermedio",
                                                        "Detallado",
                                                    ],
                                                    "factores": [
                                                        "tamaño",
                                                        "complejidad",
                                                        "experiencia",
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "Puntos de Función (FPA)",
                                                "type": FeatureType.OPTIONAL,
                                                "properties": {
                                                    "componentes": [
                                                        "ILF",
                                                        "EIF",
                                                        "EI",
                                                        "EO",
                                                        "EQ",
                                                    ],
                                                    "complejidad": [
                                                        "Simple",
                                                        "Media",
                                                        "Compleja",
                                                    ],
                                                },
                                            },
                                        ],
                                    },
                                    {
                                        "name": "Estimación Ágil",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "description": "Técnicas de estimación para equipos ágiles",
                                        },
                                        "children": [
                                            {
                                                "name": "Planning Poker",
                                                "type": FeatureType.MANDATORY,
                                                "properties": {
                                                    "escala": "Fibonacci (1,2,3,5,8,13,21...)",
                                                    "participantes": "Todo el equipo",
                                                },
                                            },
                                            {
                                                "name": "Story Points",
                                                "type": FeatureType.MANDATORY,
                                                "properties": {
                                                    "factores": [
                                                        "complejidad",
                                                        "esfuerzo",
                                                        "riesgo",
                                                    ],
                                                },
                                            },
                                        ],
                                    },
                                    {
                                        "name": "Estimación por Analogía",
                                        "type": FeatureType.OPTIONAL,
                                        "properties": {
                                            "tecnica": "Comparación con proyectos similares",
                                            "precision": "Baja a Media",
                                        },
                                    },
                                ],
                            },
                            {
                                "name": "Gestión del Cronograma",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 8,
                                    "temas": [
                                        "Diagramas de Gantt",
                                        "Camino crítico (CPM)",
                                        "PERT",
                                        "Holguras y flotantes",
                                    ],
                                },
                            },
                        ],
                    },
                    {
                        "name": "Gestión de Equipos",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Liderazgo y gestión de recursos humanos",
                            "creditos": 1.0,
                            "horas": 16,
                        },
                        "children": [
                            # NIVEL 2: Aspectos de gestión de equipos
                            {
                                "name": "Formación y Desarrollo",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 4,
                                    "temas": [
                                        "Modelo Tuckman (Forming, Storming, Norming, Performing)",
                                        "Matriz RACI",
                                        "Skills matrix",
                                    ],
                                },
                            },
                            {
                                "name": "Liderazgo",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 6,
                                    "descripcion": "Estilos y teorías de liderazgo en proyectos",
                                },
                                "children": [
                                    # NIVEL 3: Componentes de liderazgo
                                    {
                                        "name": "Estilos de Liderazgo",
                                        "type": FeatureType.XOR_GROUP,
                                        "properties": {
                                            "description": "Elegir un estilo principal a profundizar",
                                        },
                                        "children": [
                                            {
                                                "name": "Liderazgo Transformacional",
                                                "type": FeatureType.ALTERNATIVE,
                                                "properties": {
                                                    "caracteristicas": [
                                                        "Visión",
                                                        "Inspiración",
                                                        "Cambio",
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "Liderazgo Situacional",
                                                "type": FeatureType.ALTERNATIVE,
                                                "properties": {
                                                    "niveles_madurez": [
                                                        "M1",
                                                        "M2",
                                                        "M3",
                                                        "M4",
                                                    ],
                                                    "estilos": [
                                                        "Dirigir",
                                                        "Persuadir",
                                                        "Participar",
                                                        "Delegar",
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "Servant Leadership",
                                                "type": FeatureType.ALTERNATIVE,
                                                "properties": {
                                                    "principios": [
                                                        "Servicio",
                                                        "Empatía",
                                                        "Empoderamiento",
                                                    ],
                                                    "aplicacion": "Ideal para equipos ágiles",
                                                },
                                            },
                                        ],
                                    },
                                    {
                                        "name": "Teorías de Motivación",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "description": "Teorías fundamentales de motivación",
                                        },
                                        "children": [
                                            {
                                                "name": "Teoría de Maslow",
                                                "type": FeatureType.MANDATORY,
                                                "properties": {
                                                    "niveles": [
                                                        "Fisiológicas",
                                                        "Seguridad",
                                                        "Sociales",
                                                        "Estima",
                                                        "Autorrealización",
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "Teoría de Herzberg",
                                                "type": FeatureType.MANDATORY,
                                                "properties": {
                                                    "factores_higiene": [
                                                        "Salario",
                                                        "Condiciones",
                                                        "Políticas",
                                                    ],
                                                    "factores_motivadores": [
                                                        "Logro",
                                                        "Reconocimiento",
                                                        "Crecimiento",
                                                    ],
                                                },
                                            },
                                        ],
                                    },
                                    {
                                        "name": "Inteligencia Emocional",
                                        "type": FeatureType.OPTIONAL,
                                        "properties": {
                                            "componentes": [
                                                "Autoconciencia",
                                                "Autorregulación",
                                                "Empatía",
                                                "Habilidades sociales",
                                            ],
                                        },
                                    },
                                ],
                            },
                            {
                                "name": "Comunicación",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 4,
                                    "temas": [
                                        "Plan de comunicaciones",
                                        "Reuniones efectivas",
                                        "Reportes de avance",
                                        "Comunicación con stakeholders",
                                    ],
                                },
                            },
                            {
                                "name": "Gestión de Conflictos",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 2,
                                    "temas": [
                                        "Fuentes de conflicto",
                                        "Técnicas de resolución",
                                        "Negociación",
                                    ],
                                },
                            },
                        ],
                    },
                    {
                        "name": "Gestión de Riesgos y Calidad",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Identificación y mitigación de riesgos, aseguramiento de calidad",
                            "creditos": 1.0,
                            "horas": 16,
                        },
                        "children": [
                            # NIVEL 2: Gestión de riesgos
                            {
                                "name": "Identificación de Riesgos",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 4,
                                    "tecnicas": [
                                        "Brainstorming",
                                        "Checklist",
                                        "Análisis SWOT",
                                        "Diagrama de Ishikawa",
                                    ],
                                },
                            },
                            {
                                "name": "Análisis de Riesgos",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 6,
                                    "descripcion": "Técnicas para analizar y priorizar riesgos",
                                },
                                "children": [
                                    # NIVEL 3: Tipos de análisis de riesgos
                                    {
                                        "name": "Análisis Cualitativo",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "description": "Evaluación subjetiva de riesgos",
                                        },
                                        "children": [
                                            {
                                                "name": "Matriz de Probabilidad e Impacto",
                                                "type": FeatureType.MANDATORY,
                                                "properties": {
                                                    "probabilidad": [
                                                        "Muy Baja",
                                                        "Baja",
                                                        "Media",
                                                        "Alta",
                                                        "Muy Alta",
                                                    ],
                                                    "impacto": [
                                                        "Muy Bajo",
                                                        "Bajo",
                                                        "Medio",
                                                        "Alto",
                                                        "Muy Alto",
                                                    ],
                                                    "niveles_riesgo": [
                                                        "Bajo",
                                                        "Medio",
                                                        "Alto",
                                                        "Crítico",
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "Categorización de Riesgos",
                                                "type": FeatureType.MANDATORY,
                                                "properties": {
                                                    "categorias": [
                                                        "Técnicos",
                                                        "Organizacionales",
                                                        "Externos",
                                                        "Project Management",
                                                    ],
                                                },
                                            },
                                        ],
                                    },
                                    {
                                        "name": "Análisis Cuantitativo",
                                        "type": FeatureType.OR_GROUP,
                                        "properties": {
                                            "description": "Técnicas numéricas - elegir al menos una",
                                            "minimo_selecciones": 1,
                                        },
                                        "children": [
                                            {
                                                "name": "Análisis EMV (Expected Monetary Value)",
                                                "type": FeatureType.OPTIONAL,
                                                "properties": {
                                                    "formula": "EMV = Probabilidad × Impacto",
                                                    "aplicacion": "Decisiones monetarias",
                                                },
                                            },
                                            {
                                                "name": "Árbol de Decisiones",
                                                "type": FeatureType.OPTIONAL,
                                                "properties": {
                                                    "componentes": [
                                                        "Nodos de decisión",
                                                        "Nodos de chance",
                                                        "Valores esperados",
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "Simulación Monte Carlo",
                                                "type": FeatureType.OPTIONAL,
                                                "properties": {
                                                    "iteraciones": "Mínimo 1000",
                                                    "salida": "Distribución de probabilidad",
                                                    "herramientas": [
                                                        "@RISK",
                                                        "Crystal Ball",
                                                    ],
                                                },
                                            },
                                        ],
                                    },
                                ],
                            },
                            {
                                "name": "Respuesta a Riesgos",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 3,
                                    "estrategias": [
                                        "Evitar",
                                        "Transferir",
                                        "Mitigar",
                                        "Aceptar",
                                    ],
                                },
                            },
                            {
                                "name": "Gestión de Calidad",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 3,
                                    "temas": [
                                        "Plan de calidad",
                                        "Métricas de calidad",
                                        "Control de calidad vs Aseguramiento",
                                        "Gestión de la configuración",
                                    ],
                                },
                            },
                        ],
                    },
                    {
                        "name": "Metodologías Ágiles",
                        "type": FeatureType.OR_GROUP,
                        "properties": {
                            "description": "Elegir al menos una metodología ágil para profundizar",
                            "creditos": 0.5,
                            "horas": 8,
                            "minimo_selecciones": 1,
                        },
                        "children": [
                            {
                                "name": "Scrum",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "horas": 8,
                                },
                                "children": [
                                    # NIVEL 2: Componentes de Scrum
                                    {
                                        "name": "Roles Scrum",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "descripcion": "Roles fundamentales del framework Scrum",
                                        },
                                        "children": [
                                            # NIVEL 3: Detalles de cada rol
                                            {
                                                "name": "Product Owner",
                                                "type": FeatureType.MANDATORY,
                                                "properties": {
                                                    "responsabilidades": [
                                                        "Maximizar valor del producto",
                                                        "Gestionar Product Backlog",
                                                        "Definir historias de usuario",
                                                        "Aceptar o rechazar trabajo",
                                                    ],
                                                    "habilidades_clave": [
                                                        "Visión",
                                                        "Comunicación",
                                                        "Decisión",
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "Scrum Master",
                                                "type": FeatureType.MANDATORY,
                                                "properties": {
                                                    "responsabilidades": [
                                                        "Facilitar eventos Scrum",
                                                        "Eliminar impedimentos",
                                                        "Coaching al equipo",
                                                        "Promover Scrum",
                                                    ],
                                                    "tipo_liderazgo": "Servant Leadership",
                                                },
                                            },
                                            {
                                                "name": "Development Team",
                                                "type": FeatureType.MANDATORY,
                                                "properties": {
                                                    "caracteristicas": [
                                                        "Auto-organizado",
                                                        "Multifuncional",
                                                        "Sin sub-equipos",
                                                    ],
                                                    "tamaño_ideal": "3-9 personas",
                                                },
                                            },
                                        ],
                                    },
                                    {
                                        "name": "Eventos Scrum",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "descripcion": "Eventos time-boxed de Scrum",
                                        },
                                        "children": [
                                            # NIVEL 3: Detalles de cada evento
                                            {
                                                "name": "Sprint",
                                                "type": FeatureType.MANDATORY,
                                                "properties": {
                                                    "duracion": "1-4 semanas",
                                                    "objetivo": "Crear incremento potencialmente entregable",
                                                },
                                            },
                                            {
                                                "name": "Sprint Planning",
                                                "type": FeatureType.MANDATORY,
                                                "properties": {
                                                    "duracion_max": "8 horas para sprint de 1 mes",
                                                    "preguntas_clave": [
                                                        "¿Qué se puede entregar en este Sprint?",
                                                        "¿Cómo se logrará el trabajo?",
                                                    ],
                                                    "salida": "Sprint Goal y Sprint Backlog",
                                                },
                                            },
                                            {
                                                "name": "Daily Scrum",
                                                "type": FeatureType.MANDATORY,
                                                "properties": {
                                                    "duracion_max": "15 minutos",
                                                    "preguntas": [
                                                        "¿Qué hice ayer?",
                                                        "¿Qué haré hoy?",
                                                        "¿Hay impedimentos?",
                                                    ],
                                                    "participantes": "Development Team",
                                                },
                                            },
                                            {
                                                "name": "Sprint Review",
                                                "type": FeatureType.MANDATORY,
                                                "properties": {
                                                    "duracion_max": "4 horas para sprint de 1 mes",
                                                    "actividades": [
                                                        "Demo del incremento",
                                                        "Revisión del Product Backlog",
                                                        "Discusión colaborativa",
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "Sprint Retrospective",
                                                "type": FeatureType.MANDATORY,
                                                "properties": {
                                                    "duracion_max": "3 horas para sprint de 1 mes",
                                                    "enfoque": [
                                                        "¿Qué salió bien?",
                                                        "¿Qué puede mejorar?",
                                                        "Plan de mejora",
                                                    ],
                                                    "salida": "Mejoras para el próximo Sprint",
                                                },
                                            },
                                        ],
                                    },
                                    {
                                        "name": "Artefactos Scrum",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "descripcion": "Artefactos que representan trabajo o valor",
                                        },
                                        "children": [
                                            # NIVEL 3: Detalles de cada artefacto
                                            {
                                                "name": "Product Backlog",
                                                "type": FeatureType.MANDATORY,
                                                "properties": {
                                                    "responsable": "Product Owner",
                                                    "contenido": "Lista ordenada de todo lo necesario en el producto",
                                                    "atributos": [
                                                        "Descripción",
                                                        "Orden",
                                                        "Estimación",
                                                        "Valor",
                                                    ],
                                                    "evolucion": "Nunca está completo",
                                                },
                                            },
                                            {
                                                "name": "Sprint Backlog",
                                                "type": FeatureType.MANDATORY,
                                                "properties": {
                                                    "responsable": "Development Team",
                                                    "contenido": [
                                                        "Items del Product Backlog para el Sprint",
                                                        "Plan para entregar el incremento",
                                                    ],
                                                    "visibilidad": "Altamente visible",
                                                },
                                            },
                                            {
                                                "name": "Increment",
                                                "type": FeatureType.MANDATORY,
                                                "properties": {
                                                    "definicion": "Suma de todos los items completados + incrementos previos",
                                                    "condicion": "Debe cumplir Definition of Done",
                                                    "estado": "Potencialmente entregable",
                                                },
                                            },
                                            {
                                                "name": "Definition of Done",
                                                "type": FeatureType.MANDATORY,
                                                "properties": {
                                                    "descripcion": "Entendimiento compartido de lo que significa 'Done'",
                                                    "ejemplos": [
                                                        "Código escrito",
                                                        "Tests pasando",
                                                        "Code review completado",
                                                        "Documentación actualizada",
                                                        "Desplegado en ambiente de prueba",
                                                    ],
                                                },
                                            },
                                        ],
                                    },
                                ],
                            },
                            {
                                "name": "Kanban",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "horas": 8,
                                },
                                "children": [
                                    # NIVEL 2: Componentes de Kanban
                                    {
                                        "name": "Principios Kanban",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "principios": [
                                                "Visualizar el flujo de trabajo",
                                                "Limitar el WIP (Work In Progress)",
                                                "Gestionar el flujo",
                                                "Hacer políticas explícitas",
                                                "Implementar ciclos de feedback",
                                                "Mejorar colaborativamente",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Métricas Kanban",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "metricas": [
                                                "Lead Time",
                                                "Cycle Time",
                                                "Throughput",
                                                "WIP",
                                                "Diagrama de flujo acumulado",
                                            ],
                                        },
                                    },
                                ],
                            },
                            {
                                "name": "XP (Extreme Programming)",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "horas": 8,
                                },
                                "children": [
                                    # NIVEL 2: Prácticas XP
                                    {
                                        "name": "Prácticas Técnicas XP",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "practicas": [
                                                "TDD (Test Driven Development)",
                                                "Pair Programming",
                                                "Refactoring continuo",
                                                "Continuous Integration",
                                                "Código colectivo",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Valores y Principios XP",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "valores": [
                                                "Comunicación",
                                                "Simplicidad",
                                                "Feedback",
                                                "Coraje",
                                                "Respeto",
                                            ],
                                        },
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        "name": "Herramientas de Gestión",
                        "type": FeatureType.OR_GROUP,
                        "properties": {
                            "description": "Aprender al menos una herramienta de gestión de proyectos",
                            "creditos": 0.5,
                            "horas": 8,
                            "minimo_selecciones": 1,
                        },
                        "children": [
                            {
                                "name": "Jira",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "tipo": "Gestión ágil",
                                    "horas": 8,
                                },
                                "children": [
                                    # NIVEL 2: Módulos de Jira
                                    {
                                        "name": "Jira Software",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "caracteristicas": [
                                                "Tableros Scrum",
                                                "Tableros Kanban",
                                                "Backlog management",
                                                "Sprints",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Reportes Jira",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "reportes": [
                                                "Burndown chart",
                                                "Velocity chart",
                                                "Cumulative flow diagram",
                                                "Custom dashboards",
                                            ],
                                        },
                                    },
                                ],
                            },
                            {
                                "name": "Microsoft Project",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "tipo": "Gestión tradicional",
                                    "horas": 8,
                                },
                                "children": [
                                    # NIVEL 2: Funcionalidades MS Project
                                    {
                                        "name": "Planificación en MS Project",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "funciones": [
                                                "Diagramas de Gantt",
                                                "Gestión de recursos",
                                                "Camino crítico",
                                                "Líneas base",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Seguimiento y Control",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "funciones": [
                                                "Earned Value Management",
                                                "Análisis de variaciones",
                                                "Reportes de estado",
                                            ],
                                        },
                                    },
                                ],
                            },
                            {
                                "name": "Trello",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "tipo": "Gestión visual simple",
                                    "horas": 8,
                                },
                                "children": [
                                    # NIVEL 2: Características Trello
                                    {
                                        "name": "Tableros y Organización",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "elementos": [
                                                "Tableros",
                                                "Listas",
                                                "Tarjetas",
                                                "Labels",
                                                "Due dates",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Automatización Trello",
                                        "type": FeatureType.OPTIONAL,
                                        "properties": {
                                            "caracteristicas": [
                                                "Butler automation",
                                                "Power-Ups",
                                                "Integraciones",
                                            ],
                                        },
                                    },
                                ],
                            },
                            {
                                "name": "Asana",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "tipo": "Gestión colaborativa",
                                    "horas": 8,
                                },
                                "children": [
                                    # NIVEL 2: Funciones Asana
                                    {
                                        "name": "Gestión de Tareas",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "funciones": [
                                                "Proyectos",
                                                "Tareas y subtareas",
                                                "Dependencias",
                                                "Hitos",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Vistas y Reportes",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "vistas": [
                                                "Lista",
                                                "Tablero",
                                                "Cronograma",
                                                "Calendario",
                                                "Portfolios",
                                            ],
                                        },
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        "name": "Proyecto Práctico",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Aplicación práctica de conceptos aprendidos",
                            "creditos": 1.0,
                            "horas": 16,
                            "peso_evaluacion": "30%",
                        },
                        "children": [
                            # NIVEL 2: Fases del proyecto
                            {
                                "name": "Iniciación del Proyecto",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 2,
                                    "entregables": [
                                        "Project Charter",
                                        "Identificación de stakeholders",
                                        "Objetivos SMART",
                                    ],
                                },
                            },
                            {
                                "name": "Planificación Detallada",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 6,
                                    "entregables": [
                                        "WBS completo",
                                        "Cronograma (Gantt)",
                                        "Estimaciones de esfuerzo",
                                        "Plan de recursos",
                                        "Presupuesto",
                                    ],
                                },
                            },
                            {
                                "name": "Gestión de Riesgos del Proyecto",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 3,
                                    "entregables": [
                                        "Registro de riesgos",
                                        "Análisis cualitativo",
                                        "Planes de respuesta",
                                    ],
                                },
                            },
                            {
                                "name": "Seguimiento con Herramienta",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 3,
                                    "actividades": [
                                        "Configurar proyecto en herramienta elegida",
                                        "Cargar tareas y cronograma",
                                        "Simular seguimiento semanal",
                                        "Generar reportes",
                                    ],
                                },
                            },
                            {
                                "name": "Presentación Final",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 2,
                                    "formato": "15-20 minutos + Q&A",
                                    "contenido": [
                                        "Resumen ejecutivo",
                                        "Planificación y estimaciones",
                                        "Gestión de riesgos",
                                        "Demostración de herramienta",
                                        "Lecciones aprendidas",
                                    ],
                                },
                            },
                        ],
                    },
                ],
            }
        ],
        # Relaciones entre features (fundamentos para futuras expansiones)
        "feature_relations": [
            # Relaciones de nivel 1
            {
                "source": "Planificación y Estimación",
                "target": "Fundamentos de Gestión de Proyectos",
                "type": "requires",
                "description": "La planificación requiere conocimientos fundamentales de gestión",
            },
            {
                "source": "Gestión de Equipos",
                "target": "Fundamentos de Gestión de Proyectos",
                "type": "requires",
                "description": "La gestión de equipos requiere fundamentos de proyectos",
            },
            {
                "source": "Gestión de Riesgos y Calidad",
                "target": "Planificación y Estimación",
                "type": "requires",
                "description": "La gestión de riesgos requiere habilidades de planificación",
            },
            {
                "source": "Metodologías Ágiles",
                "target": "Fundamentos de Gestión de Proyectos",
                "type": "requires",
                "description": "Las metodologías ágiles requieren comprensión de fundamentos",
            },
            {
                "source": "Scrum",
                "target": "Gestión de Equipos",
                "type": "requires",
                "description": "Scrum requiere conocimientos de gestión de equipos",
            },
            {
                "source": "Kanban",
                "target": "Gestión de Equipos",
                "type": "requires",
                "description": "Kanban requiere conocimientos de gestión de equipos",
            },
            {
                "source": "Proyecto Práctico",
                "target": "Planificación y Estimación",
                "type": "requires",
                "description": "El proyecto requiere habilidades de planificación",
            },
            {
                "source": "Proyecto Práctico",
                "target": "Gestión de Riesgos y Calidad",
                "type": "requires",
                "description": "El proyecto requiere conocimientos de riesgos y calidad",
            },
            {
                "source": "Proyecto Práctico",
                "target": "Metodologías Ágiles",
                "type": "requires",
                "description": "El proyecto debe aplicar al menos una metodología ágil",
            },
            {
                "source": "Proyecto Práctico",
                "target": "Herramientas de Gestión",
                "type": "requires",
                "description": "El proyecto debe usar al menos una herramienta de gestión",
            },
            # Relaciones de nivel 2 - Fundamentos
            {
                "source": "Marcos de Referencia",
                "target": "Introducción a Proyectos",
                "type": "requires",
                "description": "Los marcos de referencia requieren conocer la introducción a proyectos",
            },
            {
                "source": "Comparativa de Enfoques",
                "target": "Marcos de Referencia",
                "type": "requires",
                "description": "Comparar enfoques requiere conocer los marcos de referencia",
            },
            # Relaciones de nivel 2 - Planificación
            {
                "source": "Técnicas de Estimación",
                "target": "Descomposición del Trabajo",
                "type": "requires",
                "description": "La estimación requiere haber descompuesto el trabajo",
            },
            {
                "source": "Gestión del Cronograma",
                "target": "Técnicas de Estimación",
                "type": "requires",
                "description": "El cronograma requiere estimaciones previas",
            },
            # Relaciones de nivel 2 - Equipos
            {
                "source": "Liderazgo",
                "target": "Formación y Desarrollo",
                "type": "requires",
                "description": "El liderazgo efectivo requiere entender la formación de equipos",
            },
            {
                "source": "Gestión de Conflictos",
                "target": "Comunicación",
                "type": "requires",
                "description": "La gestión de conflictos requiere habilidades de comunicación",
            },
            # Relaciones de nivel 2 - Riesgos
            {
                "source": "Análisis de Riesgos",
                "target": "Identificación de Riesgos",
                "type": "requires",
                "description": "El análisis requiere haber identificado los riesgos primero",
            },
            {
                "source": "Respuesta a Riesgos",
                "target": "Análisis de Riesgos",
                "type": "requires",
                "description": "La respuesta requiere haber analizado los riesgos",
            },
            # Relaciones de nivel 2 - Scrum
            {
                "source": "Eventos Scrum",
                "target": "Roles Scrum",
                "type": "requires",
                "description": "Los eventos de Scrum requieren comprender los roles",
            },
            {
                "source": "Artefactos Scrum",
                "target": "Roles Scrum",
                "type": "requires",
                "description": "Los artefactos de Scrum requieren comprender los roles",
            },
            # Relaciones de nivel 2 - Kanban
            {
                "source": "Métricas Kanban",
                "target": "Principios Kanban",
                "type": "requires",
                "description": "Las métricas requieren comprender los principios de Kanban",
            },
            # Relaciones de nivel 2 - XP
            {
                "source": "Prácticas Técnicas XP",
                "target": "Valores y Principios XP",
                "type": "requires",
                "description": "Las prácticas técnicas se basan en los valores y principios",
            },
            # Relaciones de nivel 2 - Jira
            {
                "source": "Reportes Jira",
                "target": "Jira Software",
                "type": "requires",
                "description": "Los reportes requieren conocer Jira Software",
            },
            # Relaciones de nivel 2 - MS Project
            {
                "source": "Seguimiento y Control",
                "target": "Planificación en MS Project",
                "type": "requires",
                "description": "El seguimiento requiere haber planificado el proyecto",
            },
            # Relaciones de nivel 2 - Trello
            {
                "source": "Automatización Trello",
                "target": "Tableros y Organización",
                "type": "requires",
                "description": "La automatización requiere conocer los tableros básicos",
            },
            # Relaciones de nivel 2 - Asana
            {
                "source": "Vistas y Reportes",
                "target": "Gestión de Tareas",
                "type": "requires",
                "description": "Las vistas requieren tener tareas creadas",
            },
            # Relaciones de nivel 2 - Proyecto Práctico
            {
                "source": "Planificación Detallada",
                "target": "Iniciación del Proyecto",
                "type": "requires",
                "description": "La planificación detallada requiere haber iniciado el proyecto",
            },
            {
                "source": "Gestión de Riesgos del Proyecto",
                "target": "Planificación Detallada",
                "type": "requires",
                "description": "La gestión de riesgos requiere tener la planificación",
            },
            {
                "source": "Seguimiento con Herramienta",
                "target": "Planificación Detallada",
                "type": "requires",
                "description": "El seguimiento requiere tener el plan cargado",
            },
            {
                "source": "Presentación Final",
                "target": "Seguimiento con Herramienta",
                "type": "requires",
                "description": "La presentación incluye demostración de la herramienta",
            },
            # Relaciones de nivel 3 - Técnicas de Estimación
            {
                "source": "COCOMO II",
                "target": "Descomposición del Trabajo",
                "type": "requires",
                "description": "COCOMO requiere conocer la descomposición del trabajo",
            },
            {
                "source": "Puntos de Función (FPA)",
                "target": "Descomposición del Trabajo",
                "type": "requires",
                "description": "FPA requiere identificar componentes funcionales",
            },
            {
                "source": "Story Points",
                "target": "Planning Poker",
                "type": "requires",
                "description": "Story Points se estiman típicamente con Planning Poker",
            },
            {
                "source": "Estimación Algorítmica",
                "target": "Estimación Ágil",
                "type": "excludes",
                "description": "Son enfoques diferentes - tradicional vs ágil",
            },
            # Relaciones de nivel 3 - Liderazgo
            {
                "source": "Liderazgo Situacional",
                "target": "Teorías de Motivación",
                "type": "requires",
                "description": "El liderazgo situacional requiere entender la motivación",
            },
            {
                "source": "Servant Leadership",
                "target": "Inteligencia Emocional",
                "type": "requires",
                "description": "Servant leadership requiere alta inteligencia emocional",
            },
            {
                "source": "Liderazgo Transformacional",
                "target": "Liderazgo Situacional",
                "type": "excludes",
                "description": "Son estilos alternativos mutuamente excluyentes en el XOR",
            },
            # Relaciones de nivel 3 - Análisis de Riesgos
            {
                "source": "Análisis Cuantitativo",
                "target": "Análisis Cualitativo",
                "type": "requires",
                "description": "El análisis cuantitativo requiere primero el cualitativo",
            },
            {
                "source": "Análisis EMV (Expected Monetary Value)",
                "target": "Matriz de Probabilidad e Impacto",
                "type": "requires",
                "description": "EMV usa los valores de probabilidad e impacto",
            },
            {
                "source": "Árbol de Decisiones",
                "target": "Matriz de Probabilidad e Impacto",
                "type": "requires",
                "description": "Los árboles de decisión usan análisis cualitativo previo",
            },
            {
                "source": "Simulación Monte Carlo",
                "target": "Análisis EMV (Expected Monetary Value)",
                "type": "requires",
                "description": "Monte Carlo es una extensión avanzada del análisis EMV",
            },
            # Relaciones de nivel 3 - Scrum Roles
            {
                "source": "Product Owner",
                "target": "Estilos de Liderazgo",
                "type": "requires",
                "description": "El Product Owner necesita habilidades de liderazgo",
            },
            {
                "source": "Scrum Master",
                "target": "Servant Leadership",
                "type": "requires",
                "description": "El Scrum Master debe practicar Servant Leadership",
            },
            {
                "source": "Development Team",
                "target": "Formación y Desarrollo",
                "type": "requires",
                "description": "El equipo pasa por las fases de formación de Tuckman",
            },
            # Relaciones de nivel 3 - Scrum Eventos
            {
                "source": "Sprint Planning",
                "target": "Product Backlog",
                "type": "requires",
                "description": "Sprint Planning requiere un Product Backlog ordenado",
            },
            {
                "source": "Daily Scrum",
                "target": "Sprint Backlog",
                "type": "requires",
                "description": "Daily Scrum revisa el progreso del Sprint Backlog",
            },
            {
                "source": "Sprint Review",
                "target": "Increment",
                "type": "requires",
                "description": "Sprint Review presenta el Increment completado",
            },
            {
                "source": "Sprint Retrospective",
                "target": "Sprint Review",
                "type": "requires",
                "description": "La retrospectiva ocurre después de la review",
            },
            {
                "source": "Sprint",
                "target": "Sprint Planning",
                "type": "requires",
                "description": "Cada Sprint comienza con Sprint Planning",
            },
            # Relaciones de nivel 3 - Scrum Artefactos
            {
                "source": "Sprint Backlog",
                "target": "Product Backlog",
                "type": "requires",
                "description": "El Sprint Backlog se selecciona del Product Backlog",
            },
            {
                "source": "Increment",
                "target": "Sprint Backlog",
                "type": "requires",
                "description": "El Increment se crea completando items del Sprint Backlog",
            },
            {
                "source": "Increment",
                "target": "Definition of Done",
                "type": "requires",
                "description": "Todo Increment debe cumplir la Definition of Done",
            },
            {
                "source": "Definition of Done",
                "target": "Gestión de Calidad",
                "type": "requires",
                "description": "DoD está relacionada con estándares de calidad",
            },
        ],
    },
}

# Modelo 6: Asignatura Sistemas de Bases de Datos
asignatura_bases_datos_model = {
    "name": "Sistemas de Bases de Datos",
    "description": "Asignatura completa sobre diseño, implementación y administración de bases de datos relacionales y NoSQL (1 semestre, 6 créditos)",
    "domain_name": "Ingeniería Informática",
    "version": {
        "version_number": 1,
        "status": ModelStatus.PUBLISHED,
        "features": [
            {
                "name": "Sistemas de Bases de Datos",
                "type": FeatureType.MANDATORY,
                "properties": {
                    "description": "Asignatura completa de bases de datos",
                    "creditos": 6,
                    "semestre": 3,
                    "horas_totales": 96,
                    "horas_teoricas": 48,
                    "horas_practicas": 48,
                    "nivel": "pregrado",
                    "area": "ciencias de la computación",
                },
                "children": [
                    # NIVEL 1: Módulos principales de la asignatura
                    {
                        "name": "Fundamentos de Bases de Datos",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Conceptos básicos y arquitectura de SGBD",
                            "creditos": 1.0,
                            "horas": 16,
                            "temas": [
                                "Conceptos básicos de BD",
                                "Arquitectura ANSI/SPARC",
                                "Modelos de datos",
                                "Usuarios y roles en BD",
                                "ACID y transacciones",
                            ],
                        },
                    },
                    {
                        "name": "Modelo Relacional",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Teoría del modelo relacional y álgebra",
                            "creditos": 1.5,
                            "horas": 24,
                            "temas": [
                                "Estructuras: tablas, tuplas, atributos",
                                "Dominios y tipos de datos",
                                "Claves primarias y foráneas",
                                "Álgebra relacional",
                                "Cálculo relacional",
                                "Integridad referencial",
                            ],
                        },
                    },
                    {
                        "name": "Diseño de Bases de Datos",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Metodologías de diseño y normalización",
                            "creditos": 1.5,
                            "horas": 24,
                        },
                        "children": [
                            # NIVEL 2: Fases del diseño
                            {
                                "name": "Modelo Entidad-Relación (ER)",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 8,
                                    "temas": [
                                        "Entidades y atributos",
                                        "Relaciones y cardinalidad",
                                        "Atributos multivaluados y compuestos",
                                        "Entidades débiles",
                                        "Diagrama ER",
                                    ],
                                },
                            },
                            {
                                "name": "Modelo ER Extendido (EER)",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 6,
                                    "temas": [
                                        "Generalización y especialización",
                                        "Herencia",
                                        "Restricciones de disjunción",
                                        "Agregación",
                                    ],
                                },
                            },
                            {
                                "name": "Normalización",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 8,
                                    "temas": [
                                        "Dependencias funcionales",
                                        "Primera Forma Normal (1FN)",
                                        "Segunda Forma Normal (2FN)",
                                        "Tercera Forma Normal (3FN)",
                                        "Forma Normal de Boyce-Codd (BCNF)",
                                    ],
                                },
                            },
                            {
                                "name": "Mapeo ER a Relacional",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 2,
                                    "temas": [
                                        "Mapeo de entidades",
                                        "Mapeo de relaciones",
                                        "Mapeo de jerarquías",
                                    ],
                                },
                            },
                        ],
                    },
                    {
                        "name": "SQL - Lenguaje de Consulta",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "SQL estándar para manipulación de datos",
                            "creditos": 1.0,
                            "horas": 16,
                        },
                        "children": [
                            # NIVEL 2: Categorías de SQL
                            {
                                "name": "DDL - Definición de Datos",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 3,
                                    "comandos": [
                                        "CREATE TABLE",
                                        "ALTER TABLE",
                                        "DROP TABLE",
                                        "Constraints (PK, FK, UNIQUE, CHECK)",
                                    ],
                                },
                            },
                            {
                                "name": "DML - Manipulación de Datos",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 4,
                                    "comandos": [
                                        "INSERT INTO",
                                        "UPDATE",
                                        "DELETE",
                                        "Transacciones (COMMIT, ROLLBACK)",
                                    ],
                                },
                            },
                            {
                                "name": "DQL - Consultas Básicas",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 4,
                                    "comandos": [
                                        "SELECT",
                                        "WHERE y operadores",
                                        "ORDER BY",
                                        "DISTINCT",
                                        "LIMIT/TOP",
                                    ],
                                },
                            },
                            {
                                "name": "Consultas Avanzadas",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 5,
                                    "temas": [
                                        "JOINs (INNER, LEFT, RIGHT, FULL)",
                                        "Subconsultas",
                                        "Funciones agregadas (COUNT, SUM, AVG, MAX, MIN)",
                                        "GROUP BY y HAVING",
                                        "Vistas (CREATE VIEW)",
                                        "UNION, INTERSECT, EXCEPT",
                                    ],
                                },
                            },
                        ],
                    },
                    {
                        "name": "Sistemas Gestores de BD (SGBD)",
                        "type": FeatureType.OR_GROUP,
                        "properties": {
                            "description": "Elegir al menos un SGBD para profundizar",
                            "creditos": 0.5,
                            "horas": 8,
                            "minimo_selecciones": 1,
                        },
                        "children": [
                            {
                                "name": "PostgreSQL",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "tipo": "Relacional open-source",
                                    "horas": 8,
                                },
                                "children": [
                                    # NIVEL 2: Características de PostgreSQL
                                    {
                                        "name": "Instalación y Configuración",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "temas": [
                                                "Instalación en diferentes OS",
                                                "Configuración postgresql.conf",
                                                "pg_hba.conf para autenticación",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Características Avanzadas",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "temas": [
                                                "Tipos de datos avanzados (JSON, Array)",
                                                "Extensiones (PostGIS, pg_trgm)",
                                                "Full-text search",
                                                "Funciones y procedimientos (PL/pgSQL)",
                                            ],
                                        },
                                    },
                                ],
                            },
                            {
                                "name": "MySQL/MariaDB",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "tipo": "Relacional open-source",
                                    "horas": 8,
                                },
                                "children": [
                                    # NIVEL 2: Características de MySQL
                                    {
                                        "name": "Motores de Almacenamiento",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "tipos": [
                                                "InnoDB (transaccional)",
                                                "MyISAM (no transaccional)",
                                                "Memory",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Replicación y Alta Disponibilidad",
                                        "type": FeatureType.OPTIONAL,
                                        "properties": {
                                            "temas": [
                                                "Master-Slave replication",
                                                "Group Replication",
                                                "Galera Cluster (MariaDB)",
                                            ],
                                        },
                                    },
                                ],
                            },
                            {
                                "name": "Oracle Database",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "tipo": "Relacional empresarial",
                                    "horas": 8,
                                },
                                "children": [
                                    # NIVEL 2: Características de Oracle
                                    {
                                        "name": "PL/SQL",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "temas": [
                                                "Procedimientos almacenados",
                                                "Funciones",
                                                "Packages",
                                                "Triggers",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Características Empresariales",
                                        "type": FeatureType.OPTIONAL,
                                        "properties": {
                                            "temas": [
                                                "RAC (Real Application Clusters)",
                                                "Data Guard",
                                                "Particionamiento avanzado",
                                            ],
                                        },
                                    },
                                ],
                            },
                            {
                                "name": "Microsoft SQL Server",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "tipo": "Relacional empresarial",
                                    "horas": 8,
                                },
                                "children": [
                                    # NIVEL 2: Características de SQL Server
                                    {
                                        "name": "T-SQL",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "temas": [
                                                "Stored Procedures",
                                                "Functions",
                                                "Common Table Expressions (CTE)",
                                                "Window Functions",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Integración y BI",
                                        "type": FeatureType.OPTIONAL,
                                        "properties": {
                                            "herramientas": [
                                                "SQL Server Integration Services (SSIS)",
                                                "SQL Server Reporting Services (SSRS)",
                                                "SQL Server Analysis Services (SSAS)",
                                            ],
                                        },
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        "name": "Transacciones y Concurrencia",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Control de concurrencia y recuperación",
                            "creditos": 0.5,
                            "horas": 8,
                        },
                        "children": [
                            # NIVEL 2: Aspectos de transacciones
                            {
                                "name": "Propiedades ACID",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 2,
                                    "propiedades": [
                                        "Atomicity (Atomicidad)",
                                        "Consistency (Consistencia)",
                                        "Isolation (Aislamiento)",
                                        "Durability (Durabilidad)",
                                    ],
                                },
                            },
                            {
                                "name": "Niveles de Aislamiento",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 3,
                                    "niveles": [
                                        "Read Uncommitted",
                                        "Read Committed",
                                        "Repeatable Read",
                                        "Serializable",
                                    ],
                                    "problemas": [
                                        "Dirty Read",
                                        "Non-repeatable Read",
                                        "Phantom Read",
                                    ],
                                },
                            },
                            {
                                "name": "Control de Concurrencia",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 3,
                                    "tecnicas": [
                                        "Bloqueos (locks)",
                                        "Two-Phase Locking (2PL)",
                                        "Timestamp Ordering",
                                        "Optimistic Concurrency Control",
                                        "Detección de deadlocks",
                                    ],
                                },
                            },
                        ],
                    },
                    {
                        "name": "Bases de Datos NoSQL",
                        "type": FeatureType.OR_GROUP,
                        "properties": {
                            "description": "Elegir al menos un tipo de BD NoSQL",
                            "creditos": 0.5,
                            "horas": 8,
                            "minimo_selecciones": 1,
                        },
                        "children": [
                            {
                                "name": "Bases de Datos Documentales",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "ejemplo": "MongoDB, CouchDB",
                                    "horas": 8,
                                },
                                "children": [
                                    # NIVEL 2: MongoDB específico
                                    {
                                        "name": "Operaciones CRUD en MongoDB",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "operaciones": [
                                                "insertOne/insertMany",
                                                "find con query operators",
                                                "updateOne/updateMany",
                                                "deleteOne/deleteMany",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Agregaciones y Pipeline",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "stages": [
                                                "$match",
                                                "$group",
                                                "$project",
                                                "$sort",
                                                "$lookup (joins)",
                                            ],
                                        },
                                    },
                                ],
                            },
                            {
                                "name": "Bases de Datos Clave-Valor",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "ejemplo": "Redis, DynamoDB",
                                    "horas": 8,
                                },
                                "children": [
                                    # NIVEL 2: Redis específico
                                    {
                                        "name": "Estructuras de Datos Redis",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "tipos": [
                                                "Strings",
                                                "Hashes",
                                                "Lists",
                                                "Sets",
                                                "Sorted Sets",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Casos de Uso Redis",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "usos": [
                                                "Caché de sesiones",
                                                "Rate limiting",
                                                "Pub/Sub messaging",
                                                "Leaderboards",
                                            ],
                                        },
                                    },
                                ],
                            },
                            {
                                "name": "Bases de Datos en Grafo",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "ejemplo": "Neo4j, ArangoDB",
                                    "horas": 8,
                                },
                                "children": [
                                    # NIVEL 2: Neo4j específico
                                    {
                                        "name": "Modelo de Grafo",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "elementos": [
                                                "Nodos (Nodes)",
                                                "Relaciones (Relationships)",
                                                "Propiedades",
                                                "Labels",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "Cypher Query Language",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "comandos": [
                                                "CREATE nodes y relationships",
                                                "MATCH patterns",
                                                "WHERE filters",
                                                "RETURN results",
                                            ],
                                        },
                                    },
                                ],
                            },
                            {
                                "name": "Bases de Datos Columnares",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "ejemplo": "Cassandra, HBase",
                                    "horas": 8,
                                },
                                "children": [
                                    # NIVEL 2: Cassandra específico
                                    {
                                        "name": "Modelo de Datos Cassandra",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "conceptos": [
                                                "Keyspace",
                                                "Column Family/Table",
                                                "Partition Key",
                                                "Clustering Key",
                                            ],
                                        },
                                    },
                                    {
                                        "name": "CQL - Cassandra Query Language",
                                        "type": FeatureType.MANDATORY,
                                        "properties": {
                                            "comandos": [
                                                "CREATE KEYSPACE",
                                                "CREATE TABLE",
                                                "INSERT/SELECT",
                                                "Consistency Levels",
                                            ],
                                        },
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        "name": "Optimización y Rendimiento",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Técnicas de optimización de consultas",
                            "creditos": 0.5,
                            "horas": 8,
                            "temas": [
                                "Índices (B-tree, Hash, Bitmap)",
                                "Planes de ejecución",
                                "Estadísticas y optimizador",
                                "Query tuning",
                                "Particionamiento",
                                "Caché y buffers",
                            ],
                        },
                    },
                    {
                        "name": "Seguridad en Bases de Datos",
                        "type": FeatureType.OPTIONAL,
                        "properties": {
                            "description": "Seguridad y control de acceso",
                            "creditos": 0.25,
                            "horas": 4,
                            "temas": [
                                "Autenticación y autorización",
                                "Roles y privilegios",
                                "SQL Injection y prevención",
                                "Cifrado de datos",
                                "Auditoría",
                            ],
                        },
                    },
                    {
                        "name": "Proyecto Final",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Proyecto integrador de diseño e implementación",
                            "creditos": 0.75,
                            "horas": 12,
                            "peso_evaluacion": "25%",
                            "entregables": [
                                "Modelo Entidad-Relación",
                                "Esquema relacional normalizado",
                                "Scripts de creación (DDL)",
                                "Scripts de carga de datos (DML)",
                                "Consultas SQL complejas",
                                "Documentación técnica",
                            ],
                        },
                    },
                ],
            }
        ],
        # Relaciones entre features
        "feature_relations": [
            # Relaciones de prerequisitos
            {
                "source": "Modelo Relacional",
                "target": "Fundamentos de Bases de Datos",
                "type": "requires",
                "description": "El modelo relacional requiere entender fundamentos de BD",
            },
            {
                "source": "Diseño de Bases de Datos",
                "target": "Modelo Relacional",
                "type": "requires",
                "description": "El diseño requiere conocer el modelo relacional",
            },
            {
                "source": "SQL - Lenguaje de Consulta",
                "target": "Modelo Relacional",
                "type": "requires",
                "description": "SQL opera sobre el modelo relacional",
            },
            {
                "source": "Sistemas Gestores de BD (SGBD)",
                "target": "SQL - Lenguaje de Consulta",
                "type": "requires",
                "description": "Usar un SGBD requiere conocer SQL",
            },
            {
                "source": "Transacciones y Concurrencia",
                "target": "Fundamentos de Bases de Datos",
                "type": "requires",
                "description": "Transacciones requieren entender propiedades ACID de fundamentos",
            },
            {
                "source": "Optimización y Rendimiento",
                "target": "SQL - Lenguaje de Consulta",
                "type": "requires",
                "description": "Optimizar requiere conocer SQL y consultas",
            },
            {
                "source": "Seguridad en Bases de Datos",
                "target": "Sistemas Gestores de BD (SGBD)",
                "type": "requires",
                "description": "Implementar seguridad requiere conocer un SGBD",
            },
            {
                "source": "Proyecto Final",
                "target": "Diseño de Bases de Datos",
                "type": "requires",
                "description": "El proyecto requiere saber diseñar BD",
            },
            {
                "source": "Proyecto Final",
                "target": "SQL - Lenguaje de Consulta",
                "type": "requires",
                "description": "El proyecto requiere dominar SQL",
            },
            {
                "source": "Proyecto Final",
                "target": "Sistemas Gestores de BD (SGBD)",
                "type": "requires",
                "description": "El proyecto debe implementarse en un SGBD",
            },
            # Relaciones de exclusión entre SGBD relacionales
            {
                "source": "PostgreSQL",
                "target": "Oracle Database",
                "type": "excludes",
                "description": "En el curso se profundiza en un SGBD principal",
            },
            {
                "source": "MySQL/MariaDB",
                "target": "Microsoft SQL Server",
                "type": "excludes",
                "description": "En el curso se profundiza en un SGBD principal",
            },
            # Relaciones entre NoSQL y fundamentos
            {
                "source": "Bases de Datos NoSQL",
                "target": "Fundamentos de Bases de Datos",
                "type": "requires",
                "description": "NoSQL requiere entender conceptos generales de BD",
            },
            {
                "source": "Bases de Datos Documentales",
                "target": "Modelo Relacional",
                "type": "requires",
                "description": "Entender NoSQL requiere contrastar con modelo relacional",
            },
            # Relaciones de nivel 2 - Diseño de BD
            {
                "source": "Modelo ER Extendido (EER)",
                "target": "Modelo Entidad-Relación (ER)",
                "type": "requires",
                "description": "EER es una extensión del modelo ER básico",
            },
            {
                "source": "Normalización",
                "target": "Modelo Entidad-Relación (ER)",
                "type": "requires",
                "description": "Normalización se aplica después del diseño ER",
            },
            {
                "source": "Mapeo ER a Relacional",
                "target": "Normalización",
                "type": "requires",
                "description": "El mapeo debe hacerse sobre esquemas normalizados",
            },
            # Relaciones de nivel 2 - SQL
            {
                "source": "DML - Manipulación de Datos",
                "target": "DDL - Definición de Datos",
                "type": "requires",
                "description": "DML requiere que las tablas estén definidas con DDL",
            },
            {
                "source": "DQL - Consultas Básicas",
                "target": "DDL - Definición de Datos",
                "type": "requires",
                "description": "Las consultas requieren que existan tablas definidas",
            },
            {
                "source": "Consultas Avanzadas",
                "target": "DQL - Consultas Básicas",
                "type": "requires",
                "description": "Consultas avanzadas requieren dominar consultas básicas",
            },
            # Relaciones de nivel 2 - SGBD
            {
                "source": "Características Avanzadas",
                "target": "Instalación y Configuración",
                "type": "requires",
                "description": "Características avanzadas requieren instalación previa",
            },
            {
                "source": "Replicación y Alta Disponibilidad",
                "target": "Motores de Almacenamiento",
                "type": "requires",
                "description": "HA requiere entender los motores de almacenamiento",
            },
            {
                "source": "Características Empresariales",
                "target": "PL/SQL",
                "type": "requires",
                "description": "Características empresariales de Oracle requieren PL/SQL",
            },
            {
                "source": "Integración y BI",
                "target": "T-SQL",
                "type": "requires",
                "description": "BI en SQL Server requiere dominar T-SQL",
            },
            # Relaciones de nivel 2 - Transacciones
            {
                "source": "Niveles de Aislamiento",
                "target": "Propiedades ACID",
                "type": "requires",
                "description": "Niveles de aislamiento implementan la 'I' de ACID",
            },
            {
                "source": "Control de Concurrencia",
                "target": "Niveles de Aislamiento",
                "type": "requires",
                "description": "Control de concurrencia implementa los niveles de aislamiento",
            },
            # Relaciones de nivel 2 - NoSQL
            {
                "source": "Agregaciones y Pipeline",
                "target": "Operaciones CRUD en MongoDB",
                "type": "requires",
                "description": "Agregaciones requieren dominar CRUD básico",
            },
            {
                "source": "Casos de Uso Redis",
                "target": "Estructuras de Datos Redis",
                "type": "requires",
                "description": "Implementar casos de uso requiere conocer estructuras de datos",
            },
            {
                "source": "Cypher Query Language",
                "target": "Modelo de Grafo",
                "type": "requires",
                "description": "Cypher opera sobre el modelo de grafo",
            },
            {
                "source": "CQL - Cassandra Query Language",
                "target": "Modelo de Datos Cassandra",
                "type": "requires",
                "description": "CQL opera sobre el modelo de datos de Cassandra",
            },
        ],
    },
}

# Modelo 7: Asignatura Estructura de Datos I
asignatura_estructura_datos_model = {
    "name": "Estructura de Datos I",
    "description": "Asignatura fundamental sobre estructuras de datos lineales y no lineales básicas, algoritmos de búsqueda y ordenamiento (1 semestre, 6 créditos)",
    "domain_name": "Ingeniería Informática",
    "version": {
        "version_number": 1,
        "status": ModelStatus.PUBLISHED,
        "features": [
            {
                "name": "Estructura de Datos I",
                "type": FeatureType.MANDATORY,
                "properties": {
                    "description": "Asignatura completa de estructuras de datos básicas",
                    "creditos": 6,
                    "semestre": 2,
                    "horas_totales": 96,
                    "horas_teoricas": 48,
                    "horas_practicas": 48,
                    "nivel": "pregrado",
                    "area": "ciencias de la computación",
                },
                "children": [
                    # NIVEL 1: Módulos principales de la asignatura
                    {
                        "name": "Fundamentos y Análisis de Algoritmos",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Conceptos básicos y análisis de complejidad",
                            "creditos": 1.0,
                            "horas": 16,
                            "temas": [
                                "Tipos de datos abstractos (TDA)",
                                "Notación Big-O, Omega, Theta",
                                "Análisis de tiempo y espacio",
                                "Recursión vs iteración",
                                "Complejidad temporal y espacial",
                            ],
                        },
                    },
                    {
                        "name": "Estructuras Lineales Básicas",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Arreglos, listas y estructuras secuenciales",
                            "creditos": 1.5,
                            "horas": 24,
                        },
                        "children": [
                            # NIVEL 2: Tipos de estructuras lineales
                            {
                                "name": "Arreglos",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 6,
                                    "temas": [
                                        "Arreglos estáticos",
                                        "Arreglos dinámicos (vectores)",
                                        "Arreglos multidimensionales",
                                        "Complejidad de operaciones O(1) acceso, O(n) inserción/eliminación",
                                    ],
                                },
                            },
                            {
                                "name": "Listas Enlazadas Simples",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 6,
                                    "temas": [
                                        "Nodo: dato + puntero",
                                        "Inserción al inicio O(1)",
                                        "Inserción al final O(n)",
                                        "Eliminación",
                                        "Búsqueda O(n)",
                                    ],
                                },
                            },
                            {
                                "name": "Listas Doblemente Enlazadas",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 6,
                                    "temas": [
                                        "Nodo: dato + anterior + siguiente",
                                        "Navegación bidireccional",
                                        "Inserción/eliminación eficiente",
                                    ],
                                },
                            },
                            {
                                "name": "Listas Circulares",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "horas": 6,
                                    "temas": [
                                        "Último nodo apunta al primero",
                                        "Aplicaciones: buffer circular, round-robin",
                                    ],
                                },
                            },
                        ],
                    },
                    {
                        "name": "Pilas (Stacks)",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Estructura LIFO y sus aplicaciones",
                            "creditos": 0.5,
                            "horas": 8,
                        },
                        "children": [
                            # NIVEL 2: Implementaciones y aplicaciones de pilas
                            {
                                "name": "Implementación con Arreglos",
                                "type": FeatureType.ALTERNATIVE,
                                "properties": {
                                    "horas": 3,
                                    "temas": [
                                        "Pila con tamaño fijo",
                                        "Operaciones: push O(1), pop O(1), top O(1)",
                                        "Control de overflow/underflow",
                                    ],
                                },
                            },
                            {
                                "name": "Implementación con Listas Enlazadas",
                                "type": FeatureType.ALTERNATIVE,
                                "properties": {
                                    "horas": 3,
                                    "temas": [
                                        "Pila dinámica sin límite de tamaño",
                                        "Push/pop al inicio de la lista",
                                        "Gestión de memoria",
                                    ],
                                },
                            },
                            {
                                "name": "Aplicaciones de Pilas",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 2,
                                    "temas": [
                                        "Evaluación de expresiones",
                                        "Conversión infija/postfija/prefija",
                                        "Balanceo de paréntesis",
                                        "Recursión y pila de llamadas",
                                        "Backtracking",
                                    ],
                                },
                            },
                        ],
                    },
                    {
                        "name": "Colas (Queues)",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Estructura FIFO y variantes",
                            "creditos": 0.5,
                            "horas": 8,
                        },
                        "children": [
                            # NIVEL 2: Tipos de colas y sus implementaciones
                            {
                                "name": "Cola Simple (FIFO)",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 3,
                                    "temas": [
                                        "Principio FIFO (First In, First Out)",
                                        "Operaciones: enqueue O(1), dequeue O(1)",
                                        "Implementación circular con arreglos",
                                        "Implementación con listas enlazadas",
                                    ],
                                },
                            },
                            {
                                "name": "Cola de Prioridad",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 3,
                                    "temas": [
                                        "Elementos con prioridad",
                                        "Dequeue extrae elemento de mayor prioridad",
                                        "Implementación con heap",
                                        "Aplicaciones: scheduling, algoritmos de grafos",
                                    ],
                                },
                            },
                            {
                                "name": "Deque (Double-Ended Queue)",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "horas": 2,
                                    "temas": [
                                        "Inserción/eliminación en ambos extremos",
                                        "Operaciones: addFront, addRear, removeFront, removeRear",
                                        "Aplicaciones: palindromo, sliding window",
                                    ],
                                },
                            },
                        ],
                    },
                    {
                        "name": "Árboles Binarios",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Estructuras jerárquicas básicas",
                            "creditos": 1.0,
                            "horas": 16,
                        },
                        "children": [
                            # NIVEL 2: Conceptos y tipos de árboles binarios
                            {
                                "name": "Conceptos Fundamentales",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 4,
                                    "temas": [
                                        "Terminología: nodo, raíz, hoja, padre, hijo",
                                        "Altura, profundidad, nivel",
                                        "Árbol completo vs árbol lleno",
                                        "Representación: hijos izquierdo/derecho",
                                    ],
                                },
                            },
                            {
                                "name": "Recorridos de Árboles",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 4,
                                    "temas": [
                                        "Preorden (raíz-izq-der)",
                                        "Inorden (izq-raíz-der)",
                                        "Postorden (izq-der-raíz)",
                                        "Por niveles (BFS)",
                                        "Implementación recursiva vs iterativa",
                                    ],
                                },
                            },
                            {
                                "name": "Árbol Binario de Búsqueda (BST)",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 6,
                                    "temas": [
                                        "Propiedad BST: izq < raíz < der",
                                        "Búsqueda O(log n) promedio, O(n) peor caso",
                                        "Inserción recursiva",
                                        "Eliminación: 3 casos (hoja, 1 hijo, 2 hijos)",
                                        "Sucesor/predecesor inorden",
                                    ],
                                },
                            },
                            {
                                "name": "Aplicaciones de Árboles",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "horas": 2,
                                    "temas": [
                                        "Árboles de expresión",
                                        "Árboles de decisión",
                                        "Estructuras de directorios",
                                    ],
                                },
                            },
                        ],
                    },
                    {
                        "name": "Algoritmos de Ordenamiento",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Algoritmos clásicos de ordenamiento",
                            "creditos": 1.0,
                            "horas": 16,
                        },
                        "children": [
                            # NIVEL 2: Clasificación de algoritmos de ordenamiento
                            {
                                "name": "Algoritmos Cuadráticos",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 6,
                                    "complejidad": "O(n²)",
                                    "temas": [
                                        "Bubble Sort: intercambios consecutivos",
                                        "Selection Sort: selección del mínimo",
                                        "Insertion Sort: inserción en posición ordenada",
                                        "Análisis de casos: mejor, promedio, peor",
                                    ],
                                },
                            },
                            {
                                "name": "Algoritmos Eficientes",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 8,
                                    "complejidad": "O(n log n)",
                                    "temas": [
                                        "Merge Sort: divide y conquista, estable",
                                        "Quick Sort: partición, in-place",
                                        "Heap Sort: usando heap binario",
                                        "Comparación de estabilidad y uso de memoria",
                                    ],
                                },
                            },
                            {
                                "name": "Análisis Comparativo",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 2,
                                    "temas": [
                                        "Criterios: tiempo, espacio, estabilidad",
                                        "Cuándo usar cada algoritmo",
                                        "Límite inferior para ordenamiento basado en comparaciones",
                                    ],
                                },
                            },
                        ],
                    },
                    {
                        "name": "Algoritmos de Búsqueda",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Técnicas de búsqueda en estructuras",
                            "creditos": 0.5,
                            "horas": 8,
                        },
                        "children": [
                            # NIVEL 2: Tipos de búsqueda
                            {
                                "name": "Búsqueda Lineal",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 2,
                                    "complejidad": "O(n)",
                                    "temas": [
                                        "Búsqueda secuencial",
                                        "Búsqueda con centinela",
                                        "Útil en datos no ordenados",
                                    ],
                                },
                            },
                            {
                                "name": "Búsqueda Binaria",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 4,
                                    "complejidad": "O(log n)",
                                    "temas": [
                                        "Requisito: arreglo ordenado",
                                        "División del espacio de búsqueda",
                                        "Implementación iterativa y recursiva",
                                        "Variantes: lower_bound, upper_bound",
                                    ],
                                },
                            },
                            {
                                "name": "Búsqueda en Estructuras Avanzadas",
                                "type": FeatureType.MANDATORY,
                                "properties": {
                                    "horas": 2,
                                    "temas": [
                                        "Búsqueda en BST: O(log n) promedio",
                                        "Búsqueda en tablas hash: O(1) promedio",
                                        "Comparación de eficiencia",
                                    ],
                                },
                            },
                        ],
                    },
                    {
                        "name": "Lenguaje de Implementación",
                        "type": FeatureType.XOR_GROUP,
                        "properties": {
                            "description": "Elegir un lenguaje principal para implementar",
                            "creditos": 0.0,
                            "horas": 0,
                        },
                        "children": [
                            {
                                "name": "C/C++",
                                "type": FeatureType.ALTERNATIVE,
                                "properties": {
                                    "ventajas": [
                                        "Gestión manual de memoria",
                                        "Punteros explícitos",
                                        "Alto rendimiento",
                                        "STL (C++)",
                                    ],
                                },
                            },
                            {
                                "name": "Java",
                                "type": FeatureType.ALTERNATIVE,
                                "properties": {
                                    "ventajas": [
                                        "Orientado a objetos puro",
                                        "Garbage collection",
                                        "Collections Framework",
                                        "Portable",
                                    ],
                                },
                            },
                            {
                                "name": "Python",
                                "type": FeatureType.ALTERNATIVE,
                                "properties": {
                                    "ventajas": [
                                        "Sintaxis simple",
                                        "Tipado dinámico",
                                        "Estructuras built-in ricas",
                                        "Rápido prototipado",
                                    ],
                                },
                            },
                        ],
                    },
                    {
                        "name": "Técnicas de Programación",
                        "type": FeatureType.OR_GROUP,
                        "properties": {
                            "description": "Elegir al menos una técnica avanzada",
                            "creditos": 0.5,
                            "horas": 8,
                            "minimo_selecciones": 1,
                        },
                        "children": [
                            {
                                "name": "Recursión Avanzada",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "temas": [
                                        "Recursión múltiple",
                                        "Backtracking",
                                        "Divide y conquista",
                                        "Torres de Hanoi",
                                    ],
                                },
                            },
                            {
                                "name": "Programación Genérica",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "temas": [
                                        "Templates (C++)",
                                        "Generics (Java)",
                                        "Type hints (Python)",
                                        "Reutilización de código",
                                    ],
                                },
                            },
                            {
                                "name": "Manejo de Memoria",
                                "type": FeatureType.OPTIONAL,
                                "properties": {
                                    "temas": [
                                        "Asignación dinámica",
                                        "Liberación de memoria",
                                        "Memory leaks",
                                        "Smart pointers",
                                    ],
                                },
                            },
                        ],
                    },
                    {
                        "name": "Proyecto Final",
                        "type": FeatureType.MANDATORY,
                        "properties": {
                            "description": "Implementación de múltiples estructuras",
                            "creditos": 0.5,
                            "horas": 8,
                            "peso_evaluacion": "20%",
                            "entregables": [
                                "Biblioteca de estructuras de datos",
                                "Implementación de al menos 5 estructuras",
                                "Tests unitarios",
                                "Documentación del código",
                                "Análisis de complejidad",
                            ],
                        },
                    },
                ],
            }
        ],
        # Relaciones entre features
        "feature_relations": [
            # Relaciones de prerequisitos básicos
            {
                "source": "Estructuras Lineales Básicas",
                "target": "Fundamentos y Análisis de Algoritmos",
                "type": "requires",
                "description": "Las estructuras requieren entender TDA y complejidad",
            },
            {
                "source": "Pilas (Stacks)",
                "target": "Estructuras Lineales Básicas",
                "type": "requires",
                "description": "Pilas se implementan sobre listas o arreglos",
            },
            {
                "source": "Colas (Queues)",
                "target": "Estructuras Lineales Básicas",
                "type": "requires",
                "description": "Colas se implementan sobre listas o arreglos",
            },
            {
                "source": "Árboles Binarios",
                "target": "Estructuras Lineales Básicas",
                "type": "requires",
                "description": "Árboles requieren entender nodos y enlaces",
            },
            {
                "source": "Algoritmos de Ordenamiento",
                "target": "Fundamentos y Análisis de Algoritmos",
                "type": "requires",
                "description": "Ordenamiento requiere análisis de complejidad",
            },
            {
                "source": "Algoritmos de Búsqueda",
                "target": "Fundamentos y Análisis de Algoritmos",
                "type": "requires",
                "description": "Búsqueda requiere entender complejidad",
            },
            {
                "source": "Algoritmos de Búsqueda",
                "target": "Árboles Binarios",
                "type": "requires",
                "description": "Búsqueda en BST requiere entender árboles",
            },
            # Relaciones con técnicas de programación
            {
                "source": "Recursión Avanzada",
                "target": "Fundamentos y Análisis de Algoritmos",
                "type": "requires",
                "description": "Recursión avanzada requiere entender recursión básica",
            },
            {
                "source": "Recursión Avanzada",
                "target": "Árboles Binarios",
                "type": "requires",
                "description": "Árboles son ideales para practicar recursión",
            },
            {
                "source": "Manejo de Memoria",
                "target": "Estructuras Lineales Básicas",
                "type": "requires",
                "description": "Gestión de memoria es crítica en listas enlazadas",
            },
            # Relaciones de exclusión entre lenguajes
            {
                "source": "C/C++",
                "target": "Java",
                "type": "excludes",
                "description": "Se elige un lenguaje principal para la asignatura",
            },
            {
                "source": "Java",
                "target": "Python",
                "type": "excludes",
                "description": "Se elige un lenguaje principal para la asignatura",
            },
            {
                "source": "C/C++",
                "target": "Python",
                "type": "excludes",
                "description": "Se elige un lenguaje principal para la asignatura",
            },
            # Relaciones del proyecto final
            {
                "source": "Proyecto Final",
                "target": "Estructuras Lineales Básicas",
                "type": "requires",
                "description": "El proyecto debe incluir estructuras lineales",
            },
            {
                "source": "Proyecto Final",
                "target": "Pilas (Stacks)",
                "type": "requires",
                "description": "El proyecto debe incluir pilas",
            },
            {
                "source": "Proyecto Final",
                "target": "Colas (Queues)",
                "type": "requires",
                "description": "El proyecto debe incluir colas",
            },
            {
                "source": "Proyecto Final",
                "target": "Árboles Binarios",
                "type": "requires",
                "description": "El proyecto debe incluir árboles",
            },
            {
                "source": "Proyecto Final",
                "target": "Lenguaje de Implementación",
                "type": "requires",
                "description": "El proyecto se implementa en el lenguaje elegido",
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
    asignatura_gpi_model,
    asignatura_bases_datos_model,
    asignatura_estructura_datos_model,
]
