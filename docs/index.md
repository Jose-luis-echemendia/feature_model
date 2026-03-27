# 📚 Documentación Interna de la Plataforma

Bienvenido a la documentación técnica completa del proyecto **Feature Model**. Esta documentación está organizada en tres secciones principales que cubren todos los aspectos del sistema.

---

## 🚀 Acceso Rápido

### :fontawesome-brands-git-alt: Repositorio

[:fontawesome-brands-github: **Repositorio GitHub**](https://github.com/Jose-luis-echemendia/characteristic_model){ .md-button .md-button--primary }

---

### 📦 Proyecto (Root)

Documentación general del proyecto, arquitectura global y configuración de despliegue.

[:octicons-arrow-right-24: **Explorar Documentación del Proyecto**](root_index.md){ .md-button .md-button--primary }

---

### ⚙️ Backend

API, modelos de datos, servicios, migraciones y documentación técnica del backend.

[:octicons-arrow-right-24: **Explorar Documentación del Backend**](backend_README.md){ .md-button .md-button--primary }

---

### 🎨 Frontend

Componentes, páginas, hooks y documentación del frontend (En construcción).

[:octicons-arrow-right-24: **Explorar Documentación del Frontend**](#frontend){ .md-button }

---

## 📖 Estructura de la Documentación

### 📦 Proyecto (Root)

Documentación de nivel superior que abarca:

- **Arquitectura**: Estructura de carpetas, base de datos, arquitectura de despliegue
- **Configuración**: Entornos de desarrollo y producción
- **Requisitos**: Requisitos funcionales y no funcionales del sistema

**Archivos principales:**

- [Índice del Proyecto](root_index.md)
- [README](root_README.md)
- [Requisitos](root_requirements.md)
- [Arquitectura - Estructura de Carpetas](root_1_architecture_folder_structure.md)
- [Arquitectura - Base de Datos](root_1_architecture_db.md)
- [Arquitectura - Despliegue](root_1_architecture_DEPLOYMENT_ARCHITECTURE.md)
- [Configuración - Desarrollo](root_2_configuration_development.md)
- [Configuración - Despliegue](root_2_configuration_deployment.md)

---

### ⚙️ Backend

Documentación técnica del backend (FastAPI + PostgreSQL):

**Core:**

- [README Backend](backend_README.md) - Introducción y setup
- [Comandos](backend_commands.md) - Comandos útiles de desarrollo
- [Base de Datos](backend_db.md) - Esquema y migraciones
- [Arquitectura S3](backend_MINIO_architecture.md) - Gestión de archivos

**Refactorings y Mejoras:**

- [Cambios Educativos](backend_CAMBIOS_EDUCATIVOS.md)
- [Login Endpoints Refactor](backend_LOGIN_ENDPOINTS_REFACTOR.md)
- [Resumen Refactor Login](backend_LOGIN_REFACTOR_SUMMARY.md)
- [Maestría Ciencia de Datos](backend_MAESTRIA_CIENCIA_DATOS.md)
- [Orden de Migraciones](backend_MIGRATION_ORDER_FIX.md)
- [Servicio Prestart](backend_PRESTART_SERVICE.md)

**Servicios S3:**

- [Refactoring S3](backend_README_MINIO_REFACTORING.md)
- [Ejemplos S3 Dependencies](backend_MINIO_dependency_examples.md)
- [Cambios Servicio S3](backend_MINIO_service_changes.md)
- [Uso Servicio S3](backend_MINIO_service_usage.md)

**Gestión de Usuarios:**

- [Migración User Endpoints](backend_user_endpoints_migration.md)
- [Roles de Usuario](backend_user_role.md)
- [Sugerencias de Código](backend_suggestions_code.md)
- [Requisitos Funcionales](backend_rf.md)

---

### 🎨 Frontend

Documentación del frontend (Next.js + TypeScript):

!!! info "En construcción"
La documentación del frontend está actualmente en desarrollo. Próximamente se agregarán documentos sobre componentes, hooks, páginas y servicios.

---

## 🔧 Características de esta Documentación

Esta documentación incluye:

- ✅ **Búsqueda en tiempo real** - Busca en todo el contenido
- ✅ **Modo oscuro/claro** - Cambia el tema según tu preferencia
- ✅ **Navegación por pestañas** - Organización clara por secciones
- ✅ **Código con resaltado** - Syntax highlighting para múltiples lenguajes
- ✅ **Diagramas Mermaid** - Visualización de flujos y arquitecturas
- ✅ **Responsive** - Optimizada para desktop y móvil

---

## 📊 Tecnologías Documentadas

=== "Backend"

    - **Framework:** FastAPI 0.104+
    - **Base de Datos:** PostgreSQL 17
    - **ORM:** SQLModel + SQLAlchemy
    - **Cache:** Redis
    - **Storage:** MinIO (S3 compatible)
    - **Tasks:** Celery
    - **Migraciones:** Alembic

=== "Frontend"

    - **Framework:** Next.js 14+
    - **Lenguaje:** TypeScript
    - **UI Library:** React
    - **Estilos:** CSS Modules / Tailwind
    - **State:** Zustand / React Query

=== "DevOps"

    - **Containerización:** Docker + Docker Compose
    - **CI/CD:** GitHub Actions
    - **Documentación:** MkDocs Material
    - **Linting:** ESLint, Ruff, MyPy

---

## 🆘 Ayuda y Soporte

Si encuentras algún problema o tienes sugerencias:

1. 📝 **Documentación incompleta:** Abre un issue en GitHub
2. 🐛 **Bug en la aplicación:** Reporta en el repositorio
3. 💡 **Sugerencia de mejora:** Crea una discusión en GitHub

---

## 📌 Enlaces Útiles

- [:fontawesome-brands-github: Repositorio GitHub](https://github.com/Jose-luis-echemendia/characteristic_model)

**Servicios de la Aplicación:**

!!! tip "URLs Dinámicas"
Los siguientes enlaces se configuran automáticamente según el entorno:

    - **Desarrollo:** `http://localhost:8000` (backend), `http://localhost:5173` (frontend)
    - **Producción:** Configurado mediante variables de entorno `DOMAIN` y `FRONTEND_URL`

=== "API Documentation"

    - **Swagger UI:** `{{ config.extra.domain }}/docs`
    - **ReDoc:** `{{ config.extra.domain }}/redoc`

=== "Frontend"

    - **Dashboard:** `{{ config.extra.frontend_url }}`

---

**Enlaces Rápidos (Desarrollo):**

<div class="grid cards" markdown>

- :material-api:{ .lg .middle } **API Docs - Swagger**

  ***

  Documentación interactiva de la API con interfaz Swagger UI

  [:octicons-arrow-right-24: Abrir Swagger](http://localhost:8000/docs){ .md-button }

- :material-book-open-page-variant:{ .lg .middle } **API Docs - ReDoc**

  ***

  Documentación de la API en formato ReDoc

  [:octicons-arrow-right-24: Abrir ReDoc](http://localhost:8000/redoc){ .md-button }

- :material-view-dashboard:{ .lg .middle } **Dashboard Frontend**

  ***

  Interfaz de usuario de la aplicación

  [:octicons-arrow-right-24: Abrir Dashboard](http://localhost:5173){ .md-button }

</div>

---

<div align="center">

**Feature Model Platform** | Documentación Interna  
Última actualización: {{ git.date }}

</div>
