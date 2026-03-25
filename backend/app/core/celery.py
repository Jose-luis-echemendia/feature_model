"""
app/workers/celery_app.py

Instancia y configuración de Celery para el dominio CV.

Colas:
  pdf        — generación de PDFs  (prioridad alta, tareas lentas)
  default    — operaciones CRUD asíncronas  (prioridad media)
  maintenance — limpieza y tareas de Beat  (prioridad baja)

Arrancar worker:
  celery -A app.celery_app.celery_app worker \
         --queues pdf,default,maintenance \
         --concurrency 4 --loglevel info

Arrancar Beat (en proceso separado):
  celery -A app.celery_app.celery_app beat --loglevel info
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
    "cv_generator",
    broker=settings.REDIS_URL_BROKER,
    backend=settings.REDIS_URL_BACKEND,
    include=[
        "app.tasks.pdf",
        "app.tasks.cleanup",
    ],
)

# ─────────────────────────────────────────────────────────────────────────────
# Colas y exchanges
# ─────────────────────────────────────────────────────────────────────────────

_default_exchange = Exchange("default", type="direct")
_pdf_exchange = Exchange("pdf", type="direct")
_maintenance_exchange = Exchange("maintenance", type="direct")

QUEUES = (
    Queue("default", _default_exchange, routing_key="default"),
    Queue("pdf", _pdf_exchange, routing_key="pdf"),
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
        # Generación de PDFs → cola dedicada con más tiempo
        "app.tasks.pdf.generate_cv_pdf": {
            "queue": "pdf",
            "routing_key": "pdf",
        },
        # Mantenimiento periódico → baja prioridad
        "app.tasks.cleanup.cleanup_expired_pdfs": {
            "queue": "maintenance",
            "routing_key": "maintenance",
        },
        "app.tasks.cleanup.cleanup_stale_building_cvs": {
            "queue": "maintenance",
            "routing_key": "maintenance",
        },
    },
    # ── Tiempos límite ────────────────────────────────────────────────────────
    # pdf_tasks necesita más tiempo que las tareas de CRUD
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
    worker_prefetch_multiplier=1,  # cada worker pide una tarea a la vez (justo para PDFs)
    worker_max_tasks_per_child=50,  # reinicia el proceso cada 50 tareas (evita memory leaks de WeasyPrint)
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
