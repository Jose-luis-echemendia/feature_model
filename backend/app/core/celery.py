"""
app/core/celery.py

Instancia y configuración de Celery para el dominio de Feature Models.

Colas:
    import      — importación y transformación de modelos
    validation  — validación lógica/estructural y análisis
    default     — operaciones asíncronas generales
    maintenance — tareas periódicas y housekeeping

Arrancar worker:
    celery -A app.core.celery.celery_app worker \
                 --queues import,validation,default,maintenance \
                 --concurrency 4 --loglevel info

Arrancar Beat (en proceso separado):
    celery -A app.core.celery.celery_app beat --loglevel info
"""

from __future__ import annotations

from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown
from kombu import Exchange, Queue

from app.core.config import settings
from app.core.logging import get_logger, setup_logging

log = get_logger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Instancia
# ─────────────────────────────────────────────────────────────────────────────

celery_app = Celery(
    "feature_model",
    broker=settings.REDIS_URL_BROKER,
    backend=settings.REDIS_URL_BACKEND,
    include=[
        "app.tasks.backfill",
    ],
)

# ─────────────────────────────────────────────────────────────────────────────
# Colas y exchanges
# ─────────────────────────────────────────────────────────────────────────────

_default_exchange = Exchange("default", type="direct")
_import_exchange = Exchange("import", type="direct")
_validation_exchange = Exchange("validation", type="direct")
_maintenance_exchange = Exchange("maintenance", type="direct")

QUEUES = (
    Queue("default", _default_exchange, routing_key="default"),
    Queue("import", _import_exchange, routing_key="import"),
    Queue("validation", _validation_exchange, routing_key="validation"),
    Queue("maintenance", _maintenance_exchange, routing_key="maintenance"),
)

# ─────────────────────────────────────────────────────────────────────────────
# Configuración
# ─────────────────────────────────────────────────────────────────────────────

celery_app.conf.update(
    # ── Broker / Backend ──────────────────────────────────────────────────────
    broker_url=settings.REDIS_URL_BROKER,
    result_backend=settings.REDIS_URL_BACKEND,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    # ── Serialización ─────────────────────────────────────────────────────────
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # ── Colas ─────────────────────────────────────────────────────────────────
    task_queues=QUEUES,
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    # ── Routing de tareas por nombre ──────────────────────────────────────────
    task_routes={
        # Importación de Feature Models
        "app.tasks.feature_model.import_feature_model": {
            "queue": "import",
            "routing_key": "import",
        },
        # Validaciones y análisis
        "app.tasks.feature_model.validate_feature_model_version": {
            "queue": "validation",
            "routing_key": "validation",
        },
        # Mantenimiento periódico
        "app.tasks.feature_model.cleanup_stale_import_jobs": {
            "queue": "maintenance",
            "routing_key": "maintenance",
        },
    },
    # ── Tiempos límite ────────────────────────────────────────────────────────
    # Import/validate puede tardar más que CRUD tradicional
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,  # SoftTimeLimitExceeded
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,  # SIGKILL
    # ── Reintentos ────────────────────────────────────────────────────────────
    task_max_retries=settings.CELERY_MAX_RETRIES,
    task_acks_late=True,  # ACK solo cuando la tarea termina (no al recibirla)
    task_reject_on_worker_lost=True,  # re-encola si el worker muere a mitad
    # ── Resultados ────────────────────────────────────────────────────────────
    result_expires=3600,  # los resultados en Redis expiran en 1 hora
    task_ignore_result=False,  # guardamos resultados para hacer tracking
    # ── Beat ──────────────────────────────────────────────────────────────────
    beat_schedule_filename="celerybeat-schedule",  # fichero de estado de Beat
    beat_max_loop_interval=5,
    # ── Worker ────────────────────────────────────────────────────────────────
    worker_prefetch_multiplier=1,  # cada worker pide una tarea a la vez
    worker_max_tasks_per_child=100,  # reinicia proceso para mitigar leaks en tareas pesadas
    worker_hijack_root_logger=False,  # structlog gestiona el logging
    # ── Beat schedule — importado desde beat_schedule.py ─────────────────────
    beat_schedule=None,  # se sobreescribe al final del módulo
)

# ── Importar el schedule aquí para evitar importaciones circulares ────────────
from app.core.beat_schedule import BEAT_SCHEDULE  # noqa: E402

celery_app.conf.beat_schedule = BEAT_SCHEDULE


# ─────────────────────────────────────────────────────────────────────────────
# Señales del worker
# ─────────────────────────────────────────────────────────────────────────────


@worker_process_init.connect
def init_worker_process(**kwargs: object) -> None:
    """
    Inicializa logging estructurado en cada proceso worker.
    Se dispara cuando Celery hace fork de un proceso hijo.
    """
    setup_logging()
    log.info("celery.worker.started")


@worker_process_shutdown.connect
def shutdown_worker_process(**kwargs: object) -> None:
    log.info("celery.worker.shutdown")
