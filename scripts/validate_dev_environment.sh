#!/bin/bash

# Script de validación del entorno de desarrollo
# Verifica que Docker, docker-compose y todos los servicios estén correctamente configurados

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Emojis
CHECK="✅"
CROSS="❌"
WARNING="⚠️"
INFO="ℹ️"

echo ""
echo "======================================================================"
echo "  🔍 VALIDACIÓN DEL ENTORNO DE DESARROLLO - Feature Models"
echo "======================================================================"
echo ""

# Contador de errores
ERRORS=0
WARNINGS=0

# ==============================================================================
# 1. VERIFICAR PRE-REQUISITOS
# ==============================================================================
echo -e "${BLUE}📋 1. Verificando pre-requisitos...${NC}"
echo ""

# Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}${CHECK} Docker instalado: ${DOCKER_VERSION}${NC}"
else
    echo -e "${RED}${CROSS} Docker NO está instalado${NC}"
    ((ERRORS++))
fi

# Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "${GREEN}${CHECK} Docker Compose instalado: ${COMPOSE_VERSION}${NC}"
else
    echo -e "${RED}${CROSS} Docker Compose NO está instalado${NC}"
    ((ERRORS++))
fi

# Docker en ejecución
if docker info &> /dev/null; then
    echo -e "${GREEN}${CHECK} Docker daemon está en ejecución${NC}"
else
    echo -e "${RED}${CROSS} Docker daemon NO está en ejecución${NC}"
    ((ERRORS++))
fi

echo ""

# ==============================================================================
# 2. VERIFICAR ARCHIVOS DE CONFIGURACIÓN
# ==============================================================================
echo -e "${BLUE}📁 2. Verificando archivos de configuración...${NC}"
echo ""

# docker-compose.dev.yml
if [ -f "docker-compose.dev.yml" ]; then
    echo -e "${GREEN}${CHECK} docker-compose.dev.yml existe${NC}"
    
    # Validar sintaxis YAML
    if docker-compose -f docker-compose.dev.yml config &> /dev/null; then
        echo -e "${GREEN}${CHECK} docker-compose.dev.yml tiene sintaxis válida${NC}"
    else
        echo -e "${RED}${CROSS} docker-compose.dev.yml tiene errores de sintaxis${NC}"
        ((ERRORS++))
    fi
else
    echo -e "${RED}${CROSS} docker-compose.dev.yml NO existe${NC}"
    ((ERRORS++))
fi

# .env file
if [ -f ".env" ]; then
    echo -e "${GREEN}${CHECK} Archivo .env existe${NC}"
    
    # Verificar variables críticas
    if grep -q "POSTGRES_PASSWORD=" .env && \
       grep -q "SECRET_KEY=" .env && \
       grep -q "FIRST_SUPERUSER=" .env; then
        echo -e "${GREEN}${CHECK} Variables de entorno críticas están definidas${NC}"
    else
        echo -e "${YELLOW}${WARNING} Algunas variables de entorno pueden estar faltando${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}${WARNING} Archivo .env NO existe (copia .env.example)${NC}"
    ((WARNINGS++))
fi

echo ""

# ==============================================================================
# 3. VERIFICAR PUERTOS DISPONIBLES
# ==============================================================================
echo -e "${BLUE}🔌 3. Verificando disponibilidad de puertos...${NC}"
echo ""

check_port() {
    PORT=$1
    SERVICE=$2
    
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}${WARNING} Puerto $PORT ($SERVICE) está en uso${NC}"
        PROCESS=$(lsof -Pi :$PORT -sTCP:LISTEN | tail -n 1)
        echo -e "    Proceso: ${PROCESS}"
        ((WARNINGS++))
    else
        echo -e "${GREEN}${CHECK} Puerto $PORT ($SERVICE) está disponible${NC}"
    fi
}

check_port 3000 "Frontend"
check_port 8000 "Backend"
check_port 5432 "PostgreSQL"
check_port 6379 "Redis"
check_port 9000 "MinIO API"
check_port 9001 "MinIO Console"

echo ""

# ==============================================================================
# 4. VERIFICAR ESTADO DE SERVICIOS
# ==============================================================================
echo -e "${BLUE}🐳 4. Verificando estado de servicios Docker...${NC}"
echo ""

# Verificar si los contenedores están corriendo
if docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
    echo -e "${GREEN}${CHECK} Servicios Docker están en ejecución${NC}"
    echo ""
    docker-compose -f docker-compose.dev.yml ps
    echo ""
    
    # ===========================================================================
    # 5. VERIFICAR SALUD DE SERVICIOS
    # ===========================================================================
    echo -e "${BLUE}🏥 5. Verificando salud de servicios...${NC}"
    echo ""
    
    # PostgreSQL
    if docker-compose -f docker-compose.dev.yml exec -T db pg_isready &> /dev/null; then
        echo -e "${GREEN}${CHECK} PostgreSQL está saludable${NC}"
    else
        echo -e "${RED}${CROSS} PostgreSQL NO responde${NC}"
        ((ERRORS++))
    fi
    
    # Redis
    if docker-compose -f docker-compose.dev.yml exec -T redis redis-cli ping &> /dev/null; then
        echo -e "${GREEN}${CHECK} Redis está saludable${NC}"
    else
        echo -e "${RED}${CROSS} Redis NO responde${NC}"
        ((ERRORS++))
    fi
    
    # Backend
    if curl -s http://localhost:8000/api/v1/utils/health-check/ &> /dev/null; then
        echo -e "${GREEN}${CHECK} Backend está saludable${NC}"
    else
        echo -e "${YELLOW}${WARNING} Backend NO responde (puede estar iniciando)${NC}"
        ((WARNINGS++))
    fi
    
    # Frontend
    if curl -s http://localhost:3000 &> /dev/null; then
        echo -e "${GREEN}${CHECK} Frontend está saludable${NC}"
    else
        echo -e "${YELLOW}${WARNING} Frontend NO responde (puede estar compilando)${NC}"
        ((WARNINGS++))
    fi
    
