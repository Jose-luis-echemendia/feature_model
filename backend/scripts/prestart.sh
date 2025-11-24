#! /usr/bin/env bash

set -e
set -x

# Let the DB start
python app/backend_pre_start.py

# Run migrations
alembic upgrade head

# ============================================================================
# DATABASE SEEDING - SINGLE ENTRY POINT
# ============================================================================
# El módulo app.seed.main se encarga de TODO el seeding según el entorno:
#   - Production/Staging: Solo datos esenciales (settings, FIRST_SUPERUSER, usuarios de producción)
#   - Local/Development: Datos completos (esenciales + ejemplos + usuarios de prueba)
#
# ============================================================================

echo "🌱 Iniciando Database Seeding (Entorno: ${ENVIRONMENT:-local})..."
python -m app.seed.main
