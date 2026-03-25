"""
app/workers/beat_schedule.py

Tareas periódicas de Celery Beat para el dominio CV.

Cada entrada define:
  task     — nombre registrado de la tarea (@shared_task con name=...)
  schedule — cuándo ejecutar (crontab o timedelta)
  options  — cola, expiración y prioridad

Arrancar Beat (proceso separado del worker):
  celery -A app.celery_app.celery_app beat --loglevel info
"""

from celery.schedules import crontab

BEAT_SCHEDULE: dict = {
    # ── Limpieza de PDFs expirados ────────────────────────────────────────────
    # Borra de MinIO los PDFs cuyo presigned URL ya expiró y marca el CV
    # como DRAFT para que el usuario sepa que debe regenerarlo.
    # Se ejecuta cada hora.
    # "cleanup-expired-pdfs": {
    #     "task": "app.tasks.cleanup.cleanup_expired_pdfs",
    #     "schedule": crontab(minute=0),  # cada hora en punto
    #     "options": {
    #         "queue": "maintenance",
    #         "expires": 3300,  # descarta si lleva > 55 min en cola
    #     },
    # },
}
