#!/bin/bash

# Script de validación de configuración de despliegue
# Verifica que todos los archivos necesarios existan y tengan la configuración correcta

set -e

echo "════════════════════════════════════════════════════════════════"
echo "  🔍 VALIDACIÓN DE CONFIGURACIÓN DE DESPLIEGUE"
echo "════════════════════════════════════════════════════════════════"
echo ""

ERRORS=0
WARNINGS=0

# Función para mostrar errores
error() {
    echo "❌ ERROR: $1"
    ((ERRORS++))
}

# Función para mostrar warnings
warning() {
    echo "⚠️  WARNING: $1"
    ((WARNINGS++))
}

# Función para mostrar OK
ok() {
    echo "✅ $1"
}

# ═══════════════════════════════════════════════════════════════
# VALIDAR ARCHIVOS DEL FRONTEND
# ═══════════════════════════════════════════════════════════════
echo "📁 Validando archivos del Frontend..."
echo ""

# Dockerfile de producción
if [ -f "frontend/Dockerfile" ]; then
    ok "frontend/Dockerfile existe"
    
    # Verificar que tenga multi-stage build
    if grep -q "AS deps" frontend/Dockerfile && \
       grep -q "AS builder" frontend/Dockerfile && \
       grep -q "AS runner" frontend/Dockerfile; then
        ok "  Dockerfile tiene arquitectura multi-stage"
    else
        error "  Dockerfile NO tiene arquitectura multi-stage correcta"
    fi
    
    # Verificar puerto 3000
    if grep -q "EXPOSE 3000" frontend/Dockerfile; then
        ok "  Expone puerto 3000"
    else
        error "  NO expone puerto 3000"
    fi
else
    error "frontend/Dockerfile NO existe"
fi

# next.config.ts
if [ -f "frontend/next.config.ts" ]; then
    ok "frontend/next.config.ts existe"
    
    # Verificar modo standalone
    if grep -q "output.*standalone" frontend/next.config.ts; then
        ok "  Configurado en modo standalone"
    else
        warning "  NO configurado en modo standalone"
    fi
else
    error "frontend/next.config.ts NO existe"
fi

# nginx.conf
if [ -f "frontend/nginx.conf" ]; then
    ok "frontend/nginx.conf existe"
    
    # Verificar proxy a localhost:3000
    if grep -q "localhost:3000" frontend/nginx.conf; then
        ok "  Configurado como proxy a localhost:3000"
    else
        error "  NO configurado como proxy a Next.js"
    fi
else
    error "frontend/nginx.conf NO existe"
fi

# .dockerignore
if [ -f "frontend/.dockerignore" ]; then
    ok "frontend/.dockerignore existe"
else
    warning "frontend/.dockerignore NO existe (recomendado para optimizar build)"
fi

echo ""

# ═══════════════════════════════════════════════════════════════
# VALIDAR DOCKER-COMPOSE
# ═══════════════════════════════════════════════════════════════
echo "🐳 Validando docker-compose.prod.yml..."
echo ""

if [ -f "docker-compose.prod.yml" ]; then
    ok "docker-compose.prod.yml existe"
    
    # Verificar sintaxis de celery
    if grep -q "celery -A app.core.celery.celery_app worker --loglevel=info'" docker-compose.prod.yml; then
        error "  celery_worker tiene comilla extra en el comando"
    else
        ok "  Comando de celery_worker correcto"
    fi
    
    # Verificar consistencia de redes
    if grep -q "internal-network:" docker-compose.prod.yml; then
        error "  Nombre de red inconsistente (internal-network vs internal_network)"
    else
        ok "  Nombres de redes consistentes"
    fi
    
    # Verificar puerto del backend
    if grep -q "bind 0.0.0.0:8010" docker-compose.prod.yml; then
        error "  Backend usa puerto 8010 (debería ser 8000)"
    else
        ok "  Puerto del backend correcto (8000)"
    fi
    
    # Verificar puerto del frontend en Traefik
    if grep -q "frontend.loadbalancer.server.port=80" docker-compose.prod.yml; then
        error "  Frontend configurado en puerto 80 (debería ser 3000)"
    elif grep -q "frontend.loadbalancer.server.port=3000" docker-compose.prod.yml; then
        ok "  Puerto del frontend correcto (3000)"
    else
        warning "  No se pudo verificar puerto del frontend"
    fi
    
    # Validar sintaxis YAML
    if command -v docker-compose &> /dev/null; then
        if docker-compose -f docker-compose.prod.yml config > /dev/null 2>&1; then
            ok "  Sintaxis YAML válida"
        else
            error "  Sintaxis YAML inválida"
        fi
    else
        warning "  docker-compose no disponible, no se puede validar sintaxis"
    fi
else
    error "docker-compose.prod.yml NO existe"
fi

echo ""

# ═══════════════════════════════════════════════════════════════
# VALIDAR VARIABLES DE ENTORNO
# ═══════════════════════════════════════════════════════════════
echo "🔐 Validando variables de entorno..."
echo ""

if [ -f ".env" ]; then
    ok ".env existe"
    
    # Variables críticas
    REQUIRED_VARS=(
        "DOMAIN"
        "FRONTEND_HOST"
        "STACK_NAME"
        "DOCKER_IMAGE_FRONTEND"
        "DOCKER_IMAGE_BACKEND"
        "POSTGRES_USER"
        "POSTGRES_PASSWORD"
        "POSTGRES_DB"
        "SECRET_KEY"
    )
    
    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "^${var}=" .env; then
            ok "  ${var} definida"
        else
            warning "  ${var} NO definida"
        fi
    done
else
    warning ".env NO existe (necesario para despliegue)"
fi

echo ""

# ═══════════════════════════════════════════════════════════════
# RESUMEN
# ═══════════════════════════════════════════════════════════════
echo "════════════════════════════════════════════════════════════════"
echo "  📊 RESUMEN DE VALIDACIÓN"
echo "════════════════════════════════════════════════════════════════"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "🎉 ¡TODO PERFECTO! Configuración lista para despliegue"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  $WARNINGS advertencia(s) encontrada(s)"
    echo "   La configuración puede desplegarse pero hay mejoras recomendadas"
    echo ""
    exit 0
else
    echo "❌ $ERRORS error(es) crítico(s) encontrado(s)"
    echo "⚠️  $WARNINGS advertencia(s) encontrada(s)"
    echo ""
    echo "   ¡CORRIGE LOS ERRORES ANTES DE DESPLEGAR!"
    echo ""
    exit 1
fi
