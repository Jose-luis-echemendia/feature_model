# 📦 Sistema Centralizado de Seeding - Datos Educativos

Este módulo contiene todo el sistema de poblado de base de datos (database seeding) organizado de manera modular y mantenible, con datos específicos para el sector educativo y la gestión curricular.

## 📁 Estructura

```
backend/app/seed/
├── __init__.py           # Exportaciones del módulo
├── main.py               # Orquestador principal
├── seeders.py            # Funciones de seeding
├── data_settings.py      # Datos de configuración de la app
├── data_users.py         # Datos de usuarios (producción + desarrollo)
├── data_models.py        # Datos de planes de estudio, dominios académicos, recursos educativos
└── README.md             # Este archivo
```

## 🎯 Modos de Seeding

### Producción

Solo crea datos esenciales:

- ✅ Configuraciones de aplicación educativa (`AppSettings`)
- ✅ FIRST_SUPERUSER desde variables de entorno
- ✅ Usuarios de producción (coordinadores, diseñadores curriculares)

```python
from app.seed import seed_production
seed_production(session)
```

### Desarrollo

Crea todos los datos de ejemplo para el contexto educativo:

- ✅ Usuarios de desarrollo con roles académicos
- ✅ Dominios académicos (Ingeniería Informática, Ciencias Básicas, etc.)
- ✅ Etiquetas pedagógicas (fundamentos, avanzado, práctico, etc.)
- ✅ Recursos educativos (videos, PDFs, laboratorios)
- ✅ Planes de estudio de ejemplo (Ingeniería, Cursos Full Stack)

```python
from app.seed import seed_development
seed_development(session)
```

### Automático (Recomendado)

Detecta el entorno automáticamente desde la variable `ENVIRONMENT`:

```python
from app.seed import seed_all
seed_all()  # Lee ENVIRONMENT de .env
```

## 🚀 Uso

### Desde línea de comandos

```bash
# Usando el módulo centralizado (recomendado)
python -m app.seed.main

# Usando el wrapper de compatibilidad
python -m app.seed_data
```

### Desde código

```python
from sqlmodel import Session
from app.core.db import engine
from app.seed import seed_all, seed_development, seed_production

with Session(engine) as session:
    # Opción 1: Automático según ENVIRONMENT
    seed_all()

    # Opción 2: Modo específico
    seed_development(session)

    # Opción 3: Solo producción
    seed_production(session)
```

### Desde Docker

```bash
# Ejecutar seeding en contenedor de desarrollo
docker-compose -f docker-compose.dev.yml exec backend python -m app.seed.main

# Ejecutar seeding específico
docker-compose -f docker-compose.dev.yml exec backend python -c "
from app.seed import seed_development
from sqlmodel import Session
from app.core.db import engine
with Session(engine) as session:
    seed_development(session)
"
```

## 📋 Funciones Disponibles

### Funciones Principales

| Función                     | Descripción                            | Uso                         |
| --------------------------- | -------------------------------------- | --------------------------- |
| `seed_all(environment)`     | Ejecuta seeding completo según entorno | `seed_all('local')`         |
| `seed_production(session)`  | Solo datos esenciales                  | `seed_production(session)`  |
| `seed_development(session)` | Datos completos de ejemplo             | `seed_development(session)` |

### Funciones Específicas

| Función                                                   | Descripción                            |
| --------------------------------------------------------- | -------------------------------------- |
| `seed_settings(session)`                                  | Configuraciones de la aplicación       |
| `seed_production_users(session)`                          | Usuarios de producción                 |
| `seed_development_users(session)`                         | Usuarios de desarrollo con contraseñas |
| `seed_domains(session, owner)`                            | Dominios de ejemplo                    |
| `seed_tags(session, owner)`                               | Tags del sistema                       |
| `seed_resources(session, owner)`                          | Recursos educativos                    |
| `seed_feature_models(session, owner, domains, resources)` | Modelos de características             |

## 📊 Datos Incluidos - Contexto Educativo

