#!/bin/bash

# Script para verificar el estado de salud de todos los servicios
# Uso: ./check-health.sh [dev|prod]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Determinar el archivo de compose a usar
ENV="${1:-dev}"

if [ "$ENV" = "prod" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
elif [ "$ENV" = "dev" ]; then
    COMPOSE_FILE="docker-compose.dev.yml"
else
    echo -e "${RED}❌ Entorno no válido. Usa 'dev' o 'prod'${NC}"
    exit 1
fi

echo -e "${BLUE}🏥 Verificando estado de salud de servicios ($ENV)${NC}"
echo ""

# Verificar que Docker Compose está disponible
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado o no está en el PATH${NC}"
    exit 1
fi

# Verificar que el archivo compose existe
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}❌ Archivo $COMPOSE_FILE no encontrado${NC}"
    exit 1
fi

echo -e "${BLUE}📊 Estado de los contenedores:${NC}"
echo ""

# Obtener el estado de todos los servicios
docker compose -f "$COMPOSE_FILE" ps

echo ""
echo -e "${BLUE}🔍 Health checks detallados:${NC}"
echo ""

# Función para verificar el health de un servicio
check_service() {
    local service=$1
    local container_id=$(docker compose -f "$COMPOSE_FILE" ps -q "$service" 2>/dev/null)
    
    if [ -z "$container_id" ]; then
        echo -e "  ${YELLOW}⚠️  $service: No está corriendo${NC}"
        return
    fi
    
    local health=$(docker inspect --format='{{.State.Health.Status}}' "$container_id" 2>/dev/null || echo "no-healthcheck")
    
    case "$health" in
        "healthy")
            echo -e "  ${GREEN}✅ $service: Healthy${NC}"
            ;;
        "unhealthy")
            echo -e "  ${RED}❌ $service: Unhealthy${NC}"
            # Mostrar últimos logs del healthcheck
            echo -e "     ${YELLOW}Últimos logs:${NC}"
            docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' "$container_id" | tail -n 3 | sed 's/^/     /'
            ;;
        "starting")
            echo -e "  ${YELLOW}⏳ $service: Starting...${NC}"
            ;;
        "no-healthcheck")
            local status=$(docker inspect --format='{{.State.Status}}' "$container_id")
            if [ "$status" = "running" ]; then
                echo -e "  ${BLUE}ℹ️  $service: Running (sin healthcheck)${NC}"
            else
                echo -e "  ${RED}❌ $service: $status${NC}"
            fi
            ;;
        *)
            echo -e "  ${YELLOW}⚠️  $service: Estado desconocido ($health)${NC}"
            ;;
    esac
}

# Lista de servicios a verificar
if [ "$ENV" = "dev" ]; then
    SERVICES=(
        "db"
        "redis"
        "minio"
        "prestart"
        "backend"
        "celery_worker"
        "celery_beat"
        "frontend"
        "playwright"
    )
else
    SERVICES=(
        "db"
        "redis"
        "prestart"
        "cv_backend"
        "celery_worker"
        "frontend"
        "playwright"
    )
fi

# Verificar cada servicio
for service in "${SERVICES[@]}"; do
    check_service "$service"
done

echo ""
echo -e "${BLUE}📝 Resumen:${NC}"
echo ""

# Contar servicios por estado
HEALTHY=0
UNHEALTHY=0
STARTING=0
STOPPED=0

for service in "${SERVICES[@]}"; do
    container_id=$(docker compose -f "$COMPOSE_FILE" ps -q "$service" 2>/dev/null)
    
    if [ -z "$container_id" ]; then
        ((STOPPED++))
        continue
    fi
    
    health=$(docker inspect --format='{{.State.Health.Status}}' "$container_id" 2>/dev/null || echo "no-healthcheck")
    
    case "$health" in
        "healthy")
            ((HEALTHY++))
            ;;
        "unhealthy")
            ((UNHEALTHY++))
            ;;
        "starting")
            ((STARTING++))
            ;;
        "no-healthcheck")
            status=$(docker inspect --format='{{.State.Status}}' "$container_id")
            if [ "$status" = "running" ]; then
                ((HEALTHY++))
            else
                ((STOPPED++))
            fi
            ;;
    esac
done

echo -e "  ${GREEN}✅ Healthy: $HEALTHY${NC}"
echo -e "  ${YELLOW}⏳ Starting: $STARTING${NC}"
echo -e "  ${RED}❌ Unhealthy: $UNHEALTHY${NC}"
echo -e "  ${BLUE}⏸️  Stopped: $STOPPED${NC}"

echo ""

# Determinar el estado general
if [ $UNHEALTHY -gt 0 ]; then
    echo -e "${RED}❌ Sistema tiene servicios unhealthy${NC}"
    echo ""
    echo -e "${BLUE}💡 Comandos útiles:${NC}"
    echo -e "  Ver logs:     docker compose -f $COMPOSE_FILE logs <servicio>"
    echo -e "  Reiniciar:    docker compose -f $COMPOSE_FILE restart <servicio>"
    echo -e "  Reconstruir:  docker compose -f $COMPOSE_FILE up -d --build <servicio>"
    exit 1
elif [ $STARTING -gt 0 ]; then
    echo -e "${YELLOW}⏳ Sistema todavía está iniciando...${NC}"
    echo -e "   Espera unos segundos y vuelve a ejecutar este script"
    exit 0
elif [ $STOPPED -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Algunos servicios no están corriendo${NC}"
    echo ""
    echo -e "${BLUE}💡 Para iniciar todos los servicios:${NC}"
    echo -e "  docker compose -f $COMPOSE_FILE up -d"
    exit 0
else
    echo -e "${GREEN}✅ Todos los servicios están saludables!${NC}"
    exit 0
fi
