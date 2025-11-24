# 📦 Sistema Centralizado de Seeding

Este módulo contiene todo el sistema de poblado de base de datos (database seeding) organizado de manera modular y mantenible.

## 📁 Estructura

```
backend/app/seed/
├── __init__.py           # Exportaciones del módulo
├── main.py               # Orquestador principal
├── seeders.py            # Funciones de seeding
├── data_settings.py      # Datos de configuración de la app
├── data_users.py         # Datos de usuarios (producción + desarrollo)
├── data_models.py        # Datos de modelos, dominios, tags, recursos
└── README.md             # Este archivo
```

## 🎯 Modos de Seeding

### Producción

Solo crea datos esenciales:

- ✅ Configuraciones de aplicación (`AppSettings`)
- ✅ Usuarios de producción (sin contraseñas predeterminadas)

```python
from app.seed import seed_production
seed_production(session)
```

### Desarrollo

Crea todos los datos de ejemplo:

- ✅ Usuarios de desarrollo con contraseñas conocidas
- ✅ Dominios de ejemplo (E-Commerce, Healthcare, etc.)
- ✅ Tags (performance, security, ui, etc.)
- ✅ Recursos educativos (videos, PDFs, quizzes)
- ✅ Feature Models de ejemplo

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

## 📊 Datos Incluidos

### Usuarios de Desarrollo

| Email                      | Password      | Rol            | Superuser |
| -------------------------- | ------------- | -------------- | --------- |
| `admin@example.com`        | `admin123`    | ADMIN          | ✅        |
| `designer@example.com`     | `designer123` | MODEL_DESIGNER | ❌        |
| `editor@example.com`       | `editor123`   | MODEL_EDITOR   | ❌        |
| `configurator@example.com` | `config123`   | CONFIGURATOR   | ❌        |
| `viewer@example.com`       | `viewer123`   | VIEWER         | ❌        |
| `reviewer@example.com`     | `reviewer123` | REVIEWER       | ❌        |

### Usuarios de Producción

Los usuarios de producción se crean con contraseña temporal `ChangeMe123!` que debe cambiarse:

- `echemendiajoseluis@gmail.com` (ADMIN)
- `carlos.rodriguez@gmail.com` (MODEL_DESIGNER)
- `laura.martinez@gmail.com` (MODEL_EDITOR)
- `lianysm99@gmail.com` (CONFIGURATOR)
- `yadira.rodriguez@gmail.com` (VIEWER)
- `ernesto.lito@gmail.com` (REVIEWER)

### Dominios

- **E-Commerce**: Sistemas de comercio electrónico
- **Healthcare**: Aplicaciones de salud y medicina
- **Education**: Plataformas educativas
- **IoT**: Internet de las Cosas
- **Finance**: Aplicaciones financieras

### Tags

`performance`, `security`, `ui`, `api`, `mobile`, `analytics`, `payment`, `authentication`, `database`, `cloud`

### Recursos Educativos

- Video: Introducción a Feature Models (15 min)
- PDF: Guía de Configuración
- Quiz: Feature Modeling
- Video: Tutorial Avanzado (30 min)

### Feature Models

- **E-Commerce Platform**: Modelo completo con 7 características
- **Healthcare Management System**: Sistema de gestión médica

## 🔧 Configuración

### Variables de Entorno

El sistema usa la variable `ENVIRONMENT` para determinar qué tipo de seeding ejecutar:

```bash
# .env
ENVIRONMENT=local           # → seed_development()
ENVIRONMENT=development     # → seed_development()
ENVIRONMENT=staging         # → seed_production()
ENVIRONMENT=production      # → seed_production()
```

### Personalización

#### Agregar Nuevos Usuarios de Desarrollo

Edita `data_users.py`:

```python
development_users = [
    # ... usuarios existentes ...
    ("nuevo@example.com", "password123", UserRole.ADMIN, False),
]
```

#### Agregar Nuevos Dominios

Edita `data_models.py`:

```python
domains_data = [
    # ... dominios existentes ...
    {
        "name": "Gaming",
        "description": "Dominio para aplicaciones de videojuegos",
    },
]
```

#### Agregar Nuevo Feature Model

Edita `data_models.py`:

```python
nuevo_modelo = {
    "name": "Mi Modelo",
    "description": "Descripción del modelo",
    "domain_name": "E-Commerce",
    "version": {
        "version_number": 1,
        "status": ModelStatus.PUBLISHED,
        "features": [
            {
                "name": "Característica Principal",
                "type": FeatureType.MANDATORY,
                "properties": {"description": "Descripción"},
                "children": [
                    # ... subfeatures ...
                ],
            }
        ],
    },
}

feature_models_data.append(nuevo_modelo)
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