### 👥 Usuarios de Desarrollo

| Email                               | Password      | Rol            | Descripción                      |
| ----------------------------------- | ------------- | -------------- | -------------------------------- |
| `admin@example.com`                 | `admin123`    | ADMIN          | Administrador del sistema        |
| `diseñador.curricular@example.com`  | `designer123` | MODEL_DESIGNER | Diseñador de planes curriculares |
| `coordinador.academico@example.com` | `editor123`   | MODEL_EDITOR   | Coordinador académico            |
| `jefe.carrera@example.com`          | `config123`   | CONFIGURATOR   | Jefe de carrera o programa       |
| `profesor@example.com`              | `viewer123`   | VIEWER         | Profesor con acceso de lectura   |
| `evaluador.curricular@example.com`  | `reviewer123` | REVIEWER       | Evaluador de diseño curricular   |

### 👥 Usuarios de Producción

Los usuarios de producción se crean con contraseña temporal `ChangeMe123!` que debe cambiarse:

- `echemendiajoseluis@gmail.com` (ADMIN) - Administrador principal
- `yadira.rodriguez@uci.cu` (MODEL_DESIGNER) - Diseñadora curricular
- `liany.sobrino@uci.cu` (MODEL_DESIGNER) - Diseñadora curricular
- `ernesto.valdes@estudiantes.uci.cu` (MODEL_EDITOR) - Editor de modelos
- `coord.academica@uci.cu` (CONFIGURATOR) - Coordinadora académica
- `jefe.departamento@uci.cu` (REVIEWER) - Jefe de departamento

### 🎓 Dominios Académicos

1. **Ingeniería Informática** - Programas y planes de estudio para carreras de ingeniería en ciencias informáticas
2. **Ciencias Básicas** - Cursos de matemáticas, física y química para programas de ingeniería
3. **Formación General** - Cursos de humanidades, idiomas y formación integral
4. **Desarrollo de Software** - Programas especializados en ingeniería de software
5. **Ciencia de Datos** - Planes de estudio para ciencia de datos, IA y machine learning
6. **Seguridad Informática** - Programas de ciberseguridad

### 🏷️ Etiquetas Pedagógicas

- `fundamentos` - Cursos fundamentales y de introducción
- `avanzado` - Contenido de nivel avanzado
- `práctico` - Enfoque práctico con laboratorios y proyectos
- `teórico` - Contenido teórico y conceptual
- `obligatorio` - Asignatura obligatoria del plan
- `electivo` - Asignatura electiva u optativa
- `proyecto` - Curso basado en proyectos
- `certificacion` - Preparación para certificaciones profesionales
- `investigacion` - Componente de investigación
- `practica_profesional` - Prácticas profesionales o pasantías

### 📚 Recursos Educativos

1. **Introducción a Feature Models en Educación** (VIDEO, 20 min)
   - Tutorial sobre modelado de planes de estudio
2. **Guía de Diseño Curricular con Feature Models** (PDF)
   - Metodología completa de diseño curricular
3. **Programación Orientada a Objetos - Conceptos Fundamentales** (VIDEO, 45 min)
   - Serie sobre POO con ejemplos en Python y Java
4. **Estructuras de Datos - Material de Estudio** (PDF)
   - Guía completa con ejercicios
5. **Quiz de Validación Curricular** (QUIZ, 15 min)
   - Evaluación sobre reglas en diseño curricular
6. **Base de Datos - Laboratorios Prácticos** (OTROS)
   - Conjunto de laboratorios prácticos

### 🎯 Planes de Estudio de Ejemplo

#### 1. Ingeniería en Ciencias Informáticas (5 años, 240 créditos)

**Estructura:**

- **Ciclo Básico** (60 créditos, semestres 1-2)
  - Matemática I (OBLIGATORIO)
  - Matemática II (OBLIGATORIO, prereq: Matemática I)
  - Fundamentos de Programación (OBLIGATORIO)
  - Estructuras de Datos (OBLIGATORIO, prereq: Fundamentos)
