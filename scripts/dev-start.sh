#!/bin/bash

# Script de inicio rápido para entorno de desarrollo
# Automatiza todo el proceso de configuración inicial

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo "======================================================================"
echo -e "${CYAN}  🚀 INICIO RÁPIDO - Entorno de Desarrollo Feature Models${NC}"
echo "======================================================================"
echo ""

# ==============================================================================
# 1. Verificar Docker
# ==============================================================================
echo -e "${BLUE}1. Verificando Docker...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    echo "Por favor instala Docker Desktop desde: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon no está corriendo${NC}"
    echo "Por favor inicia Docker Desktop"
    exit 1
fi

echo -e "${GREEN}✅ Docker está listo${NC}"
echo ""

# ==============================================================================
# 2. Configurar archivo .env
# ==============================================================================
echo -e "${BLUE}2. Configurando archivo de entorno...${NC}"

if [ ! -f ".env" ]; then
    echo "Creando .env desde .env.example..."
    cp .env.example .env
    echo -e "${GREEN}✅ Archivo .env creado${NC}"
    echo -e "${YELLOW}ℹ️  Puedes editar .env para personalizar la configuración${NC}"
else
    echo -e "${YELLOW}ℹ️  Archivo .env ya existe (no se sobrescribe)${NC}"
fi

echo ""

# ==============================================================================
# 3. Crear red compartida
# ==============================================================================
echo -e "${BLUE}3. Creando red Docker compartida...${NC}"

if ! docker network ls | grep -q "shared-network"; then
    docker network create shared-network
    echo -e "${GREEN}✅ Red 'shared-network' creada${NC}"
else
    echo -e "${YELLOW}ℹ️  Red 'shared-network' ya existe${NC}"
fi

echo ""

# ==============================================================================
# 4. Detener contenedores previos (si existen)
# ==============================================================================
echo -e "${BLUE}4. Limpiando contenedores previos...${NC}"

if docker-compose -f docker-compose.dev.yml ps -q 2>/dev/null | grep -q .; then
    echo "Deteniendo contenedores existentes..."
    docker-compose -f docker-compose.dev.yml down
    echo -e "${GREEN}✅ Contenedores detenidos${NC}"
else
    echo -e "${YELLOW}ℹ️  No hay contenedores previos${NC}"
fi

echo ""

# ==============================================================================
# 5. Construir imágenes
# ==============================================================================
echo -e "${BLUE}5. Construyendo imágenes Docker...${NC}"
echo -e "${YELLOW}⏳ Esto puede tomar varios minutos la primera vez...${NC}"
echo ""

docker-compose -f docker-compose.dev.yml build

echo ""
echo -e "${GREEN}✅ Imágenes construidas${NC}"
echo ""

# ==============================================================================
# 6. Iniciar servicios
# ==============================================================================
echo -e "${BLUE}6. Iniciando servicios...${NC}"
echo ""

docker-compose -f docker-compose.dev.yml up -d

echo ""
echo -e "${GREEN}✅ Servicios iniciados en modo background${NC}"
echo ""

# ==============================================================================
# 7. Esperar a que los servicios estén listos
# ==============================================================================
echo -e "${BLUE}7. Esperando a que los servicios estén listos...${NC}"
echo ""

# Función para esperar un servicio
wait_for_service() {
    SERVICE=$1
    URL=$2
    MAX_ATTEMPTS=30
    ATTEMPT=0
    
    echo -n "Esperando $SERVICE"
    
    while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        if curl -s "$URL" > /dev/null 2>&1; then
            echo -e " ${GREEN}✅${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        ((ATTEMPT++))
    done
    
    echo -e " ${YELLOW}⚠️ (timeout, pero puede estar iniciando)${NC}"
    return 1
}

# Esperar backend
wait_for_service "Backend API" "http://localhost:8000/api/v1/utils/health-check/"

# Esperar frontend
wait_for_service "Frontend" "http://localhost:3000"

echo ""

# ==============================================================================
# 8. Verificar datos sembrados
# ==============================================================================
echo -e "${BLUE}8. Verificando datos de prueba...${NC}"

sleep 5  # Dar tiempo para que complete el seeding

USER_COUNT=$(docker-compose -f docker-compose.dev.yml exec -T db \
    psql -U postgres -d app -tAc "SELECT COUNT(*) FROM users;" 2>/dev/null || echo "0")

if [ "$USER_COUNT" -gt "0" ]; then
    echo -e "${GREEN}✅ Base de datos sembrada con $USER_COUNT usuarios de prueba${NC}"
else
    echo -e "${YELLOW}⚠️  Ejecutando seeding manual...${NC}"
    docker-compose -f docker-compose.dev.yml exec backend python -m app.seed_data
fi

echo ""

# ==============================================================================
# RESUMEN FINAL
# ==============================================================================
echo "======================================================================"
echo -e "${GREEN}  ✅ ¡ENTORNO DE DESARROLLO LISTO!${NC}"
echo "======================================================================"
echo ""
echo -e "${CYAN}📱 URLs de acceso:${NC}"
echo ""
echo -e "  ${BLUE}Frontend:${NC}          http://localhost:3000"
echo -e "  ${BLUE}Backend API:${NC}       http://localhost:8000"
echo -e "  ${BLUE}API Docs (Swagger):${NC} http://localhost:8000/docs"
echo -e "  ${BLUE}API Docs (ReDoc):${NC}  http://localhost:8000/redoc"
echo -e "  ${BLUE}MinIO Console:${NC}     http://localhost:9001"
echo ""
echo -e "${CYAN}👤 Credenciales de prueba:${NC}"
echo ""
echo -e "  ${GREEN}Admin:${NC}        admin@example.com / admin123"
echo -e "  ${GREEN}Designer:${NC}     designer@example.com / designer123"
echo -e "  ${GREEN}Editor:${NC}       editor@example.com / editor123"
echo -e "  ${GREEN}Configurator:${NC} configurator@example.com / config123"
echo -e "  ${GREEN}Viewer:${NC}       viewer@example.com / viewer123"
echo ""
echo -e "${CYAN}🛠️  Comandos útiles:${NC}"
echo ""
echo -e "  ${YELLOW}Ver logs:${NC}              docker-compose -f docker-compose.dev.yml logs -f"
echo -e "  ${YELLOW}Detener servicios:${NC}     docker-compose -f docker-compose.dev.yml stop"
echo -e "  ${YELLOW}Reiniciar servicios:${NC}   docker-compose -f docker-compose.dev.yml restart"
echo -e "  ${YELLOW}Resetear todo:${NC}         docker-compose -f docker-compose.dev.yml down -v"
echo -e "  ${YELLOW}Validar entorno:${NC}       ./scripts/validate_dev_environment.sh"
echo ""
echo -e "${CYAN}📚 Documentación:${NC}"
echo ""
echo -e "  Ver DEVELOPMENT_QUICKSTART.md para guía completa"
echo ""
echo "======================================================================"
echo -e "${GREEN}  🎉 ¡Happy Coding!${NC}"
echo "======================================================================"
echo ""

# Ofrecer ver logs
echo -e "${YELLOW}¿Quieres ver los logs en tiempo real? (y/n)${NC}"
read -t 10 -n 1 response || response="n"
echo ""

if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
    echo -e "${CYAN}Mostrando logs... (Ctrl+C para salir)${NC}"
    echo ""
    docker-compose -f docker-compose.dev.yml logs -f
else
    echo -e "${BLUE}Puedes ver los logs con:${NC} docker-compose -f docker-compose.dev.yml logs -f"
    echo ""
fi
