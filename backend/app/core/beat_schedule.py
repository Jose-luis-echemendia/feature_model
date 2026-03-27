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
}
