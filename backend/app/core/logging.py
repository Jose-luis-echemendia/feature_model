"""
app/core/logging.py

Logging estructurado con structlog.

  Desarrollo:  consola colorizada y legible.
  Producción:  JSON por línea (compatible con Loki, Datadog, CloudWatch).

Uso en cualquier módulo:
    from app.core.logging import get_logger
    log = get_logger(__name__)

    log.info("cv.build.started",  cv_id=str(cv.id), user_id=str(user_id))
    log.error("pdf.generation.failed", cv_id=str(cv_id), error=str(exc))
"""

from __future__ import annotations

import logging
import logging.config
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from app.core.config import settings


# ─────────────────────────────────────────────────────────────────────────────
# Processors personalizados
# ─────────────────────────────────────────────────────────────────────────────


def _add_app_context(
    logger: Any,
    method: str,
    event_dict: EventDict,
) -> EventDict:
    """Añade contexto global de la app a cada entrada de log."""
    event_dict.setdefault("app", settings.APP_NAME)
    event_dict.setdefault("env", settings.ENVIRONMENT)
    event_dict.setdefault("version", settings.APP_VERSION)
    return event_dict


def _drop_color_message_key(
    logger: Any,
    method: str,
    event_dict: EventDict,
) -> EventDict:
    """Elimina 'color_message' que uvicorn duplica junto a 'message'."""
    event_dict.pop("color_message", None)
    return event_dict


def _extract_from_record(
    logger: Any,
    method: str,
    event_dict: EventDict,
) -> EventDict:
    """
    Extrae campos útiles del LogRecord de stdlib cuando structlog
    procesa logs de librerías externas (sqlalchemy, celery, uvicorn…).
    """
    record: logging.LogRecord | None = event_dict.get("_record")
    if record is None:
        return event_dict

    event_dict["logger"] = record.name
    event_dict["lineno"] = record.lineno
    event_dict["filename"] = record.filename
    if record.exc_info:
        event_dict["exc_info"] = record.exc_info
    return event_dict


def _add_logger_name_safely(
    logger: Any,
    method: str,
    event_dict: EventDict,
) -> EventDict:
    """
    Añade el nombre del logger sin fallar cuando structlog recibe logger=None
    (caso común en ProcessorFormatter con logs externos/uvicorn).
    """
    logger_name = getattr(logger, "name", None)
    if logger_name:
        event_dict.setdefault("logger", logger_name)
        return event_dict

    record: logging.LogRecord | None = event_dict.get("_record")
    if record is not None:
        event_dict.setdefault("logger", record.name)

    return event_dict


# ─────────────────────────────────────────────────────────────────────────────
# Cadena de processors
# ─────────────────────────────────────────────────────────────────────────────

_SHARED_PROCESSORS: list[Processor] = [
    structlog.processors.TimeStamper(fmt="iso", utc=True),
    structlog.stdlib.add_log_level,
    _add_logger_name_safely,
    _add_app_context,
    _drop_color_message_key,
    structlog.processors.StackInfoRenderer(),
]


def _build_processors(json_output: bool) -> list[Processor]:
    processors = list(_SHARED_PROCESSORS)
    if json_output:
        processors += [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors += [
            structlog.dev.ConsoleRenderer(
                exception_formatter=structlog.dev.plain_traceback,
            ),
        ]
    return processors


# ─────────────────────────────────────────────────────────────────────────────
# Stdlib logging (captura logs de librerías externas)
# ─────────────────────────────────────────────────────────────────────────────


def _configure_stdlib_logging(log_level: str) -> None:
    level_int = getattr(logging, log_level.upper(), logging.INFO)

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "structlog": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        _extract_from_record,
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        *_build_processors(json_output=settings.is_production),
                    ],
                    "foreign_pre_chain": _SHARED_PROCESSORS,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": sys.stdout,
                    "formatter": "structlog",
                },
            },
            "root": {
                "handlers": ["console"],
                "level": level_int,
            },
            "loggers": {
                # ── Uvicorn ──────────────────────────────────────────────────────
                "uvicorn": {"level": "INFO", "propagate": True},
                "uvicorn.access": {"level": "WARNING", "propagate": False},
                "uvicorn.error": {"level": "ERROR", "propagate": True},
                # ── FastAPI ──────────────────────────────────────────────────────
                "fastapi": {"level": "INFO", "propagate": True},
                # ── SQLAlchemy — queries en DEBUG, solo errores en prod ──────────
                "sqlalchemy.engine": {
                    "level": "DEBUG" if settings.DEBUG else "WARNING",
                    "propagate": True,
                },
                # ── Celery ───────────────────────────────────────────────────────
                "celery": {"level": "INFO", "propagate": True},
                "celery.task": {"level": "INFO", "propagate": True},
                "celery.beat": {"level": "INFO", "propagate": True},
                # ── WeasyPrint — bastante verboso, solo warnings ─────────────────
                "weasyprint": {"level": "WARNING", "propagate": True},
                # ── MinIO ────────────────────────────────────────────────────────
                "minio": {"level": "WARNING", "propagate": True},
                # ── httpx ────────────────────────────────────────────────────────
                "httpx": {"level": "WARNING", "propagate": True},
                "httpcore": {"level": "WARNING", "propagate": True},
            },
        }
    )


# ─────────────────────────────────────────────────────────────────────────────
# Setup principal — llamar una sola vez en main.py lifespan
# ─────────────────────────────────────────────────────────────────────────────


def setup_logging(log_level: str | None = None) -> None:
    """
    Inicializa structlog + stdlib logging.
    Si log_level es None usa settings.LOG_LEVEL.

    Llamar UNA SOLA VEZ al arrancar la app:
        setup_logging()
    """
    level = log_level or settings.LOG_LEVEL

    structlog.configure(
        processors=_build_processors(json_output=settings.is_production),
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    _configure_stdlib_logging(level)


# ─────────────────────────────────────────────────────────────────────────────
# Factories y helpers públicos
# ─────────────────────────────────────────────────────────────────────────────


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Retorna un logger structlog con el nombre del módulo.

    Uso:
        log = get_logger(__name__)
        log.info("cv.build.queued", cv_id=str(cv.id))
    """
    return structlog.get_logger(name)


class LogContext:
    """
    Context manager para atar contexto temporal a todos los logs
    del bloque. Muy útil en tareas Celery.

    Uso:
        with LogContext(cv_id=str(cv_id), user_id=str(user_id)):
            log.info("pdf.render.start")     # lleva cv_id + user_id
            await render_pdf(cv)
            log.info("pdf.render.done")      # ídem
    """

    def __init__(self, **context: Any) -> None:
        self._context = context

    def __enter__(self) -> "LogContext":
        structlog.contextvars.bind_contextvars(**self._context)
        return self

    def __exit__(self, *_: Any) -> None:
        structlog.contextvars.unbind_contextvars(*self._context.keys())


log = get_logger(__name__)