else
    echo -e "${YELLOW}${INFO} Servicios NO están en ejecución${NC}"
    echo -e "${INFO} Ejecuta: ${BLUE}docker-compose -f docker-compose.dev.yml up${NC}"
fi

echo ""

# ==============================================================================
# 6. VERIFICAR DATOS SEMBRADOS
# ==============================================================================
echo -e "${BLUE}🌱 6. Verificando datos de prueba...${NC}"
echo ""

if docker-compose -f docker-compose.dev.yml ps | grep -q "backend.*Up"; then
    # Verificar si existen usuarios de prueba
    USER_COUNT=$(docker-compose -f docker-compose.dev.yml exec -T db \
        psql -U app -d app -tAc "SELECT COUNT(*) FROM users;" 2>/dev/null || echo "0")
    
    if [ "$USER_COUNT" -gt "0" ]; then
        echo -e "${GREEN}${CHECK} Base de datos contiene $USER_COUNT usuarios${NC}"
        
        # Verificar usuario admin
        ADMIN_EXISTS=$(docker-compose -f docker-compose.dev.yml exec -T db \
            psql -U app -d app -tAc "SELECT COUNT(*) FROM users WHERE email='admin@example.com';" 2>/dev/null || echo "0")
        
        if [ "$ADMIN_EXISTS" -eq "1" ]; then
            echo -e "${GREEN}${CHECK} Usuario admin@example.com existe${NC}"
        else
            echo -e "${YELLOW}${WARNING} Usuario admin@example.com NO existe${NC}"
            echo -e "    Ejecuta: ${BLUE}docker-compose -f docker-compose.dev.yml exec backend python -m app.seed_data${NC}"
            ((WARNINGS++))
        fi
    else
        echo -e "${YELLOW}${WARNING} Base de datos está vacía${NC}"
        echo -e "    Ejecuta: ${BLUE}docker-compose -f docker-compose.dev.yml exec backend python -m app.seed_data${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}${INFO} Backend no está corriendo, no se puede verificar datos${NC}"
fi

echo ""

# ==============================================================================
# 7. VERIFICAR VOLÚMENES
# ==============================================================================
echo -e "${BLUE}💾 7. Verificando volúmenes Docker...${NC}"
echo ""

VOLUMES=$(docker volume ls -q | grep -E "(app-db-data|redis_data|minio_data)" | wc -l)
if [ "$VOLUMES" -gt "0" ]; then
    echo -e "${GREEN}${CHECK} Se encontraron $VOLUMES volúmenes de datos${NC}"
    docker volume ls | grep -E "(app-db-data|redis_data|minio_data)"
else
    echo -e "${YELLOW}${INFO} No se encontraron volúmenes (se crearán al iniciar)${NC}"
fi

echo ""

# ==============================================================================
# 8. VERIFICAR REDES
# ==============================================================================
echo -e "${BLUE}🌐 8. Verificando redes Docker...${NC}"
echo ""

if docker network ls | grep -q "shared-network"; then
    echo -e "${GREEN}${CHECK} Red 'shared-network' existe${NC}"
else
    echo -e "${YELLOW}${WARNING} Red 'shared-network' NO existe${NC}"
    echo -e "    Crea la red: ${BLUE}docker network create shared-network${NC}"
    ((WARNINGS++))
fi

echo ""

# ==============================================================================
# RESUMEN FINAL
# ==============================================================================
echo "======================================================================"
echo -e "${BLUE}📊 RESUMEN DE VALIDACIÓN${NC}"
echo "======================================================================"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}${CHECK} ¡TODO PERFECTO!${NC}"
    echo ""
    echo "✨ Tu entorno de desarrollo está completamente configurado"
    echo ""
    echo "📝 Siguiente pasos:"
    echo "   1. Si no están corriendo: docker-compose -f docker-compose.dev.yml up"
    echo "   2. Frontend: http://localhost:3000"
    echo "   3. Backend API: http://localhost:8000/docs"
    echo "   4. Login: admin@example.com / admin123"
    echo ""
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}${WARNING} Validación completada con $WARNINGS advertencias${NC}"
    echo ""
    echo "El entorno puede funcionar, pero revisa las advertencias arriba"
    echo ""
else
    echo -e "${RED}${CROSS} Validación falló con $ERRORS errores y $WARNINGS advertencias${NC}"
    echo ""
    echo "Por favor, corrige los errores antes de continuar"
    echo ""
    exit 1
fi

echo "======================================================================"
echo ""
