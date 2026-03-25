#!/bin/bash
# Script para iniciar Celery Beat (scheduler de tareas periódicas)

echo "⏰ Iniciando Celery Beat..."

cd /app

# Iniciar beat con logging
celery -A app.core.celery beat \
    --loglevel info \
    --scheduler celery.beat.PersistentScheduler


