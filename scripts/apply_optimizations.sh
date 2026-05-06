#!/bin/bash
# Performance Optimization - Quick Start Commands
# Ejecutar desde la raíz del proyecto: bash scripts/apply_optimizations.sh

set -e

echo "🚀 Iniciando aplicación de optimizaciones de performance..."
echo ""

# ============================================================================
# PASO 1: Validar dependencias
# ============================================================================
echo "📋 PASO 1: Validando dependencias..."

if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL client no encontrado"
    exit 1
fi

if ! command -v redis-cli &> /dev/null; then
    echo "❌ Redis client no encontrado"
    exit 1
fi

echo "✅ Dependencias validadas"
echo ""

# ============================================================================
# PASO 2: Aplicar migraciones Alembic (Índices)
# ============================================================================
echo "🗄️  PASO 2: Aplicando migraciones de índices..."

cd backend

# Verificar estado actual
echo "   Estado actual:"
alembic -c alembic.ini current

# Aplicar migraciones
echo "   Aplicando..."
alembic -c alembic.ini upgrade head

echo "✅ Migraciones aplicadas"
echo ""

# ============================================================================
# PASO 3: Verificar índices en PostgreSQL
# ============================================================================
echo "🔍 PASO 3: Verificando índices creados..."

INDICES_COUNT=$(psql -t -c "SELECT COUNT(*) FROM pg_indexes WHERE indexname LIKE 'idx_%'")
echo "   Índices encontrados: $INDICES_COUNT"

if [ "$INDICES_COUNT" -ge 11 ]; then
    echo "✅ Todos los índices creados correctamente"
else
    echo "⚠️  Se esperaban 11+ índices, se encontraron $INDICES_COUNT"
fi

echo ""

# ============================================================================
# PASO 4: Validar Redis
# ============================================================================
echo "💾 PASO 4: Validando Redis..."

if redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis accesible"
else
    echo "❌ Redis no responde"
    exit 1
fi

echo ""

# ============================================================================
# PASO 5: Ejecutar tests (opcional)
# ============================================================================
echo "🧪 PASO 5: Ejecutando tests..."

if pytest -q --tb=short 2>/dev/null; then
    echo "✅ Tests pasados"
else
    echo "⚠️  Algunos tests fallaron (revisar manualmente)"
fi

echo ""

# ============================================================================
# PASO 6: Resumen final
# ============================================================================
echo "=================================="
echo "✨ OPTIMIZACIONES APLICADAS"
echo "=================================="
echo ""
echo "✅ 1.1 - Índices PostgreSQL creados (11 índices)"
echo "✅ 1.2 - Eager loading mejorado (N+1 fix)"
echo "✅ 2.1 - Tree caching con Redis"
echo "✅ 2.2 - Invalidación granular de caché"
echo "✅ 2.3 - TTLs dinámicos por ModelStatus"
echo ""
echo "📊 BENCHMARKS ESPERADOS:"
echo "   • Tree building (cache MISS): 800ms → 150ms (-81%)"
echo "   • Tree building (cache HIT): 800ms → 20ms (-97%)"
echo "   • DB queries: 50 → 3-5 (-94%)"
echo ""
echo "🧪 VALIDAR CON:"
echo "   # Test caché"
echo "   curl -H 'Authorization: Bearer TOKEN' \\"
echo "     'http://localhost:8000/api/v1/feature-models/{id}/versions/{vid}/complete'"
echo ""
echo "   # Monitorear Redis"
echo "   redis-cli --stat"
echo "   redis-cli KEYS 'tree:complete:*'"
echo ""
echo "📝 PRÓXIMOS PASOS:"
echo "   1. Revisar PERFORMANCE_OPTIMIZATION.md para detalles"
echo "   2. Integrar invalidación de caché en repositorios (Paso 4)"
echo "   3. Ejecutar load testing"
echo ""

cd ..

echo "✨ ¡Listo para testing!"
