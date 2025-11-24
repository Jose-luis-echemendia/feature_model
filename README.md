# 🚀 Feature Models Platform - README

![Estado del Proyecto](https://img.shields.io/badge/estado-en%20desarrollo-yellow)
![Licencia](https://img.shields.io/badge/licencia-MIT-blue)

Plataforma completa para gestión de modelos de características (Feature Models) con backend FastAPI y frontend Next.js. es una innovadora plataforma web diseñada para la creación y gestión de planes de estudio y formación basados en modelos de características (*feature modeling*). Este sistema transforma la manera en que las instituciones educativas y corporativas diseñan sus currículos, pasando de un modelo estático a uno dinámico, modular y personalizable.

---

## 📜 Proyecto de Tesis

Este proyecto es el resultado de nuestro trabajo de tesis para optar por el título de Ingeniería en Ciencias Informáticas.

*   **Título General del Proyecto:** "Plataforma para la Configuración de Modelos de Características Aplicada al Diseño Curricular"
*   **Promotora y Tutora General:** M. Sc. Yadira Ramírez Rodríguez (yramirezr@uci.cu)

### 👨‍💻 Tesistas y Autores

| Rol             | Autor                                   | Tesis Individual                                                                              | Contacto                                   | Tutor Específico           |
| --------------- | --------------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------ | -------------------------- |
| 🚀 **Backend**  | José Luis Echemendía López              | _"Desarrollo de un sistema gestor de modelos de características utilizando FastAPI y PostgreSQL"_ | josee@estudiantes.uci.cu                  | M. Sc. Yadira Ramírez Rodríguez<br>Ing. Liany Sobrino Miranda |
| 🎨 **Frontend** | Ernes Valdés Díaz | _"Implementación de una interfaz visual para la configuración de itinerarios curriculares con Next.js"_ | evdiaz@estudiantes.uci.cu                      | M. Sc. Yadira Ramírez Rodríguez |

---

## 📋 Tabla de Contenidos

1.  [Propósito y Objetivos](#-propósito-y-objetivos)
2.  [🌟 Características Principales](#-características-principales)
3.  [🛠️ Stack Tecnológico](#️-stack-tecnológico)
4.  [🏗️ Arquitectura del Sistema](#️-arquitectura-del-sistema)
5.  [📁 Estructura de Carpetas](#-estructura-de-carpetas)
6.  [🚀 Guía de Instalación y Puesta en Marcha](#-guía-de-instalación-y-puesta-en-marcha)
7.  [✍️ Estándares y Convenciones de Código](#️-estándares-y-convenciones-de-código)
8.  [⚙️ Variables de Entorno](#️-variables-de-entorno)
9.  [Desarrollo](#desarrollo)
10. [Despliegue](#despliegue)
11. [📚 Documentación](#-documentación)
12. [Contribución](#contribución)
13. [⚖️ Licencia](#️-licencia)

---

## 🎯 Propósito y Objetivos

El propósito fundamental de **Feature Models Platform** es ofrecer una herramienta flexible y potente para que diseñadores instruccionales, académicos y jefes de formación puedan modelar, validar y generar itinerarios de aprendizaje a medida, asegurándoles variabilidad en sus planes
curriculares y contenidos académicos.

### Objetivos Principales

*   **Modelado Visual:** Permitir la creación de planes de estudio como árboles de características jerárquicos y visuales.
*   **Validación Automática:** Asegurar que cualquier itinerario generado sea coherente y válido, aplicando reglas de prerrequisitos, exclusiones y opcionalidad.
*   **Reutilización de Contenido:** Centralizar los recursos de aprendizaje (videos, documentos) para que puedan ser reutilizados en múltiples cursos.
*   **Flexibilidad Curricular:** Facilitar la creación de especializaciones, rutas personalizadas y planes adaptativos para diferentes perfiles de estudiantes.
*   **Colaboración y Calidad:** Implementar un flujo de trabajo basado en roles que permita la colaboración en el diseño y la aprobación de los planes de estudio antes de su publicación.

---


## ✨ Características Principales

- **Gestión de Modelos de Características**: Crear, editar y versionar modelos de features con  elementos obligatorios, opcionales, alternativos (XOR) y opcionales en grupo (OR).
- **Gestión de Reglas:** Define relaciones complejas como prerrequisitos (`requires`) y exclusiones (`excludes`) entre componentes.
- **Biblioteca de Recursos:** Un catálogo centralizado para gestionar los materiales de aprendizaje (`Resource`) y enlazarlos a los componentes del curso.
- **Etiquetado Pedagógico:** Usa `Tags` para clasificar componentes por dificultad, estilo de aprendizaje o competencias, permitiendo la personalización avanzada.
- **Roles y Permisos:** Un sistema granular de roles (`ADMIN`, `MODEL_DESIGNER`, `REVIEWER`, etc.) que define un flujo de trabajo claro de creación, revisión y publicación.
- **Control de Versiones:** Guarda "snapshots" de los modelos para poder evolucionarlos sin afectar a los itinerarios ya generados.
- **Configuración Automática**: Ensambla itinerarios de aprendizaje válidos y listos para ser exportados o implementados.
- **API RESTful Completa**: Documentación interactiva con Swagger/ReDoc
- **Almacenamiento S3**: Compatible con MinIO/AWS S3
- **Tareas Asíncronas**: Procesamiento en background con Celery
- **Autenticación JWT**: Sistema seguro de tokens
- **UI Moderna**: Interface responsive con Next.js 16 y React 19

## 🛠️ Tecnologías

### Backend

- **Framework**: FastAPI (Python 3.10+)
- **ORM**: SQLModel
- **Base de Datos**: PostgreSQL 17
- **Cache**: Redis 7
- **Tareas Asíncronas**: Celery
- **Storage**: MinIO (S3-compatible)
- **Migraciones**: Alembic
- **Testing**: Pytest

### Frontend

- **Framework**: Next.js 16
- **UI Library**: React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS

### DevOps

- **Containerización**: Docker & Docker Compose
- **Reverse Proxy**: Traefik (producción)
- **CI/CD**: GitHub Actions (configurado)
- **Monitoreo**: Sentry (opcional)

## 🚀 Inicio Rápido

### Pre-requisitos

- Docker Desktop instalado y corriendo
- Git
- 4GB RAM mínimo disponible
- Puertos 3000 y 8000 disponibles

### Instalación Automática (Recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/Jose-luis-echemendia/characteristic_model.git
cd characteristic_model

# 2. Ejecutar script de inicio rápido
./scripts/dev-start.sh
```

**¡Eso es todo!** El script automáticamente:

- ✅ Verifica Docker
- ✅ Crea archivo `.env`
- ✅ Construye las imágenes
- ✅ Inicia todos los servicios
- ✅ Ejecuta migraciones
- ✅ Puebla la base de datos con datos de prueba
- ✅ Valida que todo funcione

### Instalación Manual

```bash
# 1. Clonar y configurar
git clone https://github.com/Jose-luis-echemendia/characteristic_model.git
cd characteristic_model

# 2. Crear archivo de entorno
cp .env.example .env

# 3. Crear red Docker
docker network create shared-network

# 4. Iniciar servicios
docker-compose -f docker-compose.dev.yml up --build
```

### 🌐 Acceso a la Aplicación

Una vez iniciado, accede a:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **MinIO Console**: http://localhost:9001

### 👤 Credenciales de Prueba

| Rol          | Email                      | Password      | Permisos              |
| ------------ | -------------------------- | ------------- | --------------------- |
| Admin        | `admin@example.com`        | `admin123`    | Acceso completo       |
| Designer     | `designer@example.com`     | `designer123` | Crear/editar modelos  |
| Editor       | `editor@example.com`       | `editor123`   | Editar modelos        |
| Configurator | `configurator@example.com` | `config123`   | Crear configuraciones |
| Viewer       | `viewer@example.com`       | `viewer123`   | Solo lectura          |

## 💻 Desarrollo

### Estructura del Proyecto

```
feature_model/
├── backend/                # Backend FastAPI
│   ├── app/
│   │   ├── api/           # Endpoints de la API
│   │   ├── core/          # Configuración core
│   │   ├── crud/          # Operaciones de BD
│   │   ├── models/        # Modelos SQLModel
│   │   ├── schemas/       # Schemas Pydantic
│   │   ├── services/      # Lógica de negocio
│   │   └── seed_data.py   # Datos de prueba
│   ├── alembic/           # Migraciones de BD
│   └── tests/             # Tests del backend
├── frontend/              # Frontend Next.js
│   └── src/
│       └── app/           # App Router de Next.js
├── scripts/               # Scripts de utilidad
│   ├── dev-start.sh      # Inicio rápido
│   └── validate_dev_environment.sh
├── docs/                  # Documentación
├── docker-compose.dev.yml # Desarrollo
└── docker-compose.prod.yml # Producción
```

### Comandos Útiles

#### Ver Logs

```bash
# Todos los servicios
docker-compose -f docker-compose.dev.yml logs -f

# Solo backend
docker-compose -f docker-compose.dev.yml logs -f backend

# Solo frontend
docker-compose -f docker-compose.dev.yml logs -f frontend
```

#### Gestión de Servicios

```bash
# Detener servicios
docker-compose -f docker-compose.dev.yml stop

# Reiniciar servicios
docker-compose -f docker-compose.dev.yml restart

# Reiniciar solo un servicio
docker-compose -f docker-compose.dev.yml restart backend
```

#### Base de Datos

```bash
# Ejecutar migraciones
docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head

# Crear nueva migración
docker-compose -f docker-compose.dev.yml exec backend alembic revision --autogenerate -m "descripcion"

# Re-ejecutar seeding
docker-compose -f docker-compose.dev.yml exec backend python -m app.seed_data

# Acceder a PostgreSQL
docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d app
```

#### Limpiar y Resetear

```bash
# Detener y eliminar contenedores (mantiene datos)
docker-compose -f docker-compose.dev.yml down

# Eliminar TODO incluida la base de datos
docker-compose -f docker-compose.dev.yml down -v

# Rebuild completo desde cero
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up
```

#### Validación

```bash
# Validar entorno de desarrollo
./scripts/validate_dev_environment.sh

# Validar configuración de producción
./scripts/validate_deployment.sh
```

### Desarrollo Backend

#### Ejecutar Tests

```bash
# Todos los tests
docker-compose -f docker-compose.dev.yml exec backend pytest

# Con coverage
docker-compose -f docker-compose.dev.yml exec backend pytest --cov=app

# Tests específicos
docker-compose -f docker-compose.dev.yml exec backend pytest tests/api/test_users.py
```

#### Formatear Código

```bash
# Formatear con black y isort
docker-compose -f docker-compose.dev.yml exec backend bash scripts/format.sh

# Linting
docker-compose -f docker-compose.dev.yml exec backend bash scripts/lint.sh
```

#### Shell del Backend

```bash
# Acceder a shell Python
docker-compose -f docker-compose.dev.yml exec backend bash

# IPython shell
docker-compose -f docker-compose.dev.yml exec backend python
```

### Desarrollo Frontend

#### Hot Reload

El frontend está configurado con hot-reload automático:

- Edita archivos en `frontend/src/`
- Los cambios se reflejan automáticamente
- No necesitas reiniciar el contenedor

#### Instalar Dependencias

```bash
# Desde fuera del contenedor
docker-compose -f docker-compose.dev.yml exec frontend npm install <paquete>

# O reconstruir la imagen
docker-compose -f docker-compose.dev.yml up --build frontend
```

#### Build de Producción

```bash
# Build optimizado
docker-compose -f docker-compose.dev.yml exec frontend npm run build

# Preview del build
docker-compose -f docker-compose.dev.yml exec frontend npm run start
```

## 🚢 Despliegue

### Producción con Docker Compose

```bash
# 1. Configurar variables de entorno
cp .env.example .env
# Editar .env con valores de producción

# 2. Crear redes
docker network create traefik-public
docker network create internal_network

# 3. Desplegar
docker-compose -f docker-compose.prod.yml up -d

# 4. Verificar
./scripts/validate_deployment.sh
```

### Usando Script de Despliegue

```bash
./scripts/deploy.sh
```

### Configuración de Traefik

El proyecto incluye configuración de Traefik para:

- Reverse proxy automático
- SSL/TLS con Let's Encrypt
- Load balancing
- Health checks

Ver `docker-compose.prod.yml` para detalles.

## 📚 Documentación

### Documentación Técnica

- **[Guía Rápida de Desarrollo](DEVELOPMENT_QUICKSTART.md)**: Para desarrolladores frontend
- **[Arquitectura de Despliegue](DEPLOYMENT_ARCHITECTURE.md)**: Diagrama y explicación
- **[Checklist de Despliegue](DEPLOYMENT_CHECKLIST.md)**: Paso a paso para producción
- **[Correcciones de Despliegue](DEPLOYMENT_FIXES.md)**: Problemas resueltos
- **[Orden de Migraciones](MIGRATION_ORDER_FIX.md)**: Estructura de base de datos
- **[API Docs](http://localhost:8000/docs)**: Documentación interactiva Swagger

### Estructura de Base de Datos

La base de datos sigue una jerarquía de 9 niveles:

1. **Nivel 1**: `app_settings`, `users`
2. **Nivel 2**: `domains`, `resources`, `tags`
3. **Nivel 3**: `feature_model`
4. **Nivel 4**: `feature_model_versions`
5. **Nivel 5**: `features` (sin FK a feature_groups)
6. **Nivel 6**: `feature_groups`
7. **Nivel 7**: Agregar FK `features.group_id → feature_groups.id`
8. **Nivel 8**: `feature_relations`
9. **Nivel 9**: `configurations`

Ver [MIGRATION_ORDER_FIX.md](MIGRATION_ORDER_FIX.md) para detalles.

## 🧪 Testing

### Backend Tests

```bash
# Ejecutar todos los tests
docker-compose -f docker-compose.dev.yml exec backend pytest

# Tests con coverage HTML
docker-compose -f docker-compose.dev.yml exec backend pytest --cov=app --cov-report=html

# Ver coverage en navegador
open backend/htmlcov/index.html
```

### Frontend Tests

```bash
# Tests unitarios
docker-compose -f docker-compose.dev.yml exec frontend npm test

# Tests E2E con Playwright
docker-compose -f docker-compose.dev.yml exec frontend npm run test:e2e
```

## 🔧 Troubleshooting

### Puerto ya en uso

```bash
# Ver qué usa el puerto
sudo lsof -i :8000
sudo lsof -i :3000

# Cambiar puertos en docker-compose.dev.yml o matar el proceso
```

### Base de datos no responde

```bash
# Ver logs
docker-compose -f docker-compose.dev.yml logs db

# Reiniciar servicio
docker-compose -f docker-compose.dev.yml restart db
```

### Datos de prueba no aparecen

```bash
# Verificar ENVIRONMENT
docker-compose -f docker-compose.dev.yml exec backend env | grep ENVIRONMENT

# Re-ejecutar seeding
docker-compose -f docker-compose.dev.yml exec backend python -m app.seed_data
```

### Limpiar todo y empezar de cero

```bash
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea tu rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Convenciones de Código

- **Backend**: Seguir PEP 8, usar Black para formateo
- **Frontend**: Seguir guía de estilo de Next.js/React
- **Commits**: Usar Conventional Commits (feat:, fix:, docs:, etc.)
- **Tests**: Mantener coverage > 80%

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👥 Equipo

- **Backend Lead**: Jose Luis Echemendia
- **Frontend**: [Tu equipo]

## 🆘 Soporte

Si encuentras algún problema:

1. Revisa la sección de [Troubleshooting](#troubleshooting)
2. Consulta los logs: `docker-compose -f docker-compose.dev.yml logs`
3. Verifica el estado: `./scripts/validate_dev_environment.sh`
4. Abre un issue en GitHub con:
   - Descripción del problema
   - Pasos para reproducir
   - Logs relevantes
   - Versión de Docker

## 🔗 Enlaces Útiles

- **Repositorio**: https://github.com/Jose-luis-echemendia/characteristic_model
- **Documentación FastAPI**: https://fastapi.tiangolo.com/
- **Documentación Next.js**: https://nextjs.org/docs
- **Documentación Docker**: https://docs.docker.com/

---

**Hecho con ❤️ por el equipo de Feature Models**