- **Ciclo Profesional** (120 créditos, semestres 3-8)
  - Ingeniería de Software (OBLIGATORIO)
  - Bases de Datos (OBLIGATORIO)
  - Redes de Computadoras (OBLIGATORIO)
  - **Especialización** (XOR - elegir una):
    - Desarrollo de Software (30 créditos)
    - Ciencia de Datos (30 créditos)
    - Seguridad Informática (30 créditos)
- **Asignaturas Electivas** (OR - mínimo 3):
  - Desarrollo Móvil
  - Computación en la Nube
  - Internet de las Cosas
  - Blockchain
  - Realidad Virtual y Aumentada
- **Práctica Profesional** (12 créditos, semestre 9)
- **Trabajo de Diploma** (30 créditos, semestre 10)

#### 2. Desarrollo Web Full Stack (6 meses)

**Estructura:**

- **Frontend Development** (OBLIGATORIO, 120 horas)
  - HTML/CSS Fundamentals
  - JavaScript
  - **Framework Frontend** (XOR - elegir uno):
    - React
    - Vue.js
    - Angular
- **Backend Development** (OBLIGATORIO, 100 horas)
  - Node.js y Express
  - Bases de Datos
  - RESTful APIs
- **Módulos Opcionales** (OR - al menos uno):
  - DevOps Básico
  - Testing Avanzado
  - Seguridad Web
- **Proyecto Final** (OBLIGATORIO, 80 horas)

### ⚙️ Configuraciones del Sistema

| Configuración                  | Valor   | Descripción                                    |
| ------------------------------ | ------- | ---------------------------------------------- |
| `MAINTENANCE_MODE`             | `False` | Sistema disponible para uso normal             |
| `GENERATE_PDF`                 | `True`  | Permite generación de PDF de planes de estudio |
| `DOWNLOAD_PDF`                 | `True`  | Permite descarga de PDF de itinerarios         |
| `CHECK_TASK`                   | `True`  | Consulta de tareas de procesamiento            |
| `ENABLE_CURRICULUM_VALIDATION` | `True`  | Validación automática de coherencia curricular |
| `MAX_CURRICULUM_VERSIONS`      | `10`    | Número máximo de versiones a mantener          |
| `ENABLE_COLLABORATIVE_DESIGN`  | `True`  | Diseño colaborativo de modelos                 |
| `AUTO_SAVE_INTERVAL`           | `300`   | Auto-guardado cada 5 minutos                   |
| `ENABLE_LEARNING_ANALYTICS`    | `True`  | Módulo de analíticas de aprendizaje            |
| `DEFAULT_CREDIT_HOURS`         | `120`   | Créditos académicos por defecto                |

## 🔧 Configuración

### Variables de Entorno

El sistema usa la variable `ENVIRONMENT` para determinar qué tipo de seeding ejecutar:

```bash
# .env
ENVIRONMENT=local           # → seed_development() - Todos los datos de ejemplo
ENVIRONMENT=development     # → seed_development() - Todos los datos de ejemplo
ENVIRONMENT=staging         # → seed_production() - Solo datos esenciales
ENVIRONMENT=production      # → seed_production() - Solo datos esenciales
```

### Personalización

#### Agregar Nuevos Usuarios de Desarrollo

Edita `backend/app/seed/data_users.py`:

```python
development_users = [
    # ... usuarios existentes ...
    ("nuevo.profesor@example.com", "password123", UserRole.VIEWER, False),
]
```

#### Agregar Nuevos Dominios Académicos

Edita `backend/app/seed/data_models.py`:

```python
domains_data = [
    # ... dominios existentes ...
    {
        "name": "Gaming",
        "description": "Dominio para aplicaciones de videojuegos",
    },
]
```

#### Agregar Nuevo Plan de Estudios

Edita `backend/app/seed/data_models.py`:

