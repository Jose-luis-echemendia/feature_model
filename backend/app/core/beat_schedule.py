"""
app/core/beat_schedule.py

Tareas periódicas de Celery Beat para el dominio de Feature Models.

Cada entrada define:
  task     — nombre registrado de la tarea (@shared_task con name=...)
  schedule — cuándo ejecutar (crontab o timedelta)
  options  — cola, expiración y prioridad

Arrancar Beat (proceso separado del worker):
  celery -A app.core.celery.celery_app beat --loglevel info
"""

from celery.schedules import crontab

BEAT_SCHEDULE: dict = {
    # ── Mantenimiento de importaciones de Feature Models ─────────────────────
    # Ejemplo: limpiar jobs de importación atascados.
    # "cleanup-stale-import-jobs": {
    #     "task": "app.tasks.feature_model.cleanup_stale_import_jobs",
    #     "schedule": crontab(minute=0),  # cada hora en punto
    #     "options": {
    #         "queue": "maintenance",
    #         "expires": 3300,  # descarta si lleva > 55 min en cola
    #     },
    # },
    # ── Métricas de modelos activos (diario 02:00) ─────────────────────────
    "refresh-active-models-metrics": {
        "task": "app.tasks.maintenance.refresh_active_models_metrics",
        "schedule": crontab(hour=2, minute=0),
        "options": {"queue": "maintenance", "expires": 3600},
    },
    # ── Limpieza de resultados de tareas (diario 03:00) ────────────────────
    "cleanup-stale-task-results": {
        "task": "app.tasks.maintenance.cleanup_stale_task_results",
        "schedule": crontab(hour=3, minute=0),
        "options": {"queue": "maintenance", "expires": 3600},
    },
    # ── Verificación de integridad (diario 04:00) ──────────────────────────
    "verify-models-integrity": {
        "task": "app.tasks.maintenance.verify_models_integrity",
        "schedule": crontab(hour=4, minute=0),
        "options": {"queue": "maintenance", "expires": 3600},
    },
    # ── Pre-caching de análisis populares (noche 01:00) ────────────────────
    "precache-popular-models": {
        "task": "app.tasks.maintenance.precache_popular_models_analysis",
        "schedule": crontab(hour=1, minute=0),
        "options": {"queue": "maintenance", "expires": 3600},
    },
    # ── Monitoreo de tiempos de análisis (cada hora) ───────────────────────
    "collect-analysis-runtime-metrics": {
        "task": "app.tasks.maintenance.collect_analysis_runtime_metrics",
        "schedule": crontab(minute=0),
        "options": {"queue": "maintenance", "expires": 3500},
    },
    # ── Auditoría de calidad de datos (semanal lunes 05:00) ────────────────
    "audit-feature-model-data-quality": {
        "task": "app.tasks.maintenance.audit_feature_model_data_quality",
        "schedule": crontab(hour=5, minute=0, day_of_week=1),
        "options": {"queue": "maintenance", "expires": 7200},
    },
}
