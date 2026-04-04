# Copilot Repository Instructions

## Propósito

Proveer a agentes AI (y nuevos colaboradores) con la información mínima necesaria
para ser productivos en este repo: arquitectura, flujos comunes, convenciones y
comandos reproducibles.

## Reglas de commit (preservadas)

- Usar Conventional Commits: cada commit representa un cambio lógico.
- Evitar commits con debug/temporales. Preferir commits atómicos.

## Arquitectura rápida (qué mirar primero)

- Backend: FastAPI + SQLModel en [backend/app](backend/app) — punto de entrada: [backend/app/main.py](backend/app/main.py).
- Persistencia: PostgreSQL + SQLModel; migraciones con Alembic (`backend/alembic.ini`).
- Caché/Cola: Redis y Celery (tareas en `backend/app/tasks`).
- Almacenamiento de objetos: MinIO (clientes en `backend/app/core/s3`).
- Frontend: Next.js en `frontend/`.
- Infra local: varios `docker-compose` en la raíz (`docker-compose.dev.yml`, `docker-compose.backend.dev.yml`).

## Flujos y comandos esenciales

- Levantar backend en desarrollo (Docker):

  docker-compose -f docker-compose.backend.dev.yml up --build

- Alternativa local (sin Docker, desde la raíz del proyecto):

  cd backend
  python -m uvicorn app.main:app --reload --port 8000 --reload-dir backend/app

- Migraciones Alembic (generar / aplicar):

  cd backend
  alembic -c alembic.ini revision --autogenerate -m "msg"
  alembic -c alembic.ini upgrade head

- Tests (backend):

  cd backend
  pytest -q

  (alternativa: ejecutar `./scripts/test.sh` desde la raíz si existe)

- Comprobaciones de estilo / tipos:

  cd backend
  ruff .
  mypy backend

## Patrones y convenciones específicas

- Separación clara: `app/core` contiene infra (db, cache, config, logging),
  `app/api` contiene routers y validaciones, `app/services` implementa lógica de dominio.
- Registro de rutas: ver `app.api.v1.router` y uso de `settings.API_V1_PREFIX` en [backend/app/main.py](backend/app/main.py).
- Lifespan: la inicialización de todos los servicios se hace en la función `lifespan`
  de `main.py` (arranque y teardown ordenado). Evita duplicar lógica de startup.
- Manejo de errores: `app.exceptions` registra manejadores globales — seguir ese patrón para errores HTTP y validación.
- Logging: `structlog` y utilidades en `app/core/logging.py` — usar `get_logger(__name__)`.
- Modelos: usar `SQLModel` en `app/models` y actualizar migraciones vía Alembic.

## Integraciones y puntos a revisar

- Configuración central: `backend/app/core/config.py` — todas las variables de entorno relevantes viven aquí (DB, REDIS, MINIO, SENTRY).
- Health checks: `GET /health` en `main.py` muestra dependencias (DB, Redis, MinIO).
- Admin / UI interna: `setup_admin` inicializa panel administrativo; ver `app/admin.py`.

## Consejos prácticos para agentes

- Al añadir un endpoint, registrar la ruta en `app/api/v1` y seguir el prefijo de `settings`.
- Para cambios en el esquema de datos: modificar `app/models`, luego crear una revisión Alembic y correr `alembic upgrade`.
- Para tareas asíncronas o cron: revisar `app/tasks` y la configuración Celery en `app/core`.
- Antes de abrir PR: ejecutar tests backend (`pytest`), lint (`ruff`) y tipos (`mypy`) en `backend/`.

## Dónde mirar ejemplos concretos

- Punto de arranque y lifecycle: [backend/app/main.py](backend/app/main.py).
- Configuración y variables: [backend/app/core/config.py](backend/app/core/config.py).
- Dependencias y versiones: [backend/pyproject.toml](backend/pyproject.toml).
- Docker/dev compose: `docker-compose.dev.yml`, `docker-compose.backend.dev.yml` en la raíz.

## Preguntas frecuentes para iterar

- ¿Preferís que el agente genere migrations automáticamente? (sí/no)
- ¿Hay hosts externos/secretos que no deberían usarse en local? Indica qué valores de `config.py` son sensibles.

## Feedback

Revisa este archivo y dime si quieres más ejemplos concretos (p. ej. snippets de creación de router, ejemplo de Alembic revision). Puedo iterar según tu feedback.