```python
nuevo_plan = {
    "name": "Maestría en Inteligencia Artificial",
    "description": "Programa de posgrado en IA",
    "domain_name": "Ciencia de Datos",
    "version": {
        "version_number": 1,
        "status": ModelStatus.PUBLISHED,
        "features": [
            {
                "name": "Maestría IA",
                "type": FeatureType.MANDATORY,
                "properties": {
                    "creditos_totales": 90,
                    "duracion_años": 2
                },
                "children": [
                    {
                        "name": "Machine Learning Avanzado",
                        "type": FeatureType.MANDATORY,
                        "properties": {"creditos": 8},
                    },
                    # ... más asignaturas ...
                ],
            }
        ],
    },
}

feature_models_data.append(nuevo_plan)
```

#### Agregar Nuevos Recursos Educativos

Edita `backend/app/seed/data_models.py`:

```python
resources_data.append({
    "title": "Nuevo Curso Online",
    "type": ResourceType.VIDEO,
    "description": "Descripción del curso",
    "language": "es",
    "duration_minutes": 120,
    "status": ResourceStatus.PUBLISHED,
    "license": LicenseType.CREATIVE_COMMONS_BY,
    "content_url_or_data": {"url": "https://example.com/curso"},
})
```

## 🛡️ Características de Seguridad

### Idempotencia

Todas las funciones de seeding verifican si los datos ya existen antes de crearlos:

```python
existing = session.exec(
    select(User).where(User.email == email)
).first()

if existing:
    logger.info(f"  ℹ️  Usuario '{email}' ya existe, omitiendo...")
    return existing
```

### Separación Producción/Desarrollo

- Usuarios de producción **NO** tienen contraseñas predeterminadas conocidas
- Usuarios de desarrollo **SÍ** tienen contraseñas conocidas para testing
- El modo se determina automáticamente por `ENVIRONMENT`

### Logging Completo

Todas las operaciones se registran:

```
🌱 INICIANDO DATABASE SEEDING - Entorno: LOCAL
🌱 Sembrando usuarios de desarrollo...
  ✅ Creado usuario: admin@example.com (Admin)
  ✅ Creado usuario: designer@example.com (Designer)
✅ Usuarios sembrados: 6 usuarios creados
```

## 📝 Integración con el Sistema

### En `prestart.sh`

```bash
# Seed database with test data (only in development)
if [ "$ENVIRONMENT" = "local" ] || [ "$ENVIRONMENT" = "development" ]; then
    echo "🌱 Seeding database with test data..."
    python -m app.seed.main
fi
```

### En `init_db()` (db.py)

```python
from app.seed.seeders import seed_settings, seed_production_users

def init_db(session: Session) -> None:
    # ... crear superusuario ...

    # Usar sistema centralizado
    seed_settings(session)
    seed_production_users(session)
```

## 🔄 Migración desde Sistema Anterior

Si estabas usando:

- ❌ `app.core.data.settings` → ✅ `app.seed.data_settings`
- ❌ `app.core.data.users` → ✅ `app.seed.data_users`
- ❌ `app.seed_data.main()` → ✅ `app.seed.main.seed_all()`

El archivo `app/seed_data.py` se mantiene por compatibilidad pero redirige al nuevo sistema.

## 🧪 Testing

Para probar el seeding en un entorno limpio:

```bash
# 1. Resetear base de datos
docker-compose -f docker-compose.dev.yml down -v

# 2. Iniciar servicios
docker-compose -f docker-compose.dev.yml up -d db

# 3. Ejecutar migraciones
docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head

# 4. Ejecutar seeding
docker-compose -f docker-compose.dev.yml exec backend python -m app.seed.main

# 5. Verificar
docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d app -c "SELECT email, role FROM users;"
```

## 📚 Referencias

- [Documentación de SQLModel](https://sqlmodel.tiangolo.com/)
- [Guía de Desarrollo](../../DEVELOPMENT_QUICKSTART.md)
- [Arquitectura del Proyecto](../../docs/1_architecture/folder_structure.md)

---

**Última actualización**: 24 de noviembre de 2025
