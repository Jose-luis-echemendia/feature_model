#! /usr/bin/env bash

set -e
set -x

# Let the DB start
python app/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python app/initial_data.py

# Seed database with test data (only in development)
# This is safe to run multiple times - it checks if data exists before creating
if [ "$ENVIRONMENT" = "local" ] || [ "$ENVIRONMENT" = "development" ]; then
    echo "🌱 Seeding database with test data..."
    python -m app.seed_data
fi
