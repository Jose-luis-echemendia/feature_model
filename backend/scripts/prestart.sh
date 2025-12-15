#! /usr/bin/env bash

set -e
set -x

echo "========================================="
echo "🚀 Starting prestart script"
echo "========================================="
echo "📅 Date: $(date)"
echo "👤 User: $(whoami)"
echo "📂 Working directory: $(pwd)"
echo ""

# ======================================================
#           --- Let the DB start ---
# ======================================================

echo "⏳ Step 1/4: Waiting for database to be ready..."
python app/backend_pre_start.py
if [ $? -eq 0 ]; then
    echo "✅ Database is ready"
else
    echo "❌ Database connection failed"
    exit 1
fi
echo ""

# ======================================================
#             --- Run migrations ---
# ======================================================

echo "🔄 Step 2/4: Running database migrations..."
echo "📝 Alembic command: alembic upgrade head"
alembic upgrade head
if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully"
else
    echo "❌ Migrations failed"
    exit 1
fi
echo ""

# ======================================================
#             --- Sync documentation ---   
# ======================================================

echo "📚 Step 3/4: Building documentation..."
if [ -f "root_scripts/build_docs.sh" ]; then
    bash root_scripts/build_docs.sh
    if [ $? -eq 0 ]; then
        echo "✅ Documentation built successfully"
    else
        echo "⚠️  Documentation build failed (continuing anyway)"
        # No hacemos exit 1 aquí porque la documentación no es crítica para el arranque
    fi
elif [ -f "scripts/build_docs.sh" ]; then
    bash scripts/build_docs.sh
    if [ $? -eq 0 ]; then
        echo "✅ Documentation built successfully"
    else
        echo "⚠️  Documentation build failed (continuing anyway)"
    fi
else
    echo "⚠️  build_docs.sh not found (skipping documentation build)"
fi
echo ""

# ======================================================
#           --- Create initial data in DB ---
# ======================================================

echo "📊 Step 4/4: 🌱 Iniciando Database Seeding (Entorno: ${ENVIRONMENT:-local})..."
python -m app.seed.main
if [ $? -eq 0 ]; then
    echo "✅ Initial data created successfully"
else
    echo "❌ Initial data creation failed"
    exit 1
fi
echo ""

echo "========================================="
echo "✅ Prestart script completed successfully"
echo "========================================="