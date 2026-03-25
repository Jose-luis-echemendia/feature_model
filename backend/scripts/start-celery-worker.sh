#!/bin/bash
# Script para iniciar worker de Celery

echo "🚀 Iniciando Celery worker..."

cd /app

# Iniciar worker con logging
celery -A app.core.celery worker \
    --queues pdf,default,maintenance \
    --concurrency 2 \
    --loglevel info \
    --hostname worker@%h

